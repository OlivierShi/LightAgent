from pathlib import Path
import os
import sys

sys.path.append(os.path.join(str(Path(__file__).resolve().parent.parent), "lightagent"))
sys.path.append('../lightagent/')


def test_plugin_runner():
    from lightagent.plugins import PluginRunner
    p = PluginRunner()

    print(p.run("web_search", "search_news", {"query": "Today's news on Sport"}))

def test_search_news():
    from lightagent.plugins.impl.web_search import WebSearch
    ws = WebSearch()
    print(ws.search_news("今天seattle天气"))

def test_google_search_api():
    from lightagent.plugins.impl.web_search import google_search_api
    print(google_search_api("what's the weather in Seattle?"))


def test_search_wiki():
    from lightagent.plugins.impl.web_search import WebSearch
    ws = WebSearch()
    print(ws.search_wiki("姚明老婆"))

def test_lightAgent_chat():
    from datetime import datetime
    from lightagent.prompt_generator import PromptGenerator
    from lightagent.models import Message
    from lightagent.llms import GPT35
    from lightagent.plugins import PluginRunner
    from lightagent.LightAgent import LightAgent
    orch = LightAgent(PromptGenerator(), GPT35("gpt3.5"), PluginRunner())

    msg = Message("Retrieve a bottle message", role="user", last_modified_datetime=datetime.now(), conversation_id="123", enabled_plugins=["web_search", "message_in_a_bottle"])

    response, metrics = orch.chat(msg)
    print(response)

def test_sqlite3():
    from lightagent.storage.sqlite import SQLiteStorage
    db = SQLiteStorage("test.db")

    db.create_table("users", "id TEXT PRIMARY KEY, name TEXT, conversation_id_list TEXT")
    db.create_table("conversations", "id TEXT PRIMARY KEY, user_id TEXT, message_id_list TEXT")
    db.create_table("messages", "id TEXT PRIMARY KEY, content TEXT, last_modified_datetime TEXT, location TEXT, conversation_id TEXT, enabled_plugins TEXT, inner_tool_invokation_results TEXT, response TEXT")
    
def test_conv_manager_save_message():
    from lightagent.storage.conversation_manager import ConversationManager
    from lightagent.storage.sqlite import SQLiteStorage
    from lightagent.models import Message, Context, UserProfile
    from datetime import datetime
    db = SQLiteStorage("test-sqlite.db")
    cm = ConversationManager(db)

    message = Message("123", "Hello, World!", datetime.now(), "abcd", ["web_search", "message_in_a_bottle"])
    
    context = Context("abcd", [], UserProfile("1", "Mike"), [], [])
    
    cm.save_message(message, context)

    db.close()

def test_conv_manager_get_message():
    from lightagent.storage.conversation_manager import ConversationManager
    from lightagent.storage.sqlite import SQLiteStorage
    from lightagent.models import Message, Context, UserProfile
    from datetime import datetime
    db = SQLiteStorage("test-sqlite.db")
    cm = ConversationManager(db)

    message = Message("123", "Hello, World!", datetime.now(), "abcd", ["web_search", "message_in_a_bottle"])
    
    context = cm.get_message_context(message)

    print(context)
    db.close()

def test_LightAgent_multiturn():
    from datetime import datetime
    from lightagent.prompt_generator import PromptGenerator
    from lightagent.storage.conversation_manager import ConversationManager
    from lightagent.storage.logger import Logger
    from lightagent.storage.sqlite import SQLiteStorage    
    from lightagent.models import Message
    from lightagent.llms import GPT35
    from lightagent.plugins import PluginRunner
    from lightagent.LightAgent import LightAgent
    if os.path.exists("test-sqlite.db"):
        os.remove("test-sqlite.db")
    db = SQLiteStorage("test-sqlite.db")
    cm = ConversationManager(db)
    logger = Logger(db)
    orch = LightAgent(PromptGenerator(), GPT35("gpt3.5"), cm, PluginRunner(), logger)

    message = Message("123", "Who are you?", datetime.now(), "abcd",  ["web_search", "message_in_a_bottle"])
    response, metrics = orch.chat(message)
    print(response)

    message = Message("234", "What's the weather in New York City?", datetime.now(), "abcd",  ["web_search", "message_in_a_bottle"])
    
    response, metrics = orch.chat(message)
    print(response)    

    message = Message("345", "What time is it?", datetime.now(), "abcd",  ["web_search", "message_in_a_bottle"])
    
    response, metrics = orch.chat(message)
    print(response)    

    message = Message("456", "Do you know who is the wife of Yao Min?", datetime.now(), "abcd",  ["web_search", "message_in_a_bottle"])
    
    response, metrics = orch.chat(message)
    print(response)    


def test_minicpm2b():
    from lightagent.llms.minicpm2b import MiniCPM2B
    m = MiniCPM2B()


# test_bing_search()
# test_google_search()
# test_lightAgent_chat()
# test_conv_manager_save_message()
# test_conv_manager_get_message()
# test_LightAgent_multiturn()
# test_wiki_search()
# test_minicpm2b()
# test_search_news()
# test_search_wiki()
test_google_search_api()