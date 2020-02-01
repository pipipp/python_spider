# -*- coding=utf8 -*-
from scrapy import cmdline


# TODO 运行bian_wallpaper爬虫
# cmdline.execute("scrapy crawl bian_wallpaper -o ./result/bian_wallpaper.json".split())

# TODO 运行lagou爬虫
cmdline.execute("scrapy crawl lagou -o ./result/spider.json".split())
# cmdline.execute("scrapy crawl lagou -o ./result/ai.json".split())
# cmdline.execute("scrapy crawl lagou -o ./result/big_data.json".split())
# cmdline.execute("scrapy crawl lagou -o ./result/web_development.json".split())
# cmdline.execute("scrapy crawl lagou -o ./result/background_development.json".split())
# cmdline.execute("scrapy crawl lagou -o ./result/automated_testing.json".split())
# cmdline.execute("scrapy crawl lagou -o ./result/software_test.json".split())
# cmdline.execute("scrapy crawl lagou -o ./result/hardware_test.json".split())
