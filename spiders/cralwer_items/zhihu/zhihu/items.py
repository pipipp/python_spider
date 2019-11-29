# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuItem(scrapy.Item):
    """
    title          文章标题
    description    文章描述
    article        文章内容
    """
    # define the fields for your item here like:
    title = scrapy.Field()
    description = scrapy.Field()
    article = scrapy.Field()
