import requests
import time


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
                with open(self.categories[c]['parent_group_name']+'.txt', 'w', encoding='UTF8') as file:
                    file.write(f'ID категории: {self.categories[c]["parent_group_code"]}\n')
                    file.write(f'Категория товаров: {self.categories[c]["parent_group_name"]}\n')
                    file.write(f' -' * 20 + '\n')
                    file.write(f' -' * 20 + '\n')
                    for i in range(len(self.products)):
                        for key, val in self.products[i].items():
                            file.write(f'{key}:{val}\n')
                        file.write(f' -' * 20 + '\n')

            self.products.clear()


parser = Parser5ka()
parser.pars()
print('OK')
