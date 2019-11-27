# -*- coding: utf-8 -*-
import scrapy
import re
import json

from ..items import DoubanItem
from urllib.parse import urlencode, unquote
from scrapy.http import Request


class DoubanSpiderSpider(scrapy.Spider):
    name = 'douban_spider'
    start_urls = ['https://www.douban.com/j/search?']

    def start_requests(self):
        """
        构造初始请求
        :return:
        """
        params = {
            'q': 'python',  # 要搜索的信息填入这里
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
        for index, value in enumerate(json.loads(response.body)['items']):
            after_url = unquote(re.search('url=(http.+?)&', value).group(1))
            self.logger.info('Capture the url({}): {}'.format(index + 1, after_url))
            yield Request(url=after_url, callback=self.parse)

        # page_num = re.search(r'start=(\d+)', response.url).group(1)
        # page_num = 'start=' + str(int(page_num) + 20)
        # next_url = re.sub(r'start=\d+', page_num, response.url)
        # yield Request(url=next_url, callback=self.parse)

    def parse(self, response):
        """
        解析HTML，保存网页内容
        :param response:
        :return:
        """
        item = DoubanItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').extract_first()
        item['article'] = response.css('div#link-report div.note ::text').extract()
        yield item
