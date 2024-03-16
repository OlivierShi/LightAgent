from typing import List
from datetime import datetime

class Parameter():
    def __init__(self, name, description, type, required, default = None, value:dict = {}):
        self.name = name
        self.description = description
        self.type = type
        self.required = required
        self.default = default
        self.value = value

    def __str__(self) -> str:
        return f"Parameter: {self.name}, {self.description}, {self.type}, {self.required}, {self.default}, {self.value}"

    @staticmethod
    def from_json(data):
        name = data.get("name", "")
        description = data.get("description", "")
        type = data.get("type", "")
        required = data.get("required", False)
        value = data.get("value", {})
        return Parameter(name, description, type, required, value)

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
                 functions: List[Function],):
        self.name = name
        self.description = description
        self.trigger_instruction = trigger_instruction
        self.functions = functions

    @staticmethod
    def from_json(data):
        name = data.get("name", "")
        description = data.get("description", "")
        trigger_instruction = data.get("trigger_instruction", "")
        functions = data.get("functions", [])
        return Plugin(name, description, trigger_instruction, [Function.from_json(f) for f in functions])
    
class Message:
    def __init__(self, content: str, role: str, last_modified_datetime:datetime, conversation_id: str, enabled_plugins: List[str] = []):
        self.content = content
        self.role = role
        self.last_modified_datetime = last_modified_datetime
        self.conversation_id = conversation_id
        self.enabled_plugins = enabled_plugins

class UserProfile:
    def __init__(self, name, datetime:str = datetime.now().strftime("%Y-%m-%d %H:%M:%S"), location:str = None):
        self.name = name
        self.datetime = datetime
        self.location = location

class InnerToolInvokationResult:
    def __init__(self, plugin_name:str, function_name:str, success:bool, data: str, prompt:str):
        self.plugin_name = plugin_name
        self.function_name = function_name
        self.data = data
        self.prompt = prompt
        self.success : bool = success

class Context:
    # conversation history, user profile, inner triggered results
    def __init__(self, conversation_id, conversation_history: List[Message]=[], user_profile: UserProfile=None, inner_tool_invokation_results: List[InnerToolInvokationResult]=[]):
        self.conversation_id = conversation_id
        self.conversation_history: List[Message] = conversation_history
        self.user_profile: UserProfile = user_profile
        self.inner_tool_invokation_results: List[InnerToolInvokationResult] = inner_tool_invokation_results


