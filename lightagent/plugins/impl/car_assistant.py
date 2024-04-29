
class CarAssistant:
    def __init__(self, name: str = "car_assistant"):
        self.name = name

    def navigate_to(self, location: str):
        return f"I have set the destination to {location}."

    def set_temperature(self, temperature: int):
        return f"I have set the temperature to {temperature} degrees."
    
    def find_parking(self, radius: int = 1000):
        return f"I have found a parking spot within {radius} meters."

    def control_lighting(self, state: bool, light_type: str = "headlights"):
        return f"I have turned the {light_type} {'on' if state else 'off'}."
    
    def adjust_windows(self, state: bool, window_type: str = "driver_side"):
        return f"I have rolled the {window_type} window {'up' if state else 'down'}."
    
    def play_music(self, query: str):
        return f"I have started playing music for {query}."
    
    def adjust_volume(self, level = None, rate = None, direction: str = None):

        if level is not None:
            return f"I have adjusted the volume to {level}."
        
        if rate is not None:
            return f"I have adjusted {direction} the volume by {rate*100}%."
        
        if direction is not None:
            return f"I have adjusted to {direction} the volume by 20%."
        
    def ces(self, ):
        return "Contacting emergency services."
    