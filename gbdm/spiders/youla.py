import scrapy
from scrapy.loader import ItemLoader
from gbdm.items import YoulaItem

class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['youla.ru']
    start_urls = ['https://auto.youla.ru/izhevsk/cars/used/renault/?page=1000']
    pages_count = 0

    __css_query = {
        'pagination': 'div.Paginator_block__2XAPy.app_roundedBlockWithShadow__1rh6w '
                      'a div span.Button_text__1ddSj::text',
        'ads': 'div.SerpSnippet_titleWrapper__38bZM '
               'a.SerpSnippet_name__3F7Yu.SerpSnippet_titleText__1Ex8A::attr("href")',
        'title': 'div.AdvertCard_advertTitle__1S1Ak::text',
        'images': 'figure.PhotoGallery_photo__36e_r '
                  'picture img.PhotoGallery_photoImage__2mHGn::attr("src")',
        'param': 'div.AdvertCard_specs__2FEHc div.AdvertSpecs_row__ljPcX',
        'descrip': 'div.AdvertCard_description__2bVlR.AdvertCard_advertBlock__1zrsL '
                   'div.AdvertCard_descriptionInner__KnuRi::text',
        'price': 'div.AdvertCard_price__3dDCr.AdvertCard_topAdvertHeaderCommon__2zUjb.rouble::text'
    }

    def parse(self, response, start=True):
        if start:
            self.pages_count = int(response.css(self.__css_query['pagination']).extract()[-2])

        for num in range(1, self.pages_count + 1):
            yield response.follow(f'https://auto.youla.ru/izhevsk/cars/used/renault/?page={num}',
                                  callback=self.parse,
                                  cb_kwargs={'start': False}
                                  )

        for link in response.css(self.__css_query['ads']):
            yield response.follow(link, callback=self.ads_parse)

    def ads_parse(self, response):
        item_loader = ItemLoader(YoulaItem(), response)
        item_loader.add_value('url', response.url)
        item_loader.add_css('title', self.__css_query['title'])
        item_loader.add_css('images', self.__css_query['images'])
        item_loader.add_css('param', self.__css_query['param'])
        item_loader.add_css('descrip', self.__css_query['descrip'])
        item_loader.add_css('price', self.__css_query['price'])

        yield item_loader.load_item()
