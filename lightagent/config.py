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

