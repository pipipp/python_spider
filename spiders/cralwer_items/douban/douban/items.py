# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    """
    url        文章URL
    title      文章标题
    article    文章内容
    """
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    article = scrapy.Field()
