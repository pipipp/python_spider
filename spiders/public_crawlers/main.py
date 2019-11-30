# -*- coding=utf8 -*-
from scrapy import cmdline


# 运行bian_wallpaper爬虫
cmdline.execute("scrapy crawl bian_wallpaper -o bian_wallpaper.json".split())
