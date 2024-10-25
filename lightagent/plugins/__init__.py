from typing import List
from ..plugins.impl.web_search import WebSearch
from ..plugins.impl.graphic import Graphic
from ..plugins.impl.message_in_a_bottle import MessageInABottle
from ..plugins.impl.phone_assistant import PhoneAssistant
from ..plugins.impl.car_assistant import CarAssistant


class PluginRunner:
    def __init__(self, ):
        self.web_search = WebSearch()
        self.graphic = Graphic()
        self.message_in_a_bottle = MessageInABottle()
        self.phone_assistant = PhoneAssistant()
        self.car_assistant = CarAssistant()

    def run(self, plugin_name: str, function_name: str, params: dict, **kwargs):
        plugin = getattr(self, plugin_name)
        function = getattr(plugin, function_name)
        combined_params = {**params, **kwargs}
        return function(**combined_params)
    

