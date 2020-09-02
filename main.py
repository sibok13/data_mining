from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import os
from pathlib import Path
from dotenv import load_dotenv

from gbdm import settings
from gbdm.spiders.youla import YoulaSpider
from gbdm.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    load_dotenv(dotenv_path=Path('.env').absolute())
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)

    crawl_proc = CrawlerProcess(settings=crawl_settings)

    # crawl_proc.crawl(YoulaSpider)
    crawl_proc.crawl(InstagramSpider, login=os.getenv('INS_USERNAME'), password=os.getenv('ENC_PASSWORD'))

    crawl_proc.start()
