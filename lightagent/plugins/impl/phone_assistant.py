
class PhoneAssistant:
    def __init__(self, name: str = "phone_assistant"):
        self.name = name

    def place_call(self, phone_number: str):
        return f"I have placed the call to {phone_number}."

    def send_sms(self, phone_number: str = None, message: str = None):

        response = "I have opened the SMS app."
        if phone_number is None or phone_number == "":
            response += " Please add a phone number."
        if message is None or message == "":
            response += " Please add a message."
        
        response += " You need confirm the phone number and the message before sending."
        return response

    def set_alarm(self, time: str):
        return f"I have set the alarm for the time {time}."

    def create_reminder(self, time: str, title: str = None, message: str = None):
        if title is None or title == "":
            title = "[AIPhone] Reminder"
        if message is None or message == "":
            message = f"Reminder {time}"

        return f"I have created a reminder for you on {time}."
    
    def open_app(self, app_name: str):
        return f"I have opened the app {app_name}."
    
    def play_music(self, query: str):
        return f"I have started playing music for {query}."
    
    def adjust_volume(self, level = None, rate = None, direction: str = None):

        if level is not None:
            return f"I have adjusted the volume to {level}."
        
        if rate is not None:
            return f"I have adjusted {direction} the volume by {rate*100}%."
        
        if direction is not None:
            return f"I have adjusted to {direction} the volume by 20%."
        
    def adjust_brightness(self, level = None, rate = None, direction: str = None):

        if level is not None:
            return f"I have adjusted the brightness to {level}."
        
        if rate is not None:
            return f"I have adjusted {direction} the brightness by {rate*100}%."
        
        if direction is not None:
            return f"I have adjusted to {direction} the brightness by 20%."
        
    def toggle_wifi(self, state: bool):
        return f"I have turned the WiFi {'on' if state else 'off'}."
    
    def toggle_bluetooth(self, state: bool):
        return f"I have turned the Bluetooth {'on' if state else 'off'}."
    
    def toggle_dnd(self, state: bool):
        return f"I have turned the Do Not Disturb mode {'on' if state else 'off'}."
    
    def toggle_power_saving(self, state: bool):
        return f"I have turned the power saving mode {'on' if state else 'off'}."
    