# -*- coding=utf8 -*-
from scrapy import cmdline

# 运行zhihu_spider爬虫
cmdline.execute("scrapy crawl zhihu_spider -o ./result/1-contents.json".split())
