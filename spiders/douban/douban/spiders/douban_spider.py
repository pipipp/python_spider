# -*- coding: utf-8 -*-
import scrapy
import re
import json
import requests

from urllib.parse import unquote
from bs4 import BeautifulSoup
from ..items import DoubanItem


class DoubanSpiderSpider(scrapy.Spider):
    name = 'douban_spider'
    allowed_domains = ['https://www.douban.com/']
    start_urls = ['http://https://www.douban.com/j/search/']
    USER_AGENT = {
        'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                      'Chrome/78.0.3904.108 Safari/537.36'
    }

    def start_requests(self):
        search_info = 'python'
        start_value = 5
        search_url = 'https://www.douban.com/j/search?q={}&start={}&cat=1015'.format(search_info, start_value)
        yield scrapy.Request(search_url, headers=self.USER_AGENT)

    @staticmethod
    def get_further_url(response):
        for i in json.loads(response.body)['items']:
            url_info = re.search('a href="(.+?)"', i)
            if url_info:
                yield url_info.group(1)
            else:
                yield None

    def further_request(self, url):
        resp = requests.get(url=url, headers=self.USER_AGENT)

        item = DoubanItem()
        soup = BeautifulSoup(resp.text, 'lxml')

        note_id = re.search('note/(.+?)/&amp', unquote(url)).group(1)
        content = soup.find('div', id='note-{}'.format(note_id))
        item['title'] = content.find('div', class_='note-header note-header-container').find('h1').text
        item['article'] = content.find('div', id='note_{}_full'.format(note_id)).text
        item['url'] = url
        return item

    def parse(self, response):
        for each_url in self.get_further_url(response):
            if each_url:
                items = self.further_request(each_url)
                yield items

        # loops = 0
        # while True:
        #     loops += 1
        #     item = DoubanItem()
        #     for each_url in self.get_next_url(response):
        #         item['url'] = each_url
        #         yield item
        #         yield scrapy.Request(url=each_url, headers=self.headers, callback=self.next_request)
        #
        #     if loops <= 2:
        #         page_num = re.search(r'start=(\d+)', response.url).group(1)
        #         page_num = 'start=' + str(int(page_num) + 20)
        #         next_url = re.sub(r'start=\d+', page_num, response.url)
        #         yield scrapy.Request(url=next_url, headers=self.headers, callback=self.parse)
        #     else:
        #         break
