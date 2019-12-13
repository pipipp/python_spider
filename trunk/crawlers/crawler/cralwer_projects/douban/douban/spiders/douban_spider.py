"""
此爬虫是爬取豆瓣网上的信息
在下面的SEARCH_INFO参数里面填入要搜索的信息，以及在LIMIT参数里面填入要抓取的文章数量运行即可
"""
# -*- coding: utf-8 -*-
import scrapy
import re
import json

from ..items import DoubanItem
from urllib.parse import urlencode, unquote
from scrapy.http import Request


class DoubanSpiderSpider(scrapy.Spider):
    name = 'douban_spider'
    allowed_domains = ["www.douban.com"]
    start_urls = ['https://www.douban.com/j/search?']

    ARTICLE_COUNTS = 0  # 当前文章数量总数
    LIMIT = 50  # 文章数量获取限制
    SEARCH_INFO = 'python'  # 要搜索的关键字填入这里

    def start_requests(self):
        """
        构造初始请求
        :return:
        """
        params = {
            'q': self.SEARCH_INFO,
            'start': 5,  # 偏移参数（每次增加20）
            'cat': 1015
        }
        # 'https://www.douban.com/j/search?q=python&start=5&cat=1015'
        start_url = self.start_urls[0] + urlencode(params)
        return [Request(url=start_url, callback=self.get_each_url)]

    def get_each_url(self, response):
        """
        获取每一篇文章的URL
        :param response:
        :return:
        """
        if json.loads(response.body).get('items', None):
            for index, value in enumerate(json.loads(response.body)['items']):
                self.logger.info('ARTICLE_COUNTS is {}, LIMIT is {}'.format(self.ARTICLE_COUNTS, self.LIMIT))
                self.ARTICLE_COUNTS += 1
                if self.ARTICLE_COUNTS > self.LIMIT:
                    break

                after_url = unquote(re.search('url=(http.+?)&', value).group(1))
                yield Request(url=after_url, callback=self.parse)
        else:
            self.logger.warning('No data was found under this url ({}), continue to crawl'.format(response.url))

        if self.ARTICLE_COUNTS < self.LIMIT:
            page_num = re.search(r'start=(\d+)', response.url).group(1)
            page_num = 'start=' + str(int(page_num) + 20)
            next_url = re.sub(r'start=\d+', page_num, response.url)
            self.logger.info('Next url: {}'.format(next_url))
            yield Request(url=next_url, callback=self.get_each_url)

    def parse(self, response):
        """
        解析HTML，保存网页内容
        :param response:
        :return:
        """
        item = DoubanItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').extract_first()
        item['article'] = '\n'.join(response.css('div#link-report div.note ::text').extract())
        yield item
