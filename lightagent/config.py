# -*- encoding: utf-8 -*-
import os
from dotenv import load_dotenv

class BaseConfig():
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    openai_api_key = os.getenv('openai_api_key')
    openai_azure_endpoint = os.getenv('openai_azure_endpoint')
    openai_api_version = os.getenv('openai_api_version')
    openai_api_model = os.getenv('openai_api_model')

    google_search_api_key = os.getenv('google_api_key')
    google_search_cse_id = os.getenv('google_cse_id')

    bing_search_api_key = os.getenv('bing_search_api_key')
    bing_search_api_endpoint = os.getenv('bing_search_api_endpoint')

    # constants
    MAX_CONVERSATION_HISTORY_TURNS = 4  # Only put the last 4 messages into the conversation history
    MAX_CONVERSATION_HISTORY_DAYS = 2  # Only put the messages in the last 2 days into the conversation history

    MAX_SEARCH_ENGINE_RESULTS = 5
