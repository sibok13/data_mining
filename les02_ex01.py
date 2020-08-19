import requests
from bs4 import BeautifulSoup
from typing import Dict
from pymongo import MongoClient
import re
import datetime as dt


class GBB_Parser:
    domain = 'https://geekbrains.ru'
    start_url = 'https://geekbrains.ru/posts'
    headers = {
        'User-Agent': 'Mozilla / 5.0(Windows NT 6.1; Win64; x64) AppleWebKit / '
                      '537.36(KHTML, like Gecko) Chrome / '
                      '84.0.4147.105 Safari / 537.36'
    }

    def __init__(self):
        self.client = MongoClient('mongodb+srv://user:123qwerty@cluster0.mlyot.mongodb.net/test')
        self.db = self.client['pars_gb_blog']
        self.collection = self.db['posts']
        self.visited_urls = set()
        self.post_links = set()
        self.post_data = []
        self.url = str

    def pars_page(self, url=start_url):
        while url:
            response = requests.get(url, headers=self.headers)
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soap)
            self.get_post_link(soap)

    def get_next_page(self, soap) -> str:
        ul = soap.find('ul', attrs={'class': 'gb__pagination'})
        a = ul.find('a', text='›')
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def get_post_link(self, soap):
        wrapper = soap.find('div', attrs={'class': 'post-items-wrapper'})
        posts = wrapper.find_all('div', attrs={'class': 'post-item'})
        links = {f'{self.domain}{itm.find("a").get("href")}' for itm in posts}
        self.post_links.update(links)

    def parse_page_data(self):
        for url in self.post_links:
            if url in self.visited_urls:
                continue
            response = requests.get(url, headers=self.headers)
            self.url = url
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            # if len(self.post_data) > 5:
            #     break
            self.post_data.append(self.get_post_data(soap))

    def get_post_data(self, soap) -> Dict[str, str]:
        result = {}
        result['url'] = self.url
        result['title'] = soap.find('h1').text
        content = soap.find('div', attrs={'class': 'blogpost-content', 'itemprop': 'articleBody'})
        img = content.find('img')
        result['image'] = img.get('src') if img else None
        result['writer_name'] = soap.find('div', attrs={'itemprop': 'author'}).text
        article = soap.find('article')
        writer_link = article.find('a', attrs={'href': re.compile('/users/\d+')}).get('href')
        result['writer_url'] = f'{self.domain}{writer_link}'
        result['pub_date'] = dt.datetime.fromisoformat(soap.find('time', attrs={'itemprop':'datePublished'}).get('datetime'))
        return result

    def save_to_mongo(self):
        self.collection.insert_many(self.post_data)

    def load_from_mongo(self, start, end):
        start = dt.datetime.fromisoformat(start)
        end = dt.datetime.fromisoformat(end)
        result = self.collection.find({'pub_date': {'$gte': start, '$lt': end}})
        print(list(result))


if __name__ == '__main__':
    parser = GBB_Parser()
    parser.pars_page()
    parser.parse_page_data()
    parser.save_to_mongo()
    parser.load_from_mongo('2015-11-01', '2015-11-30')
