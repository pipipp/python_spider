# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BianWallpaperItem(scrapy.Item):
    """
    title       图片标题
    image_url   图片链接
    """
    title = scrapy.Field()
    image_url = scrapy.Field()
