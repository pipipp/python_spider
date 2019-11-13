# -*- coding: utf-8 -*-
import scrapy


class CccSpiderSpider(scrapy.Spider):
    name = 'ccc_spider'
    allowed_domains = ['cesium.cisco.com']
    start_urls = ['https://cesium.cisco.com/']

    def parse(self, response):
        pass
