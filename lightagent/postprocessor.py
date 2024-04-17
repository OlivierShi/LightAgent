import json 
import re

class Postprocessor:
    JSON_PATTERN = r'\{.*?\}'

    @staticmethod
    def try_parse_json_from_llm(response: str) -> dict:
        """
        Try to parse the response as JSON.
        :param response: The response to parse.
        :return: The parsed JSON object or None if parsing fails.
        """
        response = Postprocessor.postprocess_llm(response)

        try:
            js = json.loads(response)
            return js
        except json.JSONDecodeError:
            matches = re.findall(Postprocessor.JSON_PATTERN, response)
            if len(matches) > 0:
                return json.loads(matches[0])
            return {}
        
    @staticmethod
    def postprocess_llm(response: str):
        """
        Post-process the response from the language model.
        :param response: The response from the language model.
        :return: The post-processed response.
        """
        # Strip the response
        response = Postprocessor.__remove_stop_tokens(response)
        response = Postprocessor.__strip_response(response)
        return response

    def __strip_response(response: str, chars_to_remove: list = [' ', "'", '"', '`']):
        """
        Strip characters from the start and end of the response.
        :param response: The response from the language model.
        :param chars_to_remove: The characters to remove from the start or end.
        :return: The stripped response.
        """
        # Remove characters from the start
        while len(response) > 0 and response[0] in chars_to_remove:
            response = response[1:]
        
        # Remove characters from the end
        while len(response) > 0 and response[-1] in chars_to_remove:
            response = response[:-1]
        
        return response
    
    def __remove_stop_tokens(response: str, stop_tokens: list = ["<|im_end|>", "<|im_start|>"]):
        """
        Remove stop tokens from the response.
        :param response: The response from the language model.
        :param stop_tokens: The stop tokens to remove.
        :return: The response with stop tokens removed.
        """
        for token in stop_tokens:
            response = response.replace(token, "")
        return response