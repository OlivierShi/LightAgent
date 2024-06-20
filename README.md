# LightAgent
LightAgent is a framework for developing applications powered by mini LLM.


# todo:
1. responding prompt, exclude the plugin instructions that are not triggered. &#9745;
2. add metrics to log the latency. &#9745;
3. add assistant plugin. &#9745;
4. reduce the tokens of the conversation_history
5. fix bugs. &#9745;
6. add warmup &#9745;
7. improve web search api
9. add stop tokens &#9745;
10. fix json format &#9745;
11. improve extraction prompt &#9745;
12. add conntent summarization tool with LLM
13. add phi3-int4 evaluation


# good cases

## LightAgent with MiniCPM-2B 
- User: 你是谁
- LightAgent: I am LightAgent, an AI assistant designed to help users with their queries and tasks. I am capable of providing information, answering questions, and assisting with various tasks. I am here to make your life easier and more enjoyable. If you have any questions or need assistance, please feel free to ask.

- User: 北京今天出门要带伞吗
- LightAgent: Based on the information provided, it is not necessary to bring an umbrella in Beijing today. However, it is always a good idea to check the weather forecast before heading out. If the weather is expected to change or become rainy, it might be a good idea to bring an umbrella just in case.

- User: 奥巴马能赢得2024年美国大选吗
- LightAgent: Hello, I'm LightAgent. I'm sorry for the confusion, but I cannot provide real-time information or predictions. However, I can tell you that Barack Obama, a former U.S. President, is a well-known political figure. As of my last update, he is not a current candidate for the 2024 U.S. Presidential election.

- User: 金字旁加一个川读什么音
- LightAgent: 金字旁加一个川的读音是 chuàn。

## LightAgent with Phi-3B-Int4
- User: 你是谁
- LightAgent: This is LightAgent, ready to assist you! 😊

- User: Do I need to bring an umbrella when going out in Seattle today?
- LightAgent: Seattle's unspoken rules suggest that umbrellas are generally not recommended unless it's torrential rain. The Seattle weather forecast for today is 26°C.

- User: Can Obama win the 2024 US election?
- LightAgent: As an AI, I don't predict political outcomes. However, I can provide information on the current political landscape and election processes.