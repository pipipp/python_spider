# -*- coding: utf-8 -*-
import scrapy


class JianshuCrawlerSpider(scrapy.Spider):
    name = 'jianshu_crawler'
    allowed_domains = ['jianshu.com']
    start_urls = ['http://jianshu.com/']

    def parse(self, response):
        pass
