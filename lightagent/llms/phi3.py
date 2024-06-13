import os
from llms.base_LLM import BaseLLM
from config import BaseConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import StoppingCriteria
import onnxruntime_genai as og

import torch
torch.manual_seed(0)

class Phi3(BaseLLM):

    def __init__(self):
        self.model_name = "phi3-mini-int4"
        path = os.path.join(BaseConfig.BASE_DIR, "res/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4")
        self.model = og.Model(path)
        print("Model loaded")
        self.tokenizer = og.Tokenizer(self.model)
        self.tokenizer_stream = self.tokenizer.create_stream()
        print("Tokenizer created")

        self.role_user = "<|user|>"
        self.role_system = "<|assistant|>"
        self.stop_tokens = ["<|end|>", "\n", "<|assistant|>", "<|user|>"]
        self._warmup()

    def _warmup(self,):
        response = self.llm("Hello, how are you?")
        print(f"{self.model_name} Warmup successful.")

    def llm(self, query, max_new_tokens=80):
        query = query.replace("<user>", self.role_user).replace("<assistant>", self.role_system)        
        input_tokens = self.tokenizer.encode(query)
        params = og.GeneratorParams(self.model)
        self.search_options = {
            'max_length': max_new_tokens + len(input_tokens),
        }
        params.set_search_options(**self.search_options)
        params.input_ids = input_tokens
        generator = og.Generator(self.model, params)
        result = ''
        new_tokens = [] 
        try:
            while not generator.is_done():
                generator.compute_logits()
                generator.generate_next_token()

                new_token = generator.get_next_tokens()[0]
                token = self.tokenizer_stream.decode(new_token)
                result += token
                new_tokens.append(new_token)
                if token in self.stop_tokens:
                    break
        except KeyboardInterrupt:
            print("  --control+c pressed, aborting generation--")

        # Delete the generator to free the captured graph for the next generator, if graph capture is enabled
        del generator

        return result

    def generate(self, input, reasoning=True):
        max_new_tokens = 30 if reasoning else 80
        return self.llm(input, max_new_tokens=max_new_tokens)
