from typing import List
import wikipedia
from functools import lru_cache
from bs4 import BeautifulSoup
import requests
import urllib.parse
import asyncio
import concurrent.futures
from googleapiclient.discovery import build
from urllib.parse import urlparse
from ...config import BaseConfig
from ...utils.plugins_helper import PluginsHelper

def fetch_url_content(url: str) -> str:
    try:
        res = requests.get(url, timeout=1)
        res.raise_for_status()
        html_content = res.content
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text[200:2000]
    except Exception as ex:
        print(f"Failed to fetch content from {url}: {ex}")
        return ""

def aggregate_search_results(domains: List[str], results: List[str], max_len=1500) -> str:
    new_results = []
    new_domains = []
    for idx, res in enumerate(results):
        if len(res) > 100:
            new_results.append(res)
            new_domains.append(domains[idx])
    each_len = max_len // len(new_results)
    aggregated_content = ""
    for idx, res in enumerate(new_results):
        aggregated_content += f"{new_domains[idx]}: {res[idx*each_len:(idx+1)*each_len]}\n"

    return aggregated_content

def bing_search_api(query: str, num=2, max_len=1500) -> str:
    subscription_key = BaseConfig.bing_search_api_key
    endpoint = BaseConfig.bing_search_api_endpoint
    params = {"q": query, "mkt": "zh-cn", "sortBy": "Date", "count": 5}
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}

    try:
        bing_response = requests.get(endpoint, headers=headers, params=params, timeout=1)
        bing_response.raise_for_status()
        search_results = bing_response.json()
        
        urls = []
        domains = []
        
        for result in search_results['webPages']['value']:
            url = result['url']
            domain = urlparse(url).netloc
            if domain not in domains:
                urls.append(url)
                domains.append(domain)
            if len(urls) == num:
                break
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(fetch_url_content, urls))

        return aggregate_search_results(domains, results, max_len)

    except Exception as ex:
        print(f"Error during Bing search: {ex}")
        return ""
    
def google_search_api(query: str, num=2, max_len=1500) -> str:
    service = build("customsearch", "v1", developerKey=BaseConfig.google_search_api_key)
    res = service.cse().list(q=query, cx=BaseConfig.google_search_cse_id, num=num).execute()

    urls = []
    domains = []
    
    for result in res['items']:
        url = result['link']
        domain = urlparse(url).netloc
        if domain not in domains:
            urls.append(url)
            domains.append(domain)
        if len(urls) == num: 
            break
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_url_content, urls))

    return aggregate_search_results(domains, results, max_len)

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
        search_results = retry_search(google_search_api, query, retry_cnt)
    elif engine == "bing":
        search_results = retry_search(bing_search_api, query, retry_cnt)
    return search_results


async def async_search_engine(query = "今天西雅图的天气", engine = "google", retry_cnt=1):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, search_engine, query, engine, retry_cnt)
    return result

async def search_web(query = "今天西雅图的天气"):
    if PluginsHelper.is_chinese(query):
        results = await async_search_engine(query, "bing")
    else:
        results = await async_search_engine(query, "google")

    return results

async def search_wiki_and_web(query = "今天西雅图的天气"):
    async def async_wiki_search(query):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, wiki_search, query)
        return result
    
    wiki_results, web_results = await asyncio.gather(async_wiki_search(query), search_web(query))

    return f"From wiki: {wiki_results}\nFrom web: {web_results}"

class WebSearch():
    def __init__(self, name: str = "web_search"):
        self.name = name

    @lru_cache(maxsize=None)
    def search_news(self, query: str) -> str:
        return asyncio.run(search_web(query))

    @lru_cache(maxsize=None)
    def search_wiki(self, query: str) -> str:
        return asyncio.run(search_wiki_and_web(query))

if __name__ == '__main__':
    ws = WebSearch()
    print(ws.search_wiki("今天西雅图的天气"))
    print(ws.search_news("今天西雅图的天气"))
