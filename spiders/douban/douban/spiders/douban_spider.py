# -*- coding: utf-8 -*-
import scrapy
import re
import json

from ..items import DoubanItem
from urllib.parse import unquote
from scrapy.http import Request


class DoubanSpiderSpider(scrapy.Spider):
    name = 'douban_spider'
    allowed_domains = ['https://www.douban.com/']
    start_urls = ['http://https://www.douban.com/j/search/']

    def start_requests(self):
        search_info = 'python'
        start_value = 5
        search_url = 'https://www.douban.com/j/search?q={}&start={}&cat=1015'.format(search_info, start_value)
        return [Request(url=search_url, callback=self.parse)]

    def parse(self, response):
        for i in json.loads(response.body)['items']:
            url_info = re.search('a href="(.+?)"', i)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/78.0.3904.108 Safari/537.36'
            }
            yield Request(url=url_info.group(1), headers=headers, callback=self.parse_each_url)

        # page_num = re.search(r'start=(\d+)', response.url).group(1)
        # page_num = 'start=' + str(int(page_num) + 20)
        # next_url = re.sub(r'start=\d+', page_num, response.url)
        # yield Request(url=next_url, callback=self.parse)

    def parse_each_url(self, response):
        note_id = re.search('note/(.+?)/&amp', unquote(response.url)).group(1)
        item = DoubanItem()
        item['title'] = response.xpath('//*[@id="note-{}"]/div[1]/h1/text()'.format(note_id)).extract_first()
        item['article'] = response.xpath('//*[@id="note_{}_full"]//text()'.format(note_id)).extract()
        item['url'] = response.url
        yield item
