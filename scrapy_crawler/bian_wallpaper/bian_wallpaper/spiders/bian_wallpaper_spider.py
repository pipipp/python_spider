"""
爬取彼岸壁纸网站的动漫系列壁纸(1920x1080)
"""
# -*- coding: utf-8 -*-
import scrapy
import time

from ..items import BianWallpaperItem
from scrapy.http import Request
from scrapy.selector import Selector

__author__ = 'Evan'


class BianWallpaperSpider(scrapy.Spider):
    name = 'bian_wallpaper_spider'
    allowed_domains = ['www.netbian.com']
    start_urls = ['http://www.netbian.com/dongman1920_1080/index.htm']

    def parse(self, response):
        """
        解析HTML
        :param response:
        :return:
        """
        selector = Selector(response)
        all_wallpaper = selector.css('div.list ul li')
        for info in all_wallpaper:
            after_url = 'http://' + self.allowed_domains[0] + info.css('a::attr(href)').extract_first()
            yield Request(url=after_url, callback=self.save_wallpaper)

        next_page = selector.xpath('//div[@class="page"]/a[last()]/@href').extract_first()
        next_url = 'http://' + self.allowed_domains[0] + next_page
        self.logger.info('Next url: {}'.format(next_url))
        # 加3秒延时，防止爬取过快导致页面丢失
        time.sleep(3)
        yield Request(url=next_url, callback=self.parse)

    def save_wallpaper(self, response):
        """
        保存高清壁纸链接
        :param response:
        :return:
        """
        selector = Selector(response)
        item = BianWallpaperItem()
        item['title'] = selector.css('div.pic p a img::attr(title)').extract_first()
        item['image_url'] = selector.css('div.pic p a img::attr(src)').extract_first()
        yield item
