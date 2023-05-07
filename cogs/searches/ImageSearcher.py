import requests
import random
import os
import validators
from bs4 import BeautifulSoup
from .SearchEngines import SearchEngine

class ImageSearcher():

    ENGINE_ID = os.getenv('ENGINE_ID')
    GOOGLE_KEY = os.getenv('GOOGLE_KEY')

    def __init__(self, engine: SearchEngine = None):
        self._engine = engine
        self._engine_id = self.ENGINE_ID
        self._api_key = self.GOOGLE_KEY
        self._website = 'https://www.googleapis.com/customsearch/v1'

    def search(self, query: str, count: int = 1, safe = True) -> list[str]:
        params = {
            'key': self._api_key,
            'cx': self._engine_id,
            'q': query,
            'searchType': 'image',
            'num': count,
            'start': random.randint(1, 100),
            'safe': 'active' if safe else 'off',
        }

        response = requests.get(self._website, params=params).json()
        results = response['items'] if 'items' in response else []
        links = [result['link'] for result in results]
        return links


    def new_search(self, engine: SearchEngine, query: str, count: int, params: dict[str, str] = {}) -> list[str]:
        url, params = engine.value['url'], engine.value['params'] | params
        response = requests.get(url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup.prettify())
        links = [image['src'] for image in soup.find_all('img') if validators.url(image['src'])]
        return random.sample(links, count) if len(links) >= count else []
