import requests
from bs4 import BeautifulSoup
from typing import Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from les03_models import Base, Post, Writer, Tags, Hubs


class HABR_Parser:
    domain = 'https://habr.com'
    start_url = 'https://habr.com/ru/top/'
    headers = {
        'User-Agent': 'Mozilla / 5.0(Windows NT 6.1; Win64; x64) AppleWebKit / '
                      '537.36(KHTML, like Gecko) Chrome / '
                      '84.0.4147.105 Safari / 537.36'
    }

    def __init__(self):
        self.engine = create_engine('sqlite:///gb_blog.db')
        self.visited_urls = set()
        self.post_links = set()
        self.post_data = []
        self.url = str
        self.tags_all = []
        self.hubs_all = []

    def pars_page(self, url=start_url):
        while url:
            response = requests.get(url, headers=self.headers)
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soap)
            self.get_post_link(soap)

    def get_next_page(self, soap) -> str:
        a = soap.find('a', attrs={'id': 'next_page'})
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def get_post_link(self, soap):
        h2 = soap.find_all('h2', attrs={'class': 'post__title'})
        links = {itm.find("a").get("href") for itm in h2}
        self.post_links.update(links)

    def parse_page_data(self):
        for url in self.post_links:
            if url in self.visited_urls:
                continue
            response = requests.get(url, headers=self.headers)
            self.url = url
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            if len(self.post_data) > 5:
                break
            self.post_data.append(self.get_post_data(soap))

    def get_post_data(self, soap) -> Dict[str, str]:
        result = {}
        result['title'] = soap.find('span', attrs={'class': 'post__title-text'}).text
        result['url'] = self.url
        full_name_tmp = soap.find('a', attrs={'class': 'user-info__fullname'})
        full_name = full_name_tmp.text if full_name_tmp else ''
        nick_name = soap.find('a', attrs={'class': 'user-info__nickname user-info__nickname_doggy'}).text
        result['writer_name'] = f'{full_name}@{nick_name}'
        writer_url = soap.find('a', attrs={'class': 'user-info__nickname user-info__nickname_doggy'})
        result['writer_url'] = f'{self.domain}{writer_url.get("href")}'
        tags = soap.find('ul', attrs={'class': 'inline-list inline-list_fav-tags js-post-tags'})
        tags_a = tags.find_all('a', attrs={'rel': 'tag'})
        result['tags'] = [[itm.text.strip(), itm.get('href')] for itm in tags_a]
        for i in result['tags']:
            if i in self.tags_all:
                continue
            else:
                self.tags_all.append(i)
        hubs = soap.find('ul', attrs={'class': 'inline-list inline-list_fav-tags js-post-hubs'})
        hubs_a = hubs.find_all('a', attrs={'rel': 'tag'})
        result['hubs'] = [[itm.text.strip(), itm.get('href')] for itm in hubs_a]
        for i in result['hubs']:
            if i in self.hubs_all:
                continue
            else:
                self.hubs_all.append(i)
        return result

    def save_db(self):
        Base.metadata.create_all(self.engine)
        session_db = sessionmaker(bind=self.engine)

        session = session_db()

# Добавление авторов

        writers = [Writer(itm["writer_name"], itm["writer_url"]) for itm in self.post_data]
        session.add_all(writers)
        try:
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()

# Добавление тегов

        tags = [Tags(itm[0], itm[1]) for itm in self.tags_all]
        session.add_all(tags)
        try:
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()

# Добавление хабов

        hubs = [Hubs(itm[0], itm[1]) for itm in self.hubs_all]
        session.add_all(hubs)
        try:
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()

# Добавление постов

        posts = [Post(itm["title"], itm["url"],
                      session.query(Writer.id).filter(Writer.name == itm["writer_name"]),
                      [session.query(Tags.id).filter(Tags.name == itm["tags"][0][0])]
                      # пытался сначала связать пост с 1 тегом, а потом генератором или циклом формировать
                      # список из id тегов и передавать его в модель, но что-то не получается :(
                      # если возможно, прошу разъяснить, как можно сделать в моем решении, чтобы работало
                      # решение так себе, но я его сам выстрадал
                      ) for itm in self.post_data]
        session.add_all(posts)

        try:
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
        finally:
            session.close()


if __name__ == '__main__':
    parser = HABR_Parser()
    parser.pars_page()
    parser.parse_page_data()
    parser.save_db()
    print(1)
