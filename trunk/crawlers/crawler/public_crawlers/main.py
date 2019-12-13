# -*- coding=utf8 -*-
from scrapy import cmdline


# TODO 运行bian_wallpaper爬虫
# cmdline.execute("scrapy crawl bian_wallpaper -o bian_wallpaper.json".split())

# TODO 运行lagou爬虫
cmdline.execute("scrapy crawl lagou -o spider.json".split())
# cmdline.execute("scrapy crawl lagou -o ai.json".split())
# cmdline.execute("scrapy crawl lagou -o big_data.json".split())
# cmdline.execute("scrapy crawl lagou -o web_development.json".split())
# cmdline.execute("scrapy crawl lagou -o background_development.json".split())
# cmdline.execute("scrapy crawl lagou -o automated_testing.json".split())
# cmdline.execute("scrapy crawl lagou -o software_test.json".split())
# cmdline.execute("scrapy crawl lagou -o hardware_test.json".split())
