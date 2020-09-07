from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Firefox()

class MV_Parser:
    domain = 'https://www.mvideo.ru'
    driver.get('https://www.mvideo.ru/promo/bolshaya-shkolnaya-rasprodazha-skidki-bolee-40-mark168010620')

    def __init__(self):
        self.client = MongoClient('mongodb+srv://user:123qwerty@cluster0.mlyot.mongodb.net/test')
        self.db = self.client['pars_mv']
        self.collection = self.db['items']

    __css_query = {
        'items': 'div.product-tiles-list-wrapper div.c-product-tile',
        'price': 'div.c-product-tile__checkout-section div.c-pdp-price__current',
        'pag': 'a.c-pagination__next',
    }

    def pars_page(self):
        while True:
            media_coll = driver.find_element_by_css_selector('body')
            for _ in range(10):
                media_coll.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)
            media_coll.send_keys(Keys.HOME)

            items = self.datas_wait(self.__css_query['items'], multi=True)
            for i in range(0, len(items)):
                item = items[i]
                result = {
                    'title': item.find_element_by_css_selector('h4').text,
                    'price': int(item.find_element_by_css_selector(
                        self.__css_query['price']).text.replace(' ', '').replace('¤', '')),
                }
                self.save_to_mongo(result)

            try:
                next_page = self.datas_wait(self.__css_query['pag'])
                next_page.click()
                time.sleep(2)
            except Exception as e:
                print(e)
                driver.quit()
                break

    def datas_wait(self, css_selector, multi=False):
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            if multi:
                return driver.find_elements_by_css_selector(css_selector)
            return driver.find_element_by_css_selector(css_selector)
        except Exception as e:
            print(e)
            driver.quit()

    def save_to_mongo(self, data):
        self.collection.insert_one(data)


if __name__ == '__main__':
    parser = MV_Parser()
    parser.pars_page()
