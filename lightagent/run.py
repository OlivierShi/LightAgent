from datetime import datetime
import os
import uuid
from prompt_generator import PromptGenerator
from storage.conversation_manager import ConversationManager
from storage.logger import Logger
from storage.sqlite import SQLiteStorage    
from models import Message
from llms import GPT35, Phi3
from plugins import PluginRunner
from LightAgent import LightAgent
from utils.log_helpers import LogHelpers

if os.path.exists("run-sqlite.db"):
    os.remove("run-sqlite.db")
db = SQLiteStorage("run-sqlite.db")
cm = ConversationManager(db)
logger = Logger(db)
agent = LightAgent(PromptGenerator(), GPT35("GPT3.5"), cm, PluginRunner(), logger)


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

    message = Message(msg_id, query, datetime.now(), conv_id,  ["web_search", "car_assistant"])
    
    response, metrics = agent.chat(message)
    print(f"LightAgent: {response}")
    LogHelpers.metrics_printer(metrics)

    LogHelpers.details_logger(metrics, f"log_details_{message.id}.log")
    
    print("=" * 100)
