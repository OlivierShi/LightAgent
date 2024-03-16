from llms.base_LLM import BaseLLM

class EchoLLM(BaseLLM):
    def __init__(self, model_name: str):
        """
        Initialize the language model.
        :param model_name: The name or path to the model.
        """
        pass

    def generate(self, input):
        """
        Generate a response given an input.
        :param input: The input to the model.
        :return: The generated response.
        """
        return input