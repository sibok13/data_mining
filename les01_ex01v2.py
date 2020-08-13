import requests
import time
import json

class Parser5ka:
    _domain = 'https://5ka.ru/'
    _api_path = 'api/v2/special_offers/'
    _api_cat = 'api/v2/categories/'
    params = {
        'categories': 0,
        'records_per_page': 15
    }
    headers = {
        'User-Agent': 'Mozilla / 5.0(Windows NT 6.1; Win64; x64) AppleWebKit / '
                      '537.36(KHTML, like Gecko) Chrome / '
                      '84.0.4147.105 Safari / 537.36'
    }

    def __init__(self):
        self.products = []
        self.categories = []

    def pars(self):
        params = self.params
        headers = self.headers
        url = self._domain + self._api_path
        url_cat = self._domain + self._api_cat

        response_cat = requests.get(url_cat, headers=headers)
        cat = response_cat.json()
        self.categories.extend(cat)

        for c in range(len(self.categories)):
            params['categories'] = int(self.categories[c]['parent_group_code'])
            params_data = params
            url_data = url
            while url_data:
                response = requests.get(url_data, headers=headers, params=params_data)
                data = response.json()
                params = {}
                url_data = data['next']
                self.products.extend(data['results'])
                time.sleep(0.1)

            if len(self.products) > 0:
                data = {
                    'name': self.categories[c]["parent_group_name"],
                    'code': self.categories[c]["parent_group_code"],
                    'products': self.products
                    }
                with open(self.categories[c]['parent_group_name']+'.json', 'w', encoding='UTF8') as file:
                    json.dump(data, file, ensure_ascii=False)

            self.products.clear()


parser = Parser5ka()
parser.pars()
print('OK')
