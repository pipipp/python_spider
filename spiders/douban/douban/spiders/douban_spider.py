# -*- coding: utf-8 -*-
import scrapy
import re
import json

from ..items import DoubanItem
from urllib.parse import urlencode, unquote
from scrapy.http import Request


class DoubanSpiderSpider(scrapy.Spider):
    name = 'douban_spider'
    allowed_domains = ['https://www.douban.com/']
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
        获取响应结果里的每一页URL
        :param response:
        :return:
        """
        for index, value in enumerate(json.loads(response.body)['items']):
            after_url = re.search('a href="(.+?)"', value).group(1)
            self.logger.info('Capture URL({}): {}'.format(index + 1, after_url))

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
        note_id = re.search('note/(.+?)/&amp', unquote(response.url)).group(1)
        self.logger.info('note_id: {}'.format(note_id))

        item = DoubanItem()
        item['title'] = response.xpath('//*[@id="note-{}"]/div[1]/h1/text()'.format(note_id)).extract_first()
        item['article'] = response.xpath('//*[@id="note_{}_full"]//text()'.format(note_id)).extract()
        item['url'] = response.url
        yield item
