# -*- coding: utf-8 -*-
import scrapy
import re


class DoubanSpiderSpider(scrapy.Spider):
    name = 'douban_spider'
    allowed_domains = ['https://www.douban.com/j/search']
    start_urls = ['http://https://www.douban.com/j/search/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/78.0.3904.108 Safari/537.36'
    }

    def start_requests(self):
        search_info = 'python'
        url = 'https://www.douban.com/j/search?q={}&start=5&cat=1015'.format(search_info)
        resp = scrapy.Request(url, headers=self.headers)
        return result

    def parse(self, response):
        pass

