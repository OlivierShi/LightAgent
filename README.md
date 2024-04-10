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


[
    {
        "name": "open_trunk",
        "description": "Helps the user to open the trunk of the car.",
        "parameters": []
    },
    {
        "name": "close_trunk",
        "description": "Helps the user to close the trunk of the car.",
        "parameters": []
    },
    {
        "name": "lock_doors",
        "description": "Locks all the doors of the car.",
        "parameters": []
    },
    {
        "name": "unlock_doors",
        "description": "Unlocks all the doors of the car.",
        "parameters": []
    },
    {
        "name": "start_engine",
        "description": "Starts the car's engine.",
        "parameters": []
    },
    {
        "name": "stop_engine",
        "description": "Stops the car's engine.",
        "parameters": []
    },
    {
        "name": "activate_headlights",
        "description": "Turns on the car's headlights.",
        "parameters": [
            {
                "name": "mode",
                "type": "string",
                "description": "The mode of the headlights, e.g., 'auto', 'on', 'off'.",
                "required": true
            }
        ]
    },
    {
        "name": "adjust_seat",
        "description": "Adjusts the position of the driver's seat.",
        "parameters": [
            {
                "name": "position",
                "type": "string",
                "description": "The desired position adjustment, e.g., 'forward', 'backward', 'up', 'down'.",
                "required": true
            }
        ]
    },
    {
        "name": "set_temperature",
        "description": "Sets the temperature inside the car.",
        "parameters": [
            {
                "name": "temperature",
                "type": "number",
                "description": "The desired temperature in Celsius or Fahrenheit.",
                "required": true
            }
        ]
    },
    {
        "name": "play_music",
        "description": "Plays music in the car.",
        "parameters": [
            {
                "name": "song_name",
                "type": "string",
                "description": "The name of the song to play.",
                "required": false
            },
            {
                "name": "artist_name",
                "type": "string",
                "description": "The name of the song's artist.",
                "required": false
            }
        ]
    },
    {
        "name": "navigate_to",
        "description": "Sets the car's navigation system to the specified destination.",
        "parameters": [
            {
                "name": "destination",
                "type": "string",
                "description": "The address or name of the destination.",
                "required": true
            }
        ]
    },
    {
        "name": "check_fuel_level",
        "description": "Checks the car's current fuel level.",
        "parameters": []
    },
    {
        "name": "check_tire_pressure",
        "description": "Checks the pressure of all tires.",
        "parameters": []
    }
]
