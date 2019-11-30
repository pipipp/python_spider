# -*- coding: utf-8 -*-
import scrapy

from ..items import BianItem
from scrapy.http import Request
from scrapy.selector import Selector


class BianWallpaperSpider(scrapy.Spider):
    name = 'bian_wallpaper'
    allowed_domains = ['www.netbian.com']
    start_urls = ['http://www.netbian.com/dongman1920_1080/index.htm']

    def parse(self, response):
        """
        解析HTML，保存图片
        :param response:
        :return:
        """
        item = BianItem()
        selector = Selector(response)
        all_wallpaper = selector.css('div.list ul li').extract()
        for info in all_wallpaper:
            print('info: {}'.format(info))
            item['description'] = info.css('a img::src').extract_first()
            item['image'] = info.css('a img::alt').extract_first()
            yield item

        # next_url = self.start_urls[0]
        # self.logger.info('Next url: {}'.format(next_url))
        # yield Request(url=next_url, callback=self.get_each_url)
