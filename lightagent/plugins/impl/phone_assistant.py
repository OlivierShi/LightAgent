
class PhoneAssistant:
    def __init__(self, name: str = "phone_assistant"):
        self.name = name

    def place_call(self, phone_number: str):
        return f"Calling {phone_number}."

    def send_sms(self, phone_number: str = None, message: str = None):

        response = "I have opened the SMS app."
        if phone_number is None or phone_number == "":
            response += " Please add a phone number."
        if message is None or message == "":
            response += " Please add a message."
        
        response += " You need confirm the phone number and the message before sending."
        return response

    def set_alarm(self, time: str):
        return f"Setting alarm for {time}."

    def create_reminder(self, time: str, title: str = None, message: str = None):
        if title is None or title == "":
            title = "[AIPhone] Reminder"
        if message is None or message == "":
            message = f"Reminder {time}"

        return f"Creating reminder for {time} with title {title} and message {message}."
    
    def open_app(self, app_name: str):
        return f"Opening {app_name}."
    
    def play_music(self, query: str):
        return f"Playing music with query {query}."
    
