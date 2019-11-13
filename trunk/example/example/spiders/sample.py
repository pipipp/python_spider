# -*- coding: utf-8 -*-
import scrapy
from ..items import ExampleItem


class SampleSpider(scrapy.Spider):
    name = 'sample'  # 项目名称，具有唯一性不能同名
    allowed_domains = ['quotes.toscrape.com']  # 允许的domain range
    start_urls = ['http://quotes.toscrape.com/']  # 起始URL

    def parse(self, response):
        item = ExampleItem()
        quotes = response.css('.quote')  # 使用css选择器，返回一个列表，包含"class='quote'"的所有结果
        for quote in quotes:
            item['text'] = quote.css('.text::text').extract_first()  # 返回匹配到的第一个文本字符串
            item['author'] = quote.css('.author::text').extract_first()  # 返回匹配到的第一个文本字符串
            item['tags'] = quote.css('.tags .tag::text').extract()  # 返回一个列表，包含匹配到的所有文本字符串
            yield item

        next_url = response.css('.pager .next a::attr("href")').extract_first()  # 返回下一页的URL
        url = response.urljoin(next_url)  # 拼接成一个绝对的URL
        yield scrapy.Request(url=url, callback=self.parse)  # 循环检索每一页，直到最后一页
