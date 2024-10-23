from datetime import datetime
import os
import uuid
import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from lightagent.prompts.prompt_generator import PromptGenerator
from lightagent.storage.conversation_manager import ConversationManager
from lightagent.storage.logger import Logger
from lightagent.storage.sqlite import SQLiteStorage    
from lightagent.data_schemas import Message
from lightagent.llms import GPT35, Phi3
from lightagent.plugins import PluginRunner
from lightagent.LightAgent import LightAgent
from lightagent.utils.log_helpers import LogHelpers


def main(args):
    if os.path.exists("run-sqlite.db"):
        os.remove("run-sqlite.db")
    db = SQLiteStorage("run-sqlite.db")
    cm = ConversationManager(db)
    logger = Logger(db)
    agent = LightAgent(PromptGenerator(), GPT35(), cm, PluginRunner(), logger)


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

        message = Message(msg_id, query, datetime.now(), conv_id,  ["web_search", "phone_assistant"])
        
        new_message, metrics = agent.chat(message)
        print(f"LightAgent: {new_message.response}")
        LogHelpers.metrics_printer(metrics)

        if args.verbose:
            LogHelpers.details_logger(metrics, f"log_details_{message.id}.log")
        
        print("=" * 100)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with LightAgent. Type 'new' to start a new conversation, 'exit' to exit.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Write detail logs into the text for debuging, each message will be stored in a file.")

    args = parser.parse_args()

    main(args)