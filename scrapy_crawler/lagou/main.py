# -*- coding=utf8 -*-
from scrapy import cmdline

# 运行lagou_spider爬虫
cmdline.execute("scrapy crawl lagou_spider -o ./result/spiders.csv".split())
