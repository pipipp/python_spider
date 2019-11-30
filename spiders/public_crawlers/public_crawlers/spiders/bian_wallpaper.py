# -*- coding: utf-8 -*-
import scrapy


class BianWallpaperSpider(scrapy.Spider):
    name = 'bian_wallpaper'
    allowed_domains = ['www.netbian.com']
    start_urls = ['http://www.netbian.com/']

    def parse(self, response):
        pass
