# -*- coding=utf8 -*-
from scrapy import cmdline

# TODO 执行爬虫指令
cmdline.execute("scrapy crawl sample_spider -o sample.json".split())  # 执行爬虫并在当前目录下生成一个sample.json文件
