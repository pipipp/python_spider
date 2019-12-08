# -*- coding: utf-8 -*-
import scrapy
import time
import json

from ..items import LagouItem
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from urllib.parse import quote


class BianWallpaperSpider(scrapy.Spider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_url = 'https://www.lagou.com/jobs/list_{}?labelWords=&fromSearch=true&suginput='
    search_url = 'https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false'

    SEARCH_INFO = '爬虫开发工程师'  # 工作职位
    CITY_INFO = '深圳'  # 工作地点

    def start_requests(self):
        """
        构造初始请求
        :return:
        """
        self.start_url = self.start_url.format(quote(self.SEARCH_INFO))
        return [Request(url=self.start_url, callback=self.after_requests)]

    def get_cookies(self, response):
        """
        获取当前response的cookies
        :param response:
        :return: str(cookies)
        """
        # 因为请求头中cookies的类型为字符串，所以将字典转化为字符串类型
        cookies = ''
        for key, value in response.cookies.get_dict().items():
            cookies += (key + '=' + value + '; ')
        return cookies

    def after_requests(self, response):
        """
        获取初始界面的cookies，构建后续的AJAX请求
        :param response:
        :return:
        """
        cookies = self.get_cookies(response)

        for index in range(1, 2):
            headers = {
                'User-Agent': self.settings['USER_AGENT'],
                'Referer': self.start_url,
                'Cookie': cookies
            }
            data = {
                'first': 'false',
                'pn': index,
                'kd': '爬虫开发工程师',
            }
            self.search_url = self.search_url.format(quote(self.CITY_INFO))
            yield FormRequest(url=self.search_url, method='POST', headers=headers, formdata=data, callback=self.parse)

    def parse(self, response):
        """
        解析HTML
        :param response:
        :return:
        """
        result = json.loads(response.text)['content']['positionResult']['result']
        if result:
            print(result)
        else:
            pass
