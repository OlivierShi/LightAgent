from typing import List, Tuple
import os
import json
from data_schemas import Parameter, InnerToolInvokationResult, Plugin, Context, Function, UserProfile, Message
from prompts.prompt_generator import ASK_FOR_USER_INPUT
from config import BaseConfig

class AgentHelpers:
    
    @staticmethod
    def check_params_to_function(parameters: List[Parameter]) -> Tuple[dict, dict]:
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
    
    @staticmethod
    def load_all_plugins():
        # load all plugins from the plugin directory
        all_plugins = {}
        plugin_files = os.listdir(f"{BaseConfig.BASE_DIR}/plugins/spec")
        for plugin_file in plugin_files:
            plugin_json = json.load(open(f"{BaseConfig.BASE_DIR}/plugins/spec/{plugin_file}", "r"))
            plugin = Plugin.from_json(plugin_json)
            all_plugins[plugin.name] = plugin
        return all_plugins

    @staticmethod
    def aggregate_enabled_and_invoked_plugins(enabled_plugins: List[Plugin], inner_tool_invokation_results: List[InnerToolInvokationResult]) -> List[str]:
        plugins_names = []
        for _p in enabled_plugins:
            plugins_names.append(_p.name)

        for tool_invocation in inner_tool_invokation_results:
            if tool_invocation.plugin_name not in plugins_names:
                plugins_names.append(tool_invocation.plugin_name)
        return plugins_names
    
    @staticmethod
    def check_detected_plugin_results(plugin: Plugin, allowed_plugins: List[Plugin]) -> bool:

        is_valid_plugin = True
        should_skip_reasoning = False
        returnback_data = ""

        if not plugin or plugin.name not in [p.name for p in allowed_plugins]:
            is_valid_plugin = False
            plugin.name = ""
            returnback_data = "No plugin detected."
            should_skip_reasoning = True
        if plugin.name == "withdraw":
            returnback_data = "I need withdraw the query."
            should_skip_reasoning = True
        if plugin.name == "generate_response":
            returnback_data = "I need to generate the response to the user query."
            should_skip_reasoning = True
        
        return should_skip_reasoning, is_valid_plugin, returnback_data

    @staticmethod
    def check_detected_function_results(plugin: Plugin, function: Function) -> bool:
        is_valid_function = True
        should_skip_reasoning = False
        returnback_data = ""

        if not function or function.name not in [f.name for f in plugin.functions]:
            is_valid_function = False
            returnback_data = f"The plugin {plugin.name} was failed."
            should_skip_reasoning = True
        return should_skip_reasoning, is_valid_function, returnback_data
    
    @staticmethod
    def check_missing_parameters(plugin: Plugin, function: Function, parameters: dict):
        # handle missing required parameters and prompt to ask for user inputs. 
        prompt_to_ask_for_user_input = ""
        for param in function.parameters:
            if param.name in parameters:
                prompt_to_ask_for_user_input += f"The {param.name} is missing when processing your query.\n"
        return prompt_to_ask_for_user_input
    

    @staticmethod
    def apply_options_to_context(context: Context, options: dict):
        # apply options to the agent
        if "user_name" in options:
            context.user_profile.name = options["user_name"]
        if "user_location" in options:
            context.user_profile.location = options["user_location"]
        if "enabled_plugins" in options:
            context.enabled_plugins = list(set(options["enabled_plugins"] + context.enabled_plugins))

    @staticmethod
    def update_context(context: Context = None, message: Message = None, user_profile: UserProfile=None, inner_tool_invokation_results: List[InnerToolInvokationResult] = [], options: dict = {}):
        # given trigger_results and context, update the context
        if message:
            context.conversation_history.append(message)
            if message.enabled_plugins and len(message.enabled_plugins) > 0:
                context.enabled_plugins = list(set(message.enabled_plugins + context.enabled_plugins))
        if user_profile:
            context.user_profile = user_profile
        if inner_tool_invokation_results:
            context.inner_tool_invokation_results = inner_tool_invokation_results
        if options:
            AgentHelpers.apply_options_to_context(context, options)

    @staticmethod
    def update_context_by_plugin_results(context: Context, plugin: Plugin, function: Function, success: bool, data: str, prompt: str=None):
        plugin_name = plugin.name if plugin else ""
        function_name = function.name if function else ""
        plugins_results = context.inner_tool_invokation_results
        if function_name == "" or plugins_results[-1].plugin_name != plugin_name:
            plugins_results.append(InnerToolInvokationResult(plugin_name, function_name, success=success, data=data, prompt=None))
        else:
            plugins_results[-1].function_name = function_name
            plugins_results[-1].success = success
            plugins_results[-1].data = data

        AgentHelpers.update_context(context=context, inner_tool_invokation_results=plugins_results)
   
    @staticmethod
    def detach_plugins(plugins: List[Plugin], detached_plugins: List[Plugin]) -> List[Plugin]:
        left_plugins = []
        detached_plugins_names = [plugin.name for plugin in detached_plugins]
        for plugin in plugins:
            if plugin.name not in detached_plugins_names:
                left_plugins.append(plugin)
        return left_plugins
    