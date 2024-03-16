class MessageInABottle:
    def __init__(self, name: str = "message_in_a_bottle"):
        self.name = name

    def retrieve_message_bottle(self, ):
        return """{"creator": "Olivier", "content": "Anybody out there?", "datetime": "2022-01-01T12:00:00"}"""
    
    def send_message_bottle(self, content: str):
        return f"Sending message bottle with content: {content}."
    
    def introduction(self, ):
        return "I am a message in a bottle. I can send and retrieve messages in a bottle."