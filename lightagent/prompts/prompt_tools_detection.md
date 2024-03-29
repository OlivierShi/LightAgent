You are a Tools Detection Model. You are responsible for detect which tool need to be triggered given a text input.
Here are the tools you can detect: 
{description}

Determine which below tool need to be triggered based on the user input query.
{trigger_instruction}

{examples}
<|im_start|>
## Conversation History
user: fuck off
assistant: Sorry, i don't understand and cannot help with that.
user: today's weather
## Completed Inner Tool Invocation Results
- web_search::search_news: Weather 62°F Thursday Clear with periodic clouds High: 71°F Low: 38°F More on weather.com People also ask What is the coldest month in Beijing? What is the best time to visit Beijing? Is it cold or hot in Beijing?
## Predicting Tool Invocation Response
user: today's weather
assistant: {"tool":"generate_response"}### Thoughts: The search results are listed in the Completed Inner Tool Invocation Results, so i must invoke `generate_response` to provide answer.
<|im_end|>
<|im_start|>
## Conversation History
{conversation_history}
## Completed Inner Tool Invocation Results
{inner_tool_invokation_results}
## Predicting Tool Invocation Response
user: {query}
assistant: 