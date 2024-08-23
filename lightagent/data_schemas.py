from typing import List
from datetime import datetime

class Parameter():
    def __init__(self, name, description, type, required, example = None, default = None, value:dict = {}):
        self.name = name
        self.description = description
        self.type = type
        self.required = required
        self.example = example
        self.default = default
        self.value = value

    def __str__(self) -> str:
        return f"Parameter: {self.name}, {self.description}, {self.type}, {self.required}, {self.example}, {self.default}, {self.value}"

    @staticmethod
    def from_json(data):
        name = data.get("name", "")
        description = data.get("description", "")
        type = data.get("type", "")
        required = data.get("required", False)
        example = data.get("example", None)
        value = data.get("value", {})
        return Parameter(name, description, type, required, example=example, value=value)

class Function:
    def __init__(self, name,
                 description,
                 trigger_instruction,
                 parameters: List[Parameter] = []):
        self.name = name
        self.description = description
        self.trigger_instruction = trigger_instruction
        self.parameters = parameters

    def __str__(self) -> str:
        return f"Function: {self.name}, {self.description}, {self.trigger_instruction}, {self.parameters}"

    @staticmethod
    def from_json(data):
        name = data.get("name", "")
        description = data.get("description", "")
        trigger_instruction = data.get("trigger_instruction", "")
        parameters = data.get("parameters", [])
        return Function(name, description, trigger_instruction, [Parameter.from_json(p) for p in parameters])

class Plugin:
    def __init__(self, name,
                 description,
                 trigger_instruction,
                 response_instruction,
                 functions: List[Function],
                 examples: dict = None):
        self.name = name
        self.description = description
        self.trigger_instruction = trigger_instruction
        self.response_instruction = response_instruction
        self.functions = functions
        self.examples = examples

    def __str__(self) -> str:
        return f"Plugin: {self.name}, {self.description}, {self.trigger_instruction}, {self.response_instruction}, {self.functions}"

    @staticmethod
    def from_json(data):
        name = data.get("name", "")
        description = data.get("description", "")
        trigger_instruction = data.get("trigger_instruction", "")
        response_instruction = data.get("response_instruction", "")
        functions = data.get("functions", [])
        examples = data.get("examples", None)
        return Plugin(name, description, trigger_instruction, response_instruction, [Function.from_json(f) for f in functions], examples)
    
class UserProfile:
    def __init__(self, id, name, datetime:str = datetime.now().strftime("%Y-%m-%d %H:%M:%S"), location:str = None):
        self.id = id
        self.name = name
        self.datetime = datetime
        self.location = location
    
    def __str__(self) -> str:
        return f"UserProfile: {self.id}, {self.name}, {self.datetime}, {self.location}"

class InnerToolInvokationResult:
    def __init__(self, plugin_name:str, function_name:str, success:bool, data: str, prompt:str):
        self.plugin_name = plugin_name
        self.function_name = function_name
        self.data = data
        self.prompt = prompt
        self.success : bool = success

    def __str__(self) -> str:
        return f"InnerToolInvokationResult: {self.plugin_name}, {self.function_name}, {self.success}, {self.data}, {self.prompt}"
    
    def to_json(self) -> dict:
        return {
            "plugin_name": self.plugin_name,
            "function_name": self.function_name,
            "data": self.data,
            "prompt": self.prompt,
            "success": self.success
        }

class Message:
    def __init__(self, id: str, content: str, last_modified_datetime:datetime, conversation_id: str, enabled_plugins: List[str] = [], location:str = None, inner_tool_invokation_results: List[InnerToolInvokationResult]=[], response: str=None):
        self.id = id
        self.content = content
        self.last_modified_datetime = last_modified_datetime
        self.conversation_id = conversation_id
        self.enabled_plugins = enabled_plugins
        self.location = location
        self.inner_tool_invokation_results = inner_tool_invokation_results
        self.response = response

    def __str__(self) -> str:
        return f"Message: {self.id}, {self.content}, {self.last_modified_datetime}, {self.conversation_id}, {self.enabled_plugins}, {self.location}, {self.inner_tool_invokation_results}, {self.response}"

class Context:
    # conversation history, user profile, inner triggered results
    def __init__(self, conversation_id, conversation_history: List[Message]=[], user_profile: UserProfile=None, enabled_plugins:List[str]=[], inner_tool_invokation_results: List[InnerToolInvokationResult]=[]):
        self.conversation_id = conversation_id
        self.conversation_history: List[Message] = conversation_history
        self.user_profile: UserProfile = user_profile
        self.inner_tool_invokation_results: List[InnerToolInvokationResult] = inner_tool_invokation_results
        self.enabled_plugins = enabled_plugins

    def __str__(self) -> str:
        return f"Context: {self.conversation_id}, {[str(msg) for msg in self.conversation_history]}, {self.user_profile}, {self.inner_tool_invokation_results}, {self.enabled_plugins}"


class Conversation:
    def __init__(self, id, user_id, message_id_list: List[str]):
        self.id = id
        self.user_id = user_id
        self.message_id_list = message_id_list

    def __str__(self) -> str:
        return f"Conversation: {self.id}, {self.user_id}, {self.message_id_list}"