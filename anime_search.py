import requests
import sys
import os
import json

from bs4 import BeautifulSoup
import site_info

from anime import Anime


class SearchException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message


class AnimeSearcher:

    def __init__(self):
        pass

    def search(self, text):
        response = requests.get(site_info.search + text)
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, "html.parser")

        err = soup.find('h2', class_='hl-msg-jump-tit')
        if err:
            raise SearchException("search failed")

        l = soup.find_all('a', class_='hl-item-thumb hl-lazy')
        if not l:
            return []

        r = []
        for it in l:
            r.append(Anime(0, it['title'], it['href'], it['data-original']))
        return r
