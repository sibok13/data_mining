import scrapy
from pymongo import MongoClient


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['https://www.avito.ru/izhevsk/kvartiry/prodam']

    __xpath_query = {
        'pagination': '//div[@class="pagination-root-2oCjZ"]/'
                      'span[@class="pagination-item-1WyVp"]/'
                      '@data-marker',
        'ads': '//h3[@class="snippet-title"]/a[@class="snippet-link"][@itemprop="url"]/@href'
    }

    client = MongoClient('mongodb+srv://user:123qwerty@cluster0.mlyot.mongodb.net/test')
    db = client['pars_avito']
    collection = db['ads_avito']

    def parse(self, response, start=True):
        if start:
            pages_count = int(
                response.xpath(self.__xpath_query['pagination']).extract()[-1].split('(')[-1].replace(')', ''))

            for num in range(2, pages_count + 1):
                yield response.follow(f'?p={num}', callback=self.parse, cb_kwargs={'start': False})

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(link, callback=self.ads_parse)

    def ads_parse(self, response):
        result = {}
        title = response.css('h1.title-info-title span.title-info-title-text::text').extract()
        result['title'] = title[0]
        result['url'] = response.url
        result['photo'] = response.css('div.gallery-img-wrapper.js-gallery-img-wrapper '
                                  'div.gallery-img-frame.js-gallery-img-frame::attr("data-url")').extract()
        price = response.css('span.js-item-price::text').extract_first()
        result['price'] = {response.css('span.font_arial-rub::text').extract_first(): int(price.replace(' ', ''))}
        address = response.css('span.item-address__string::text').extract()
        result['address'] = address[0].strip()
        param_title = response.css('ul.item-params-list li.item-params-list-item span::text').extract()
        param_data = response.css('ul.item-params-list li.item-params-list-item::text').extract()[1:-1:2]
        result['params'] = dict(zip(param_title, param_data))

        self.collection.insert(result)

