from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def __init__(self, model_name: str):
        """
        Initialize the language model.
        :param model_name: The name or path to the model.
        """
        pass

    @abstractmethod
    def generate(self, input, reasoning=True):
        """
        Generate a response given an input.
        :param input: The input to the model.
        :param reasoning: This generation is for reasoning or not.
        :return: The generated response.
        """
        pass