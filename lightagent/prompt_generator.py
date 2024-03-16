from typing import List
from models import UserProfile, Message, InnerToolInvokationResult
from config import BaseConfig
import os

class PromptGenerator:
    def __init__(self,):
        self.prompt_tools_detection = open(f"{BaseConfig.BASE_DIR}/prompts/prompt_tools_detection.md", "r").read()
        self.prompt_tools_detection_description = open(f"{BaseConfig.BASE_DIR}/prompts/prompt_tools_detection_description.md", "r").read()
        self.prompt_tools_detection_trigger = open(f"{BaseConfig.BASE_DIR}/prompts/prompt_tools_detection_trigger.md", "r").read()
        self.prompt_function_detection = open(f"{BaseConfig.BASE_DIR}/prompts/prompt_function_detection.md", "r").read()
        self.prompt_function_parameters_extraction_parameter = open(f"{BaseConfig.BASE_DIR}/prompts/prompt_function_parameters_extraction_parameter_format.md", "r").read()
        self.prompt_function_parameters_extraction = open(f"{BaseConfig.BASE_DIR}/prompts/prompt_function_parameters_extraction.md", "r").read()
        self.prompt_responding = open(f"{BaseConfig.BASE_DIR}/prompts/prompt_responding.md", "r").read()
        self.prompt_responding_failure = open(f"{BaseConfig.BASE_DIR}/prompts/prompt_responding_failure.md", "r").read()

    def format_prompt_tools_detection_description(self, name: str, description: str):
        return self.prompt_tools_detection_description.format(name=name, description=description)
    
    def format_prompt_tools_detection_trigger(self, name: str, trigger_instruction: str):
        return self.prompt_tools_detection_trigger.format(name=name, trigger_instruction=trigger_instruction)
    
    def format_prompt_tools_detection(self, description: str, trigger_instruction: str, conversation_history:str, inner_tool_invokation_results:str, query: str, examples: str = None):
        
        if self._is_none_or_whitespace(examples):
            examples = ""
        if self._is_none_or_whitespace(conversation_history):
            conversation_history = ""
        if self._is_none_or_whitespace(inner_tool_invokation_results):
            inner_tool_invokation_results = ""
        
        return self.prompt_tools_detection.format(description=description, trigger_instruction=trigger_instruction, examples=examples, conversation_history=conversation_history, inner_tool_invokation_results=inner_tool_invokation_results, query=query)
    
    def format_prompt_function_detection(self, description: str, trigger_instruction: str, query: str, examples: str = None):
        if self._is_none_or_whitespace(examples):
            examples = ""
            return self.prompt_function_detection.format(description=description, trigger_instruction=trigger_instruction, examples=examples, query=query)
        
    def format_prompt_function_parameters_extraction_parameter(self, name: str, type: str, description: str):
        return self.prompt_function_parameters_extraction_parameter.format(name=name, type=type, description=description)
    
    def format_prompt_function_parameters_extraction(self, function_name: str, description: str, parameters: str, query: str, examples: str = None):
        if self._is_none_or_whitespace(examples):
            examples = ""
        return self.prompt_function_parameters_extraction  \
                .replace("{function_name}", function_name) \
                .replace("{description}", description)     \
                .replace("{parameters}", parameters)       \
                .replace("{examples}", examples)           \
                .replace("{query}", query)
       
    def format_prompt_responding_user_profile(self, user_profile: UserProfile = None):
        if user_profile is None:
            return None
        
        prompt_user_profile = ""
        if user_profile.name is not None:
            prompt_user_profile += f"- User name is: {user_profile.name}.\n"
        if user_profile.datetime is not None:
            prompt_user_profile += f"- Current time is: {user_profile.datetime}.\n"
        if user_profile.location is not None:
            prompt_user_profile += f"- Location is: {user_profile.location}.\n"
        return prompt_user_profile

    def format_conversation_history(self, conversation_history: List[Message] = []):
        if not conversation_history or len(conversation_history) == 0:
            return None
        
        prompt_conversation_history = ""
        ordered_messages = sorted(conversation_history, key=lambda x: x.last_modified_datetime)
        for msg in ordered_messages:
            prompt_conversation_history += f"- {msg.role}: {msg.content}\n"
        return prompt_conversation_history

    def format_inner_tool_invokation_results(self, inner_tool_invokation_results: List[InnerToolInvokationResult] = []):
        if not inner_tool_invokation_results or len(inner_tool_invokation_results) == 0:
            return None
        
        prompt_inner_tool_invokation_results = ""
        for result in inner_tool_invokation_results:
            prompt_inner_tool_invokation_results += f"- {result.plugin_name}::{result.function_name}: {result.data}\n"
            if result.prompt is not None:
                prompt_inner_tool_invokation_results += f"    * Prompt: {result.prompt}\n"
        return prompt_inner_tool_invokation_results

    def format_prompt_responding(self,
                                 user_profile:str, 
                                 conversation_history:str, 
                                 inner_tool_invokation_results:str, 
                                 query:str,
                                 success:bool):
        if self._is_none_or_whitespace(user_profile):
            user_profile = ""
        if self._is_none_or_whitespace(conversation_history):
            conversation_history = ""
        if self._is_none_or_whitespace(inner_tool_invokation_results):
            inner_tool_invokation_results = ""
        
        responding_template = self.prompt_responding if success else self.prompt_responding_failure
        return responding_template.format(
            user_profile=user_profile,
            conversation_history=conversation_history,
            inner_tool_invokation_results=inner_tool_invokation_results,
            query=query)

    def _is_none_or_whitespace(self, s: str):
        return s is None or s.isspace() or s == ""