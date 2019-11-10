# -*- coding: utf-8 -*-
import scrapy
from ..items import ExampleItem


class SampleSpider(scrapy.Spider):
    name = 'sample'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        item = ExampleItem()
        quotes = response.css('.quote')
        for quote in quotes:
            item['text'] = quote.css('.text::text').extract_first()
            item['author'] = quote.css('.author::text').extract_first()
            item['tags'] = quote.css('.tags .tag::text').extract()
            yield item

        next_url = response.css('.pager .next a::attr("href")').extract_first()
        url = response.urljoin(next_url)
        yield scrapy.Request(url=url, callback=self.parse)
