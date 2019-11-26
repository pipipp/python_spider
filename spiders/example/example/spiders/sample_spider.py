"""Spider类基础属性和方法
属性:                       含义:
name                       爬虫名称，它必须是唯一的，用来启动爬虫
allowed_domains            允许爬取的域名，是可选配置
start_urls                 起始URL列表，当没有重写start_requests()方法时，默认使用这个列表
custom_settings            它是一个字典，专属与本Spider的配置，此设置会覆盖项目全局的设置，必须在初始化前被更新，必须定义成类变量
settings                   它是一个Settings对象，我们可以直接获取项目的全局设置变量

方法：                      含义:
start_requests()           生成初始请求，必须返回一个可迭代对象，默认使用start_urls里的URL和GET请求，如需使用POST需要重写此方法
parse()                    当Response没有指定回调函数时，该方法会默认被调用，该函数必须要返回一个包含Request或Item的可迭代对象
closed()                   当Spider关闭时，该方法会被调用，可以在这里定义释放资源的一些操作或其他收尾操作
"""
# -*- coding: utf-8 -*-
import scrapy

from ..items import ExampleItem
from scrapy.http import Request, FormRequest


class SampleSpider(scrapy.Spider):
    name = 'sample_spider'  # 项目名称，具有唯一性不能同名
    allowed_domains = ['quotes.toscrape.com']  # 允许的domain range
    start_urls = ['http://quotes.toscrape.com/']  # 起始URL

    def parse(self, response):
        """
        该函数必须要返回一个包含 Request 或 Item 的可迭代对象
        :param response:
        :return:
        """
        # json.loads(response.body)  # 获取AJAX数据
        # response.xpath('//a/text()')  # 使用xpath选择器解析，返回一个列表
        # response.xpath('//a/text()').re('Name:\s(.*)')  # 使用xpath选择器 + 正则表达式解析，返回正则匹配的分组列表
        # response.xpath('//a/text()').re_first('Name:\s(.*)')  # 使用xpath选择器 + 正则表达式解析，返回正则匹配的第一个结果
        quotes = response.css('.quote')  # 使用css选择器，返回一个列表，包含"class='quote'"的所有结果

        item = ExampleItem()
        for quote in quotes:
            item['text'] = quote.css('.text::text').extract_first()  # 返回匹配到的第一个文本字符串
            item['author'] = quote.css('.author::text').extract_first()  # 返回匹配到的第一个文本字符串
            item['tags'] = quote.css('.tags .tag::text').extract()  # 返回一个列表，包含匹配到的所有文本字符串
            yield item

        next_url = response.css('.pager .next a::attr("href")').extract_first()  # 返回下一页的URL
        url = response.urljoin(next_url)  # 拼接成一个绝对的URL
        yield Request(url=url, callback=self.parse)  # 设置回调函数，循环检索每一页
