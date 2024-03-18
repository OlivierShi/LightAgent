from pathlib import Path
import os
import sys

sys.path.append(os.path.join(str(Path(__file__).resolve().parent.parent), "lightagent"))
sys.path.append('../lightagent/')


def test_plugin_runner():
    from lightagent.plugins import PluginRunner
    p = PluginRunner()

    print(p.run("web_search", "search_news", {"query": "Today's news on Sport"}))

def test_google_search():
    from lightagent.plugins.impl.web_search import google_search
    print(google_search("Today's weather in New York City"))

def test_bing_search():
    from lightagent.plugins.impl.web_search import bing_search
    print(bing_search("Today's weather in New York City"))


def test_lightOrch_chat():
    from datetime import datetime
    from lightagent.prompt_generator import PromptGenerator
    from lightagent.models import Message
    from lightagent.llms import GPT35
    from lightagent.plugins import PluginRunner
    from lightagent.LightAgent import LightAgent
    orch = LightAgent(PromptGenerator(), GPT35("gpt3.5"), PluginRunner())

    msg = Message("Retrieve a bottle message", role="user", last_modified_datetime=datetime.now(), conversation_id="123", enabled_plugins=["web_search", "message_in_a_bottle"])

    response = orch.chat(msg)
    print(response)

def test_sqlite3():
    from lightagent.storage.sqlite import SQLiteStorage
    db = SQLiteStorage("test.db")
    

# test_bing_search()
# test_google_search()
# test_lightOrch_chat()