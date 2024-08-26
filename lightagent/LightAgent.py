from typing import List, Tuple
import time
from prompts.prompt_generator import PromptGenerator
from data_schemas import Plugin, Message, Function, Parameter, Context, UserProfile, InnerToolInvokationResult
from llms import BaseLLM
from plugins import PluginRunner
from storage.conversation_manager import ConversationManager
from storage.logger import Logger
from config import BaseConfig
from utils.log_helpers import LogHelpers
from utils.llm_postprocessor import LLMPostprocessor
from utils.agent_helpers import AgentHelpers
from prompts.prompt_generator import ASK_FOR_USER_INPUT

class LightAgent:
    """
    Since the mini-LLM is a light-weight version of the LLM, the agent to drive LLM need to be specific for light-weight. It means the task to handle the query need to be decomposed into minimized tasks. 
    """
    def __init__(self, prompt_generator: PromptGenerator, 
                 llm: BaseLLM, 
                 conv_mnger: ConversationManager, 
                 plugin_runner: PluginRunner,
                 logger: Logger):
        self.max_tool_invokation_times = 1
        self.prompt_generator = prompt_generator
        self.llm = llm
        self.conv_mnger = conv_mnger
        self.all_plugins = AgentHelpers.load_all_plugins()
        self.default_plugins_names = ["generate_response", "withdraw"]
        self.default_plugins = self.register_plugins(self.default_plugins_names) # default plugins
        self.enabled_plugins = [] # todo: enabled plugins by the query
        self.plugin_runner = plugin_runner
        self.logger = logger

    def chat(self, message: Message, options: dict = {}):
        # message -> content, conversation_id, enabled_plugins
        # context -> conversation history, user profile, inner triggered results
        # context is agg data from `users` and `messages` tables, will not be persisted in the database.
        metrics = {}

        context = self.conv_mnger.get_message_context(message)
        AgentHelpers.update_context(context=context, message=message, options=options)

        LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== context\n{context}\n", None)
        
        self.enabled_plugins = self.register_plugins(message.enabled_plugins + context.enabled_plugins)
        
        # tools trigger and invokation step
        _tool_invokation_num = 0
        detached_plugins = []
        while _tool_invokation_num < self.max_tool_invokation_times:
            _tool_invokation_num += 1

            plugin = self.detect_plugin(message, context, detached_plugins, metrics)
            should_skip_reasoning, is_valid_plugin, returnback_data = AgentHelpers.check_detected_plugin_results(plugin, self.enabled_plugins + self.default_plugins)

            AgentHelpers.update_context_by_plugin_results(context, plugin, None, is_valid_plugin, returnback_data, None)
            if should_skip_reasoning:
                break
            
            function = self.detect_function(plugin, message, context, metrics)
            should_skip_reasoning, is_valid_function, returnback_data = AgentHelpers.check_detected_function_results(plugin, function)
            AgentHelpers.update_context_by_plugin_results(context, plugin, function, is_valid_function, returnback_data, None)
            if should_skip_reasoning:
                break

            params = self.extract_params_to_function(plugin, function, message, context, metrics)
            result, success = self.execute_function(plugin, function, params, metrics)

            AgentHelpers.update_context_by_plugin_results(context, plugin, function, success, result, None)
            if success:
                # detach the successfully triggered plugin
                detached_plugins.append(plugin)

        # response step
        response = self.respond(message, context, metrics)

        self.conv_mnger.save_message(message, context, response)

        self.logger.log("\n".join(metrics["details"]), message.id)

        return response, metrics
    
    def register_plugins(self, plugin_names: list) -> List[Plugin]:
        return [self.all_plugins[plugin_name] for plugin_name in set(plugin_names)]

    def detect_plugin(self, message: Message, context: Context, detached_plugins: List[Plugin] = [], metrics={}) -> Plugin:
        """
        Given message, determine which plugin is relevant.
        Currently, each time can only detect one plugin.

        Args:
            message (Message): The input message.

        Returns:
            Plugin: return the detected plugin
        """

        plugins_description = ""
        plugins_trigger = ""
        examples = ""

        plugins_to_detect = AgentHelpers.detach_plugins(self.enabled_plugins + self.default_plugins, detached_plugins)
        for plugin in plugins_to_detect:
            plugins_description += self.prompt_generator.format_prompt_tools_detection_description(plugin.name, plugin.description)
            plugins_description += "\n"

            plugins_trigger += self.prompt_generator.format_prompt_tools_detection_trigger(plugin.name, plugin.trigger_instruction)
            plugins_trigger += "\n"

            if plugin.examples and "tool_detection" in plugin.examples:
                examples += plugin.examples["tool_detection"]
                examples += "\n"
        plugins_description = plugins_description.strip("\n")
        plugins_trigger = plugins_trigger.strip("\n")
        examples = examples.strip("\n")

        query = message.content
        conversation_history = context.conversation_history
        inner_tool_invokation_results = context.inner_tool_invokation_results
        prompt_conversation_history = self.prompt_generator.format_conversation_history(conversation_history)
        prompt_inner_tool_invokation_results = self.prompt_generator.format_inner_tool_invokation_results(inner_tool_invokation_results)
        
        prompt_detect_plugins = self.prompt_generator.format_prompt_tools_detection(
            plugins_description, 
            plugins_trigger, 
            prompt_conversation_history, 
            prompt_inner_tool_invokation_results, 
            query, 
            examples)

        start_time = time.time()
        response = self.llm.generate(prompt_detect_plugins, reasoning=True)
        end_time = time.time()
        
        LogHelpers.metrics_helper(metrics, "perf", "detect_plugin", end_time - start_time)

        processed_result = LLMPostprocessor.try_parse_json_from_llm(response)
        processed_plugin_name = processed_result.get("tool", None)

        detected_plugin = None

        for plugin in self.enabled_plugins + self.default_plugins:
            if processed_plugin_name == plugin.name:
                detected_plugin = plugin
                break

        LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== prompt to detect plugin\n{prompt_detect_plugins}\n== response from LLM\n{response}\n== detected plugin: {processed_plugin_name}\n", end_time - start_time)
        LogHelpers.metrics_log_helper(metrics, "log", f"detect_plugin::{processed_plugin_name}", end_time - start_time)
        return detected_plugin

    def detect_function(self, plugin: Plugin, message: Message, context: Context, metrics={}) -> Function:
        """
        Given the current plugin and the message, determine which functions of the plugin are relevant
        Currently, each time can only detect one function.

        Args:
            plugin (Plugin): The current plugin.
            message (Message): The input message.

        Returns:
            Plugin: return the detected function of this plugin.
        """
        functions = plugin.functions
        if len(functions) == 0:
            return None
        if len(functions) == 1:
            return functions[0]
        
        description = ""
        trigger_instruction = ""
        examples = ""

        for func in functions:
            description += self.prompt_generator.format_prompt_tools_detection_description(func.name, func.description)
            description += "\n"
            trigger_instruction += self.prompt_generator.format_prompt_tools_detection_trigger(func.name, func.trigger_instruction)
            trigger_instruction += "\n"

        if plugin.examples and "function_detection" in plugin.examples:
            examples += plugin.examples["function_detection"]
            examples += "\n"

        description = description.strip("\n")
        trigger_instruction = trigger_instruction.strip("\n")
        examples = examples.strip("\n")

        query = message.content
        conversation_history = context.conversation_history
        inner_tool_invokation_results = context.inner_tool_invokation_results
        prompt_conversation_history = self.prompt_generator.format_conversation_history(conversation_history)
        prompt_inner_tool_invokation_results = self.prompt_generator.format_inner_tool_invokation_results(inner_tool_invokation_results)

        prompt_detect_functions = self.prompt_generator.format_prompt_tools_detection(
            description, 
            trigger_instruction, 
            prompt_conversation_history,
            prompt_inner_tool_invokation_results,
            query, 
            examples)

        start_time = time.time()
        response = self.llm.generate(prompt_detect_functions, reasoning=True)
        end_time = time.time()
        LogHelpers.metrics_helper(metrics, "perf", "detect_function", end_time - start_time)

        processed_result = LLMPostprocessor.try_parse_json_from_llm(response)
        processed_function_name = processed_result.get("tool", None)
        detected_function = None
        for func in functions:
            if processed_function_name == func.name:
                detected_function = func
                break

        LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== prompt to detect function\n{prompt_detect_functions}\n== response from LLM\n{response}\n== detected function: {processed_function_name}\n", end_time - start_time)
        LogHelpers.metrics_log_helper(metrics, "log", f"detect_function::{processed_function_name}", end_time - start_time)
        return detected_function
    
    def extract_params_to_function(self, plugin: Plugin, function: Function, message: Message, context: Context, metrics:dict) -> List[Parameter]:
        # given query and context, determine which parameters are relevant
        parameters = function.parameters
        if not parameters or len(parameters) == 0:
            return None

        parameters_prompts = ""
        for param in parameters:
            parameters_prompts += self.prompt_generator.format_prompt_function_parameters_extraction_parameter(param.name, param.type, param.required, param.description)
            parameters_prompts += "\n"
        
        parameters_format = self.prompt_generator.format_prompt_function_parameters_extraction_format(function)

        examples = ""
        if plugin.examples and "parameters_extraction" in plugin.examples:
            examples = plugin.examples["parameters_extraction"]

        conversation_history = context.conversation_history
        inner_tool_invokation_results = context.inner_tool_invokation_results
        prompt_conversation_history = self.prompt_generator.format_conversation_history(conversation_history)
        prompt_inner_tool_invokation_results = self.prompt_generator.format_inner_tool_invokation_results(inner_tool_invokation_results)
        
        prompt_extract_params = self.prompt_generator.format_prompt_function_parameters_extraction(
            function.name, 
            function.description, 
            parameters_prompts, 
            parameters_format,
            prompt_conversation_history,
            prompt_inner_tool_invokation_results,
            message.content, 
            examples)
        
        start_time = time.time()
        response = self.llm.generate(prompt_extract_params, reasoning=True)
        end_time = time.time()
        LogHelpers.metrics_helper(metrics, "perf", "extract_params_to_function", end_time - start_time)
         
        processed_params = LLMPostprocessor.try_parse_json_from_llm(response)
        
        log_str_params = ""
        for k, v in processed_params.items():
            for param in parameters:
                if k == param.name and v is not None:
                    param.value = {k: v}
                    log_str_params += f"== extracted parameter: {k} -> {v}\n"
                    LogHelpers.metrics_log_helper(metrics, "log", f"extract_params_to_function::{k} -> {v}", end_time - start_time)

        LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== prompt to extract parameters to the function {function.name}\n{prompt_extract_params}\n== response from LLM\n{response}\n{log_str_params}\n", end_time - start_time)
        return parameters

    def respond(self,
                message: Message,
                context: Context,
                metrics={}):
        # given query, conversation history, user profile, inner triggered results, return the response
        query = message.content
        conversation_history = context.conversation_history
        user_profile = context.user_profile
        inner_tool_invokation_results = context.inner_tool_invokation_results
        prompt_user_profile = self.prompt_generator.format_prompt_responding_user_profile(user_profile)
        prompt_conversation_history = self.prompt_generator.format_conversation_history(conversation_history)
        prompt_inner_tool_invokation_results = self.prompt_generator.format_inner_tool_invokation_results(inner_tool_invokation_results)
        
        included_plugin_names = AgentHelpers.aggregate_enabled_and_invoked_plugins(self.enabled_plugins, inner_tool_invokation_results)
        prompt_responding_instruction = self.prompt_generator.format_prompt_responding_instruction([self.all_plugins[p_n] for p_n in included_plugin_names])

        success = all([res.success for res in inner_tool_invokation_results])
        prompt_responding = self.prompt_generator.format_prompt_responding(prompt_responding_instruction,
                                                                           prompt_user_profile,
                                                                           prompt_conversation_history,
                                                                           prompt_inner_tool_invokation_results,
                                                                           query,
                                                                           success)
        start_time = time.time()
        response = self.llm.generate(prompt_responding, reasoning=False)
        end_time = time.time()
        LogHelpers.metrics_helper(metrics, "perf", "respond", end_time - start_time)

        postprocessed_response = LLMPostprocessor.postprocess_llm(response)

        LogHelpers.metrics_log_helper(metrics, "log", f"respond::{postprocessed_response}", end_time - start_time)
        LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== prompt to respond\n{prompt_responding}\n== response from LLM\n{response}\n== processed response: {postprocessed_response}\n", end_time - start_time)

        return response

    def execute_function(self, plugin: Plugin, function: Function, parameters:List[Parameter], metrics: dict) -> Tuple[str, bool]:
        # given function and params, execute the function
        start_time = time.time()
        parameters_to_execute, missing_required_parameters_to_execute = AgentHelpers.check_params_to_function(parameters)
        result = ""
        success = False
        if missing_required_parameters_to_execute or len(missing_required_parameters_to_execute) > 0:
            result = AgentHelpers.check_missing_parameters(plugin, function, missing_required_parameters_to_execute)
            success = False
        else:
            try:
                result = self.plugin_runner.run(plugin.name, function.name, parameters_to_execute)
                success = True
            except:
                result = f"{plugin.description}, the execution of the function was unsuccessful."
                success = False

        end_time = time.time()
        LogHelpers.metrics_helper(metrics, "perf", "execute_function", end_time - start_time)
        LogHelpers.metrics_log_helper(metrics, "log", f"execute_function::{result[:50]}...", end_time - start_time)
        LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== {plugin.name}::{function.name} execution\n{result[:150]}...", end_time - start_time)

        return result, success


