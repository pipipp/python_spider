# -*- coding=utf8 -*-
from scrapy import cmdline

# 运行douban_spider爬虫
cmdline.execute("scrapy crawl douban_spider -o ./result/douban.json".split())
