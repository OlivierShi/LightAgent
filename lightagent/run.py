from datetime import datetime
import os
import uuid
from prompt_generator import PromptGenerator
from conversation_manager import ConversationManager
from storage.sqlite import SQLiteStorage    
from models import Message
from llms import GPT35
from plugins import PluginRunner
from LightAgent import LightAgent
from helpers import Helpers

if os.path.exists("run-sqlite.db"):
    os.remove("run-sqlite.db")
db = SQLiteStorage("run-sqlite.db")
cm = ConversationManager(db)
agent = LightAgent(PromptGenerator(), GPT35("gpt3.5"), cm, PluginRunner())


query = ""
conv_id = str(uuid.uuid4())

while True:

    msg_id = str(uuid.uuid4())
    query = input("Enter a query: ")
    print(f"User: {query}")
    if query == "new":
        conv_id = str(uuid.uuid4())
        continue
    
    if query == "exit":
        break

    message = Message(msg_id, query, datetime.now(), conv_id,  ["web_search",])
    
    response, metrics = agent.chat(message)
    Helpers.metrics_printer(metrics)
    print(f"LightAgent: {response}")
    print("\n")