import json
from typing import List, Tuple
import time
from datetime import datetime
from prompt_generator import PromptGenerator
from models import Plugin, Message, Function, Parameter, Context, UserProfile, InnerToolInvokationResult
from llms import BaseLLM
from plugins import PluginRunner
from conversation_manager import ConversationManager
from config import BaseConfig
from utils.log_helpers import LogHelpers
from utils.llm_postprocessor import LLMPostprocessor

ASK_FOR_USER_INPUT = "ASK_FOR_USER_INPUT"

class LightAgent:
    """
    Since the mini-LLM is a light-weight version of the LLM, the agent to drive LLM need to be specific for light-weight. It means the task to handle the query need to be decomposed into minimized tasks. 
    """
    def __init__(self, prompt_generator: PromptGenerator, llm: BaseLLM, conv_mnger: ConversationManager, plugin_runner: PluginRunner = None):
        self.max_tool_invokation_times = 1
        self.prompt_generator = prompt_generator
        self.llm = llm
        self.conv_mnger = conv_mnger
        self.default_plugins_names = ["generate_response", "withdraw"]
        self.parsed_plugins = {}
        self.default_plugins = self.register_plugins(self.default_plugins_names) # default plugins
        self.enabled_plugins = [] # enabled plugins by the query

        self.plugin_runner = PluginRunner() if plugin_runner is None else plugin_runner

    def parse_plugin(self, plugin_name: str) -> Plugin:
        # parse the plugin name to get the plugin object
        plugin_json = json.load(open(f"{BaseConfig.BASE_DIR}/plugins/spec/{plugin_name}.json", "r"))
        parsed = Plugin.from_json(plugin_json)
        self.parsed_plugins[plugin_name] = parsed
        return parsed

    def register_plugins(self, plugin_names: list):
        # todo: load the plugins based on plugin name.
        return [self.parse_plugin(plugin_name) for plugin_name in set(plugin_names)]
    
    def detach_plugins(self, plugins: List[Plugin], detached_plugins: List[Plugin]) -> List[Plugin]:
        left_plugins = []
        detached_plugins_names = [plugin.name for plugin in detached_plugins]
        for plugin in plugins:
            if plugin.name not in detached_plugins_names:
                left_plugins.append(plugin)
        return left_plugins

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

        plugins_to_detect = self.detach_plugins(self.enabled_plugins + self.default_plugins, detached_plugins)
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
        
        prompt_detect_plugins = self.prompt_generator.format_prompt_tools_detection(plugins_description, plugins_trigger, prompt_conversation_history, prompt_inner_tool_invokation_results, query, examples)

        start_time = time.time()
        response = self.llm.generate(prompt_detect_plugins, reasoning=True)
        end_time = time.time()
        
        LogHelpers.metrics_helper(metrics, "perf", "detect_plugin", end_time - start_time)

        processed_result = LLMPostprocessor.try_parse_json_from_llm(response)
        processed_plugin_name = processed_result.get("tool", None)

        for plugin in self.enabled_plugins + self.default_plugins:
            if processed_plugin_name == plugin.name:
                LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== prompt to detect plugin\n{prompt_detect_plugins}\n== response from LLM\n{response}\n== detected plugin: {plugin.name}\n", end_time - start_time)
                LogHelpers.metrics_log_helper(metrics, "log", f"detect_plugin::{plugin.name}", end_time - start_time)
                return plugin
        return None

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

        prompt_detect_functions = self.prompt_generator.format_prompt_function_detection(description, trigger_instruction, message.content, examples)

        start_time = time.time()
        response = self.llm.generate(prompt_detect_functions, reasoning=True)
        end_time = time.time()
        LogHelpers.metrics_helper(metrics, "perf", "detect_function", end_time - start_time)

        processed_result = LLMPostprocessor.try_parse_json_from_llm(response)
        processed_function_name = processed_result.get("tool", None)
        for func in functions:
            if processed_function_name == func.name:
                LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== prompt to detect function\n{prompt_detect_functions}\n== response from LLM\n{response}\n== detected function: {func.name}\n", end_time - start_time)
                LogHelpers.metrics_log_helper(metrics, "log", f"detect_function::{func.name}", end_time - start_time)
                return func
        return None
    
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

        prompt_extract_params = self.prompt_generator.format_prompt_function_parameters_extraction(function.name, function.description, parameters_prompts, parameters_format, message.content, examples)
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

    def check_params_to_function(self, parameters: List[Parameter]) -> Tuple[dict, dict]:
        # given function and params, check if the params are valid
        if not parameters or len(parameters) == 0:
            return {}, {}
        
        parameters_to_execute = {}
        missing_required_parameters_to_execute = {} 
        for param in parameters:
            if param.value:
                parameters_to_execute[param.name] = param.value[param.name]
            else:
                if param.required:
                    missing_required_parameters_to_execute[param.name] = ASK_FOR_USER_INPUT
                elif param.default:
                    parameters_to_execute[param.name] = param.default
        return parameters_to_execute, missing_required_parameters_to_execute

    def include_plugins_for_response_instruction(self, inner_tool_invokation_results: List[InnerToolInvokationResult]) -> List[Plugin]:
        plugins = []
        plugins_names = []
        for _p in self.enabled_plugins:
            plugins.append(_p)
            plugins_names.append(_p.name)

        for tool_invocation in inner_tool_invokation_results:
            if tool_invocation.plugin_name not in plugins_names:
                plugins.append(self.parsed_plugins[tool_invocation.plugin_name])
        return plugins

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
        
        included_plugins = self.include_plugins_for_response_instruction(inner_tool_invokation_results)
        prompt_responding_instruction = self.prompt_generator.format_prompt_responding_instruction(included_plugins)

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

    def execute_ask_for_user_input(self, plugin: Plugin, function: Function, parameters: dict):
        # handle missing required parameters and prompt to ask for user inputs. 
        prompt_to_ask_for_user_input = ""
        for param in function.parameters:
            if param.name in parameters:
                prompt_to_ask_for_user_input += f"The {param.name} is missing when processing your query.\n"
        return prompt_to_ask_for_user_input

    def execute_function(self, plugin: Plugin, function: Function, parameters: dict, metrics={}):
        # given function and params, execute the function
        start_time = time.time()
        results = self.plugin_runner.run(plugin.name, function.name, parameters)
        end_time = time.time()
        LogHelpers.metrics_helper(metrics, "perf", "execute_function", end_time - start_time)
        LogHelpers.metrics_log_helper(metrics, "log", f"execute_function::{results[:50]}...", end_time - start_time)
        LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== {plugin.name}::{function.name} execution\n{results[:150]}...", end_time - start_time)
        return results

    def update_context(self, context: Context = None, message: Message = None, user_profile: UserProfile=None, inner_tool_invokation_results: List[InnerToolInvokationResult] = [], options: dict = {}):
        # given trigger_results and context, update the context

        if message:
            context.conversation_history.append(message)
        if user_profile:
            context.user_profile = user_profile
        if inner_tool_invokation_results:
            context.inner_tool_invokation_results = inner_tool_invokation_results
        if options:
            self.apply_options(context, options)

    def apply_options(self, context: Context, options: dict):
        # apply options to the agent
        if "user_name" in options:
            context.user_profile.name = options["user_name"]
        if "user_location" in options:
            context.user_profile.location = options["user_location"]
        if "enabled_plugins" in options:
            context.enabled_plugins = options["enabled_plugins"]

    def handle_plugin_results(self, context: Context, plugin_name: str, function_name: str, success: bool, data: str, prompt: str=None):
        cur_tool_invokation_result = InnerToolInvokationResult(plugin_name, function_name, success=success, data=data, prompt=None)
        self.update_context(context=context, inner_tool_invokation_results=context.inner_tool_invokation_results + [cur_tool_invokation_result])

    def check_detected_plugin_results(self, context: Context, plugin: Plugin) -> bool:
        if not plugin or plugin.name == "":
            self.handle_plugin_results(context, "", "", False, "No plugin detected.", None)
            return False
        
        if plugin.name == "withdraw":
            self.handle_plugin_results(context, plugin.name, "", True, "I need withdraw the query.", None)
            return False
        
        if plugin.name == "generate_response":
            self.handle_plugin_results(context, plugin.name, "", True, "I need to generate the response to the user query.", None)
            return False
        
        return True

    def check_detected_function_results(self, context: Context, plugin: Plugin, function: Function) -> bool:
        if not function or function.name not in [f.name for f in plugin.functions]:
            self.handle_plugin_results(context, plugin.name, "", False, f"The plugin {plugin.name} was failed.", None)
            return False
        return True
    
    def chat(self, message: Message, options: dict = {}):
        # message -> content, conversation_id, enabled_plugins
        # context -> conversation history, user profile, inner triggered results
        # context is agg data from `users` and `messages` tables, will not be persisted in the database.
        metrics = {}

        context = self.conv_mnger.get_message_context(message)
        self.update_context(context=context, message=message, options=options)

        LogHelpers.metrics_log_helper(metrics, "details", f"\n\n== context\n{context}\n", None)
        
        self.enabled_plugins = self.register_plugins(message.enabled_plugins + context.enabled_plugins)
        
        # tools trigger and invokation step
        _tool_invokation_num = 0
        detached_plugins = []
        while _tool_invokation_num < self.max_tool_invokation_times:

            plugin = self.detect_plugin(message, context, detached_plugins, metrics)

            _tool_invokation_num += 1

            if not self.check_detected_plugin_results(context, plugin):
                break
            
            function = self.detect_function(plugin, message, context, metrics)
        
            if not self.check_detected_function_results(context, plugin, function):
                break

            params = self.extract_params_to_function(plugin, function, message, context, metrics)

            parameters_to_execute, missing_required_parameters_to_execute = self.check_params_to_function(params)
            result = ""
            success = False
            if missing_required_parameters_to_execute or len(missing_required_parameters_to_execute) > 0:
                result = self.execute_ask_for_user_input(plugin, function, missing_required_parameters_to_execute)
                success = False
            else:
                try:
                    result = self.execute_function(plugin, function, parameters_to_execute, metrics)
                    success = True
                except:
                    result = f"{plugin.description}, the execution of the function was unsuccessful."
                    success = False
            
            self.handle_plugin_results(context, plugin.name, function.name, success, result, None)
            if success:
                # detach the successfully triggered plugin
                detached_plugins.append(plugin)

        # response step
        response = self.respond(message, context, metrics)

        self.conv_mnger.save_message(message, context, response)
        return response, metrics

