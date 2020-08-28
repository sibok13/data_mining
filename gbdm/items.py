# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy import Selector

def validate_photo(value):
    return value

def get_params(value):
    teg_param = Selector(text=value)
    result = {
        teg_param.css('div.AdvertSpecs_label__2JHnS::text').extract_first():
            f'{teg_param.css("div.AdvertSpecs_data__xK2Qx::text").extract_first()}'
            f'{teg_param.css("div.AdvertSpecs_data__xK2Qx a::text").extract_first()}'.replace('None', '')
    }
    return result

def validate_price(value):
    value = value.replace('\u2009', '')
    return value

class YoulaItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field(input_processor=MapCompose(validate_photo))
    param = scrapy.Field(input_processor=MapCompose(get_params))
    descrip = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(validate_price))
