from typing import List
import wikipedia
from functools import lru_cache
from bs4 import BeautifulSoup
import requests
import urllib.parse

def google_search(query: str) -> str:
    # todo: implement google search
    html_content = requests.get(f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}")
    soup = BeautifulSoup(html_content.content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    text = "Search tools".join(text.split("Search tools")[1: ]) 
    text = "Settings".join(text.split("Settings")[: -1]).strip()
    return text[:2000]

def bing_search(query: str) -> List[str]:
    # html_content = requests.get(f"https://www.bing.com/search?q={query}&form=QBLH&sp=-1&lq=0&pq=today%27s+weather+in+beijin&sc=11-25&qs=n&sk=&cvid=E5727B4DBE0B4A4DA59CE23DF18604F9&ghsh=0&ghacc=0&ghpl=")
    url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(query)}&form=QBLH&sp=-1&lq=0&ghsh=0&ghacc=0&ghpl=&cc=us&setlang=en"
    html_content = requests.get(url)
    soup = BeautifulSoup(html_content.content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    text = "My org".join(text.split("My org")[1: ]) 
    text = "Pagination".join(text.split("Pagination")[: -1]).strip()
    return text[:1000]


class WebSearch():
    # todo: exception handler
    def __init__(self, name: str = "web_search"):
        self.name = name

    @lru_cache(maxsize=None)
    def search_news(self, query: str) -> str:
        search_results = [google_search(query), bing_search(query)]
        return "\n".join(search_results)

    @lru_cache(maxsize=None)
    def search_wikipedia(self, query: str) -> str:
        try:
            wiki = wikipedia.summary(query, sentences=10)
        except wikipedia.exceptions.DisambiguationError as e:
            wiki = wikipedia.summary(e.options[0], sentences=10)
        return wiki
    

