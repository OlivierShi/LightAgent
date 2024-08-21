from openai import AzureOpenAI
from llms.base_LLM import BaseLLM
from config import BaseConfig

class GPT35(BaseLLM):
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = AzureOpenAI(
            azure_endpoint = BaseConfig.openai_azure_endpoint, 
            api_key=BaseConfig.openai_api_key,  
            api_version=BaseConfig.openai_api_version
            )
        
        self.role_user = "user:"
        self.role_system = "assistant:"
        self._warmup()

    def _warmup(self,):
        response = self.generate("Hello, how are you?")
        print(f"{self.model_name} Warmup successful.")

    def generate(self, input, reasoning=True, postprocessors=[]):
        stops = ["\n\n", self.role_system] if reasoning else [self.role_system]
        input = input.replace("<user>", self.role_user).replace("<assistant>", self.role_system)

        messages = [{"role":"system","content":input}]
        completion = self.client.chat.completions.create(
            model=BaseConfig.openai_api_model,
            messages = messages,
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stops
        )
        return completion.choices[0].message.content