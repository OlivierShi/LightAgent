from typing import List
from plugins.impl.web_search import WebSearch
from plugins.impl.graphic import Graphic
from plugins.impl.message_in_a_bottle import MessageInABottle


class PluginRunner:
    def __init__(self, ):
        self.web_search = WebSearch()
        self.graphic = Graphic()
        self.message_in_a_bottle = MessageInABottle()

    def run(self, plugin_name: str, function_name: str, params: dict):
        plugin = getattr(self, plugin_name)
        function = getattr(plugin, function_name)
        return function(**params)
    

