from storage.sqlite import SQLiteStorage
from models import *
from typing import List
import json

class ConversationManager:
    def __init__(self, storage: SQLiteStorage):
        if storage is None:
            self.storage = SQLiteStorage("lightagent.db")
        else:
            self.storage = storage
        storage.create_table("users", "id TEXT PRIMARY KEY, name TEXT, conversation_id_list TEXT")
        storage.create_table("conversations", "id TEXT PRIMARY KEY, user_id TEXT, message_id_list TEXT")
        storage.create_table("messages", "id TEXT PRIMARY KEY, content TEXT, last_modified_datetime TEXT, location TEXT, conversation_id TEXT, enabled_plugins TEXT, inner_tool_invokation_results TEXT, response TEXT")
    
    def __serialize_inner_tool_invokation_results(self, inner_tool_invokation_results: List[InnerToolInvokationResult] = []):
        obj = [result.to_json() for result in inner_tool_invokation_results]
        return self.__serialize_json(obj)
    
    def __deserialize_inner_tool_invokation_results(self, str: str):
        return [InnerToolInvokationResult(**result) for result in self.__deserialize_json(str)]
    
    def __convert_message(self, message_data: tuple):
        return Message(
            id=message_data[0],
            content=message_data[1],
            last_modified_datetime=datetime.strptime(message_data[2], "%Y-%m-%d %H:%M:%S"),
            location=message_data[3],
            conversation_id=message_data[4],
            enabled_plugins=self.__deserialize_json(message_data[5]),
            inner_tool_invokation_results=self.__deserialize_inner_tool_invokation_results(message_data[6]),
            response=message_data[7]
        )

    def __serialize_json(self, obj: dict):
        return json.dumps(obj)
    
    def __deserialize_json(self, str: str):
        return json.loads(str)
    
    def get_message_context(self, message: Message):
        conversation_data = self.storage.get("conversations", f"id = '{message.conversation_id}'")
        if not conversation_data or len(conversation_data) != 3:
            conversation = Conversation(message.conversation_id, "anonymous", [])
            user = None
        else:
            conversation = Conversation(
                id=message.conversation_id,
                user_id=conversation_data[1],
                message_id_list=self.__deserialize_json(conversation_data[2]))
            if conversation.user_id == "anonymous":
                user = None
            else:
                user_data = self.storage.get("users", f"id = '{conversation.user_id}'")
                user = UserProfile(
                    id=user_data[0],
                    name=user_data[1],
                    datetime=message.last_modified_datetime,
                    location=message.location
                )

        return Context(
            conversation_id=message.conversation_id,
            conversation_history=[self.__convert_message(self.storage.get("messages", f"id = '{message_id}'")) for message_id in conversation.message_id_list],
            user_profile=user,
            inner_tool_invokation_results=[]
        )


    def save_message(self, message: Message, context: Context, response: str = None):
        self.storage.upsert("messages", {
            "id": message.id,
            "content": message.content,
            "last_modified_datetime": message.last_modified_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "location": message.location,
            "conversation_id": message.conversation_id,
            "enabled_plugins": self.__serialize_json(message.enabled_plugins),
            "inner_tool_invokation_results": self.__serialize_inner_tool_invokation_results(context.inner_tool_invokation_results),
            "response": response
        })

        message_id_list = [msg.id for msg in context.conversation_history]
        self.storage.upsert("conversations", {
            "id": message.conversation_id,
            "user_id": context.user_profile.id if context.user_profile else "anonymous",
            "message_id_list": self.__serialize_json(message_id_list)
        
        })

        if context.user_profile:
            user_data = self.storage.get("users", f"id = '{context.user_profile.id}'")
            conversation_id_list = self.__deserialize_json(user_data[2]) if user_data and len(user_data) == 3 else []
            conversation_id_list.append(message.conversation_id)
            self.storage.upsert("users", {"id": context.user_profile.id, "name": context.user_profile.name, "conversation_id_list": self.__serialize_json(conversation_id_list)})

    def close_storage(self):
        self.storage.close()