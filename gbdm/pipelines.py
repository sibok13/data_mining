# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from pymongo import MongoClient

class GbdmPipeline:

    def __init__(self):
        client = MongoClient('mongodb+srv://user:123qwerty@cluster0.mlyot.mongodb.net/test')
        self.db = client['pars_youla']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        collection.insert_one(item)
        return item

class GbdmImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for url in item.get('images', []):
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if item.get('images'):
            item['images'] = [itm[1] for itm in results if itm[0]]
        return item
