# -*- coding: utf-8 -*-
import scrapy
import re
import json

from ..items import ZhihuItem
from urllib.parse import urlencode
from scrapy.http import Request


class ZhihuSpiderSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/search?']

    ARTICLE_COUNTS = 0  # 当前文章数量总数
    LIMIT = 50  # 文章数量获取限制
    SEARCH_INFO = 'python'  # 要搜索的关键字填入这里

    def start_requests(self):
        """
        构造初始请求
        :return:
        """
        params = {
            'type': 'content',
            'q': self.SEARCH_INFO
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
            'q': self.SEARCH_INFO,
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
        解析AJAX请求，保存JSON数据
        :param response:
        :return:
        """
        self.logger.info('response: {}'.format(json.loads(response.text)['data']))

        item = ZhihuItem()
        for each_info in json.loads(response.text)['data']:
            self.logger.info('title: {}'.format(each_info['object']['title']))
            self.logger.info('content: {}'.format(each_info['object']['content']))
            # item['url'] = response.url
            # item['title'] = response.css('title::text').extract_first()
            # item['article'] = response.css('div#link-report div.note ::text').extract()
            # yield item
