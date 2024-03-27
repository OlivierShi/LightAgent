import os
from llms.base_LLM import BaseLLM
from config import BaseConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import StoppingCriteria

import torch
torch.manual_seed(0)


class EosListStoppingCriteria(StoppingCriteria):
    def __init__(self, eos_sequence):
        self.eos_sequence = eos_sequence

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        last_ids = input_ids[:,-len(self.eos_sequence):].tolist()
        return self.eos_sequence in last_ids
    
class MiniCPM2B(BaseLLM):
    def __init__(self, model_name="minicpm2b", general_stops=["<|im_end|>", "<|im_start|>", "###"], strict_stops=["\n\n",]):
        self.model_name = model_name
        path = 'openbmb/MiniCPM-2B-dpo-fp16'
        self.tokenizer = AutoTokenizer.from_pretrained(path, cache_dir=os.path.join(BaseConfig.BASE_DIR, "res/models/"))
        self.model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.float16, device_map='cuda', trust_remote_code=True, cache_dir=os.path.join(BaseConfig.BASE_DIR, "res/models/"))
        self.stopping_criteria_list_general = [EosListStoppingCriteria(self.tokenizer.encode(f" {stop} ", add_special_tokens=False))[1:-1] for stop in general_stops]
        self.stopping_criteria_list_strict = [EosListStoppingCriteria(self.tokenizer.encode(f" {stop} ", add_special_tokens=False))[1:-1] for stop in strict_stops]

    def llm(self, query, temperature=0.1, top_p=0.8, stopping_criteria=None):
        if stopping_criteria is None:
            stopping_criteria = self.stopping_criteria_list_general

        responds, history = self.model.chat(
            self.tokenizer,
            query,
            temperature=temperature,
            top_p=top_p,
            pad_token_id=self.tokenizer.eos_token_id,
            stopping_criteria=stopping_criteria)
        torch.cuda.empty_cache()
        print(responds)
        return responds

    def generate(self, input, reasoning=True):
        stopping_criteria = self.stopping_criteria_list_general + self.stopping_criteria_list_strict if reasoning else self.stopping_criteria_list_general
        return self.llm(input, stopping_criteria=stopping_criteria)
    