"""
爬取知乎网站的指定文章内容
"""
# -*- coding: utf-8 -*-
import scrapy
import re
import json

from ..items import ZhihuItem
from ..constants import LIMIT, SEARCH_INFO

from urllib.parse import urlencode
from scrapy.http import Request
from scrapy.selector import Selector

__author__ = 'Evan'


class ZhihuSpiderSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/search?']
    ARTICLE_COUNTS = 0

    def start_requests(self):
        """
        构造初始请求
        :return:
        """
        params = {
            'type': 'content',
            'q': SEARCH_INFO
        }
        start_url = self.start_urls[0] + urlencode(params)
        return [Request(url=start_url, callback=self.after_requests)]

    def after_requests(self, response):
        """
        获取初始界面的search_hash_id值，构建后续的AJAX请求
        :param response:
        :return:
        """
        search_hash_id = re.search(r'search_hash_id=(\w+?)&', response.text).group(1)
        params = {
            't': 'general',
            'q': SEARCH_INFO,
            'correction': 1,
            'offset': 20,  # 偏移参数（每次增加20）
            'limit': 20,
            'lc_idx': 27,  # 偏移参数（每次增加20）
            'show_all_topics': 0,
            'search_hash_id': search_hash_id,
            'vertical_info': '0,1,0,0,0,0,0,0,0,1',
        }
        after_url = 'https://www.zhihu.com/api/v4/search_v3?' + urlencode(params)
        return [Request(url=after_url, callback=self.parse)]

    def parse(self, response):
        """
        解析AJAX请求，保存JSON文本
        :param response:
        :return:
        """
        item = ZhihuItem()
        for info in json.loads(response.text)['data']:
            self.logger.info('ARTICLE_COUNTS is {}, LIMIT is {}'.format(self.ARTICLE_COUNTS, LIMIT))
            self.ARTICLE_COUNTS += 1
            if self.ARTICLE_COUNTS > LIMIT:
                break

            selector = Selector(text=info['highlight']['title'])
            item['title'] = ''.join(selector.xpath('//text()').extract())
            selector = Selector(text=info['highlight']['description'])
            item['description'] = ''.join(selector.xpath('//text()').extract())
            selector = Selector(text=info['object']['content'])
            item['article'] = '\n'.join(selector.xpath('//text()').extract())
            yield item

        if self.ARTICLE_COUNTS < LIMIT:
            offset = 'offset=' + str(int(re.search(r'offset=(\d+)', response.url).group(1)) + 20)
            lc_idx = 'lc_idx=' + str(int(re.search(r'lc_idx=(\d+)', response.url).group(1)) + 20)
            next_url = re.sub(r'lc_idx=\d+', lc_idx, re.sub(r'offset=\d+', offset, response.url))
            self.logger.info('Next url: {}'.format(next_url))
            yield Request(url=next_url, callback=self.parse)
