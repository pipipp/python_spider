# -*- coding=utf8 -*-
from scrapy import cmdline


# TODO 运行bian_wallpaper爬虫
# cmdline.execute("scrapy crawl bian_wallpaper -o bian_wallpaper.json".split())

# TODO 运行lagou爬虫
cmdline.execute("scrapy crawl lagou -o lagou.json".split())
