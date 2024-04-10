# LightAgent
LightAgent is a framework for developing applications powered by mini LLM.


# todo:
1. responding prompt, exclude the plugin instructions that are not triggered. &#9745;
2. add metrics to log the latency. &#9745;
3. add assistant plugin.
4. reduce the tokens of the conversation_history
5. fix bugs.
6. add warmup &#9745;
7. improve web search api


[
  {
    "name": "place_call",
    "description": "Helps the user to place a phone call to a specified phone number or contact stored in the phone.",
    "parameters": [
      {"name": "phone_number", "type": "string", "description": "The phone number to call, formatted as a string."}
    ]
  },
  {
    "name": "send_sms",
    "description": "Sends an SMS message to a specified phone number with a user-defined message.",
    "parameters": [
      {"name": "phone_number", "type": "string", "description": "The recipient's phone number."},
      {"name": "message", "type": "string", "description": "The text message to send."}
    ]
  },
  {
    "name": "set_alarm",
    "description": "Sets an alarm for the user at a specified time.",
    "parameters": [
      {"name": "time", "type": "string", "description": "The time to set the alarm for, typically in HH:MM format."},
      {"name": "label", "type": "string", "description": "An optional label for the alarm.", "optional": true}
    ]
  },
  {
    "name": "create_reminder",
    "description": "Creates a reminder with a specified title, message, and time.",
    "parameters": [
      {"name": "title", "type": "string", "description": "The title of the reminder."},
      {"name": "message", "type": "string", "description": "A message or note about the reminder."},
      {"name": "time", "type": "string", "description": "The time or date when the reminder should alert the user."}
    ]
  },
  {
    "name": "open_app",
    "description": "Opens an application installed on the user's phone.",
    "parameters": [
      {"name": "app_name", "type": "string", "description": "The name of the application to open."}
    ]
  },
  {
    "name": "play_music",
    "description": "Plays music based on the user's request. Can specify a song, artist, or playlist.",
    "parameters": [
      {"name": "query", "type": "string", "description": "A search query to find the music to play, such as a song title, artist name, or playlist name."}
    ]
  },
  {
    "name": "check_weather",
    "description": "Provides weather information for a specified location.",
    "parameters": [
      {"name": "location", "type": "string", "description": "The location to check the weather for. Can be a city name, zip code, or coordinates."}
    ]
  },
  {
    "name": "navigate_to",
    "description": "Starts navigation to a specified destination using the phone's map service.",
    "parameters": [
      {"name": "destination", "type": "string", "description": "The destination address or landmark to navigate to."}
    ]
  },
  {
    "name": "take_photo",
    "description": "Activates the phone's camera to take a photo.",
    "parameters": []
  },
  {
    "name": "record_video",
    "description": "Starts recording a video with the phone's camera.",
    "parameters": []
  },
  {
    "name": "search_online",
    "description": "Performs an online search based on the user's query.",
    "parameters": [
      {"name": "query", "type": "string", "description": "The search query."}
    ]
  }
]
