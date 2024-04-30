from typing import List
import wikipedia
from functools import lru_cache
from bs4 import BeautifulSoup
import requests
import urllib.parse
import asyncio
import concurrent.futures
from config import BaseConfig
from googleapiclient.discovery import build

def google_search_api(query: str, num=4) -> List[str]:
    service = build("customsearch", "v1", developerKey=BaseConfig.google_search_api_key)
    res = service.cse().list(q=query, cx=BaseConfig.google_search_cse_id, num=num).execute()

    print(res['items'])
    url = res['items'][0]["link"]

    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(f"Failed to get search results from google. Status code: {res.status_code}")
    html_content = res.content
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text

def google_search(query: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        "Sec-Ch-Ua-Platform": "Windows",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Sec-Ch-Ua-Platform-Version": "14.0.0"
    }
    url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to get search results from google. Status code: {res.status_code}")
    html_content = res.content
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text[200:2200]

def bing_search(query: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        "Sec-Ch-Ua": "Google Chrome",
        "Accept-Language": "en"
    }
    url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(query)}&cc=-1"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to get search results from bing. Status code: {res.status_code}")
    html_content = res.content
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text[500:1500]

def wiki_search(query: str) -> str:
    try:
        wiki = wikipedia.summary(query, sentences=10)
    except wikipedia.exceptions.DisambiguationError as e:
        wiki = wikipedia.summary(e.options[0], sentences=5)
    except wikipedia.exceptions.PageError as e:
        wiki = "No result found from wikipedia."
    return wiki

def search_engine(query: str, engine: str, retry_cnt=1) -> str:
    def retry_search(engine_func, query, retry_cnt):
        result = "No result found."
        while retry_cnt >= 0:
            try:
                result = engine_func(query)
                break
            except:
                retry_cnt -= 1
        return result
    
    search_results = "No result found."
    if engine == "google":
        search_results = retry_search(google_search, query, retry_cnt)
    elif engine == "bing":
        search_results = retry_search(bing_search, query, retry_cnt)
    return search_results


async def async_search_engine(query = "今天西雅图的天气", engine = "google", retry_cnt=1):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, search_engine, query, engine, retry_cnt)
    return result

async def search_web(query = "今天西雅图的天气"):
    google_results, bing_results = await asyncio.gather(async_search_engine(query, "bing"), async_search_engine(query, "google"))
    return "\n".join([google_results, bing_results])

async def search_wiki_and_news(query = "今天西雅图的天气"):
    async def async_wiki_search(query):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, wiki_search, query)
        return result
    
    wiki_results, google_results, bing_results = await asyncio.gather(async_wiki_search(query), async_search_engine(query, "google"), async_search_engine(query, "bing"))

    return wiki_results + "\n" + google_results[int(len(google_results)/2):] + "\n" + bing_results[int(len(bing_results)/2):]

class WebSearch():
    def __init__(self, name: str = "web_search"):
        self.name = name

    @lru_cache(maxsize=None)
    def search_news(self, query: str) -> str:
        return asyncio.run(search_web(query))

    @lru_cache(maxsize=None)
    def search_wiki(self, query: str) -> str:
        return asyncio.run(search_wiki_and_news(query))

if __name__ == '__main__':
    ws = WebSearch()
    print(ws.search_wiki("今天西雅图的天气"))
    print(ws.search_news("今天西雅图的天气"))
