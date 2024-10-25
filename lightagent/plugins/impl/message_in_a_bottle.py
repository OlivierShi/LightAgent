import requests
from typing import Optional
from ...config import BaseConfig

WECHATMP_USER_ID_HEADER = "wechatmp-user-id"
INTERNAL_USER_ID = "user_id"
class MessageInABottle:
    def __init__(self, name: str = "message_in_a_bottle"):
        self.name = name
        self.base_url = BaseConfig.message_bottle_endpoint

    def get_user_info(self, **kwargs):
        if INTERNAL_USER_ID not in kwargs:
            return "You are not registered."
        headers = {WECHATMP_USER_ID_HEADER: kwargs[INTERNAL_USER_ID]}

        url = f'{self.base_url}/users/me'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        results = response.json()
        if "msg" in results:
            return results["msg"]
            
        return "Failed to get your information."
    
    def update_alias(self, alias: str, **kwargs):
        if INTERNAL_USER_ID not in kwargs:
            return "You are not registered."
        headers = {WECHATMP_USER_ID_HEADER: kwargs[INTERNAL_USER_ID]}
                
        url = f'{self.base_url}/users/me'
        data = {'alias': alias}
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        results = response.json()
        if "msg" in results:
            return results["msg"]
        
        return "Failed to update your alias."
        
    def send_message_bottle(self, content: str, **kwargs):
        if INTERNAL_USER_ID not in kwargs:
            return "You are not registered."
        headers = {WECHATMP_USER_ID_HEADER: kwargs[INTERNAL_USER_ID]}

        url = f'{self.base_url}/send_message_bottle'
        data = {'content': content}
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        results = response.json()
        if "msg" in results:
            return results["msg"]        
        return "Failed to send message bottle."


    def check_message_bottles(self, **kwargs):
        if INTERNAL_USER_ID not in kwargs:
            return "You are not registered."
        headers = {WECHATMP_USER_ID_HEADER: kwargs[INTERNAL_USER_ID]}

        url = f'{self.base_url}/check_message_bottles'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        results = response.json()
        if "msg" in results:
            return results["msg"]          
        return "Failed to check message bottles."

    def reply_to_message_bottle(self, message_id: str, content: str, **kwargs):
        if INTERNAL_USER_ID not in kwargs:
            return "You are not registered."
        headers = {WECHATMP_USER_ID_HEADER: kwargs[INTERNAL_USER_ID]}

        url = f'{self.base_url}/reply_to_message_bottle'
        data = {'message_id': message_id, 'content': content}
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        results = response.json()
        if "msg" in results:
            return results["msg"]   
                
        return "Failed to reply to message bottle."
    
    def retrieve_message_bottle(self, **kwargs):
        if INTERNAL_USER_ID not in kwargs:
            return "You are not registered."
        headers = {WECHATMP_USER_ID_HEADER: kwargs[INTERNAL_USER_ID]}

        url = f'{self.base_url}/retrieve_message_bottle'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        results = response.json()
        if "msg" in results:
            return results["msg"]   
        
        return "Failed to retrieve message bottle."