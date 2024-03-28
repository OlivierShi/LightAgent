import json
from typing import List, Tuple
from datetime import datetime
from prompt_generator import PromptGenerator
from models import Plugin, Message, Function, Parameter, Context, UserProfile, InnerToolInvokationResult
from llms import BaseLLM
from plugins import PluginRunner
from postprocessor import Postprocessor
from conversation_manager import ConversationManager
from config import BaseConfig

ASK_FOR_USER_INPUT = "ASK_FOR_USER_INPUT"

class LightAgent:
    """
    Since the mini-LLM is a light-weight version of the LLM, the agent to drive LLM need to be specific for light-weight. It means the task to handle the query need to be decomposed into minimized tasks. 
    """
    def __init__(self, prompt_generator: PromptGenerator, llm: BaseLLM, conv_mnger: ConversationManager, plugin_runner: PluginRunner = None):
        self.max_tool_invokation_times = 2
        self.prompt_generator = prompt_generator
        self.llm = llm
        self.conv_mnger = conv_mnger
        self.default_plugins_names = ["generate_response", "withdraw"]
        self.default_plugins = self.register_plugins(self.default_plugins_names) # default plugins
        self.enabled_plugins = [] # enabled plugins by the query

        self.plugin_runner = PluginRunner() if plugin_runner is None else plugin_runner

    def parse_plugin(self, plugin_name: str) -> Plugin:
        # parse the plugin name to get the plugin object
        plugin_json = json.load(open(f"{BaseConfig.BASE_DIR}/plugins/spec/{plugin_name}.json", "r"))
        return Plugin.from_json(plugin_json)

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

    def detect_plugin(self, message: Message, context: Context, detached_plugins: List[Plugin] = []) -> Plugin:
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

        plugins_to_detect = self.detach_plugins(self.enabled_plugins + self.default_plugins, detached_plugins)
        for plugin in plugins_to_detect:
            plugins_description += self.prompt_generator.format_prompt_tools_detection_description(plugin.name, plugin.description)
            plugins_description += "\n"

            plugins_trigger += self.prompt_generator.format_prompt_tools_detection_trigger(plugin.name, plugin.trigger_instruction)
            plugins_trigger += "\n"
        plugins_description = plugins_description.strip("\n")
        plugins_trigger = plugins_trigger.strip("\n")

        query = message.content
        conversation_history = context.conversation_history
        inner_tool_invokation_results = context.inner_tool_invokation_results
        prompt_conversation_history = self.prompt_generator.format_conversation_history(conversation_history)
        prompt_inner_tool_invokation_results = self.prompt_generator.format_inner_tool_invokation_results(inner_tool_invokation_results)
        
        prompt_detect_plugins = self.prompt_generator.format_prompt_tools_detection(plugins_description, plugins_trigger, prompt_conversation_history, prompt_inner_tool_invokation_results, query)

        self.log.write("\n\n== prompt to detect plugin\n")
        self.log.write(prompt_detect_plugins)
        self.log.write("\n\n== prompt to detect plugin\n")
        self.log.write(prompt_detect_plugins)
        response = self.llm.generate(prompt_detect_plugins, reasoning=True)
        self.log.write(f"\n\n== response from LLM\n")
        self.log.write(response)
        processed_plugin_name = Postprocessor.postprocess_llm(response)
        for plugin in self.enabled_plugins + self.default_plugins:
            if processed_plugin_name == plugin.name:
                self.log.write(f"== detected plugin: {plugin.name}\n")
                return plugin
        return None

    def detect_function(self, plugin: Plugin, message: Message, context: Context) -> Function:
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
        for func in functions:
            description += self.prompt_generator.format_prompt_tools_detection_description(func.name, func.description)
            description += "\n"
            trigger_instruction += self.prompt_generator.format_prompt_tools_detection_trigger(func.name, func.trigger_instruction)
            trigger_instruction += "\n"
        description = description.strip("\n")
        trigger_instruction = trigger_instruction.strip("\n")
        prompt_detect_functions = self.prompt_generator.format_prompt_function_detection(description, trigger_instruction, message.content)

        self.log.write("\n\n== prompt to detect functions\n")
        self.log.write(prompt_detect_functions)
        self.log.write("\n\n== prompt to detect functions\n")
        self.log.write(prompt_detect_functions)
        response = self.llm.generate(prompt_detect_functions, reasoning=True)
        self.log.write(f"\n\n== response from LLM\n")
        self.log.write(response)
        processed_function_name = Postprocessor.postprocess_llm(response)
        for func in functions:
            if processed_function_name == func.name:
                self.log.write(f"== detected function: {func.name}\n")
                return func
        return None
    
    def extract_params_to_function(self, function: Function, message: Message, context: Context) -> List[Parameter]:
        # given query and context, determine which parameters are relevant
        parameters = function.parameters
        if not parameters or len(parameters) == 0:
            return None

        parameters_prompts = ""
        for param in parameters:
            parameters_prompts += self.prompt_generator.format_prompt_function_parameters_extraction_parameter(param.name, param.type, param.description)
            parameters_prompts += "\n"
        
        prompt_extract_params = self.prompt_generator.format_prompt_function_parameters_extraction(function.name, function.description, parameters_prompts, message.content)
        self.log.write(f"\n\n== prompt to extract parameters to the function {function.name}\n")
        self.log.write(prompt_extract_params)
        self.log.write(f"\n\n== prompt to extract parameters to the function {function.name}\n")
        self.log.write(prompt_extract_params)
        response = self.llm.generate(prompt_extract_params, reasoning=True)
        self.log.write(f"\n\n== response from LLM\n")
        self.log.write(response)        
        processed_params = json.loads(Postprocessor.postprocess_llm(response))
        
        for k, v in processed_params.items():
            for param in parameters:
                if k == param.name and v is not None:
                    param.value = {k: v}
                    self.log.write(f"== extracted parameter: {k} -> {v}\n")
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

    def respond(self,
                message: Message,
                context: Context):
        # given query, conversation history, user profile, inner triggered results, return the response
        query = message.content
        conversation_history = context.conversation_history
        user_profile = context.user_profile
        inner_tool_invokation_results = context.inner_tool_invokation_results
        prompt_user_profile = self.prompt_generator.format_prompt_responding_user_profile(user_profile)
        prompt_conversation_history = self.prompt_generator.format_conversation_history(conversation_history)
        prompt_inner_tool_invokation_results = self.prompt_generator.format_inner_tool_invokation_results(inner_tool_invokation_results)
        
        success = all([res.success for res in inner_tool_invokation_results])
        prompt_responding = self.prompt_generator.format_prompt_responding(prompt_user_profile,
                                                                           prompt_conversation_history,
                                                                           prompt_inner_tool_invokation_results,
                                                                           query,
                                                                           success)
        self.log.write(f"\n\n== prompt to respond\n")
        self.log.write(prompt_responding)
        self.log.write(f"\n\n== prompt to respond\n")
        self.log.write(prompt_responding)
        response = self.llm.generate(prompt_responding, reasoning=False)
        self.log.write(f"\n\n== response from LLM\n")
        self.log.write(response)
        response = Postprocessor.postprocess_llm(response)
        # todo: parse the response
        return response

    def execute_ask_for_user_input(self, plugin: Plugin, function: Function, parameters: dict):
        # handle missing required parameters and prompt to ask for user inputs. 
        prompt_to_ask_for_user_input = ""
        for param in function.parameters:
            if param.name in parameters:
                prompt_to_ask_for_user_input += f"The {param.name} is missing when processing your query.\n"
        return prompt_to_ask_for_user_input

    def execute_function(self, plugin: Plugin, function: Function, parameters: dict):
        # given function and params, execute the function
        # todo: implement the function interface;
        return self.plugin_runner.run(plugin.name, function.name, parameters)

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

    def chat(self, message: Message, options: dict = {}):
        # message -> content, conversation_id, enabled_plugins
        # context -> conversation history, user profile, inner triggered results
        # context is agg data from `users` and `messages` tables, will not be persisted in the database.
        self.log = open(f"prompt_{message.id}.log", "w", encoding="utf-8")
        self.log.write(f"\n== chat with message\n")
        context = self.conv_mnger.get_message_context(message)
        self.update_context(context=context, message=message, options=options)
        self.log.write(f"\n== context\n")
        self.enabled_plugins = self.register_plugins(message.enabled_plugins + context.enabled_plugins)
        
        # tools trigger and invokation step
        _tool_invokation_num = 0
        detached_plugins = []
        while _tool_invokation_num < self.max_tool_invokation_times:

            plugin = self.detect_plugin(message, context, detached_plugins)

            _tool_invokation_num += 1

            if not plugin or plugin.name in self.default_plugins_names:
                break
            
            function = self.detect_function(plugin, message, context)
        
            if not function:
                break

            params = self.extract_params_to_function(function, message, context)
            parameters_to_execute, missing_required_parameters_to_execute = self.check_params_to_function(params)
            result = ""
            success = False
            if missing_required_parameters_to_execute or len(missing_required_parameters_to_execute) > 0:
                result = self.execute_ask_for_user_input(plugin, function, missing_required_parameters_to_execute)
                success = False
            else:
                try:
                    result = self.execute_function(plugin, function, parameters_to_execute)
                    success = True
                except:
                    result = f"{plugin.description}, the execution of the function was unsuccessful."
                    success = False
            
            cur_tool_invokation_result = InnerToolInvokationResult(plugin.name, function.name, success=success, data=result, prompt=None)
            self.update_context(context=context,
                                inner_tool_invokation_results=context.inner_tool_invokation_results + [cur_tool_invokation_result])
            self.log.write(f"== trigger results\n")
            self.log.write(cur_tool_invokation_result.data)
            if success:
                # detach the successfully triggered plugin
                detached_plugins.append(plugin)
            else:
                break

        # response step
        response = self.respond(message, context)

        self.conv_mnger.save_message(message, context, response)
        self.log.close()
        return response


    

# from llms import GPT35
# orch = LightAgent(PromptGenerator(), GPT35("gpt3.5"), PluginRunner())
# msg = Message("Retrieve a bottle message", role="user", last_modified_datetime=datetime.now(), conversation_id="123", enabled_plugins=["web_search", "message_in_a_bottle"])
# response = orch.chat(msg)
# print(response)
