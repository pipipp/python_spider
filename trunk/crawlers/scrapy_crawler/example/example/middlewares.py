# -*- coding: utf-8 -*-

# Define here the models for your crawler middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random
from scrapy import signals


class RandomUserAgentMiddleware(object):
    """
    自定义类
    """
    def __init__(self):
        self.user_agents = [
            # Chrome UA
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/73.0.3683.75 Safari/537.36',
            # IE UA
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            # Microsoft Edge UA
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
        ]

    def process_request(self, request, spider):
        """
        生成一个随机请求头
        :param request:
        :param spider:
        :return:
        """
        request.headers['User-Agent'] = random.choice(self.user_agents)


class ExampleSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the crawler middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your crawler.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        """
        当 Response 被 Spider MiddleWare 处理时，会调用此方法
        :param response:
        :param spider:
        :return:
        """
        # Called for each response that goes through the crawler
        # middleware and into the crawler.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        """
        当 Spider 处理 Response 返回结果时，会调用此方法
        :param response:
        :param result:
        :param spider:
        :return:
        """
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a crawler or process_spider_input() method
        # (from other crawler middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        """
        以 Spider 启动的 Request 为参数被调用，执行的过程类似 process_spider_output()，必须返回 Request
        :param start_requests:
        :param spider:
        :return:
        """
        # Called with the start requests of the crawler, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ExampleDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your crawler.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        """
        在发送请求到 Download 之前调用此方法，可以修改User-Agent、处理重定向、设置代理、失败重试、设置Cookies等功能
        :param request:
        :param spider:
        :return: 如果返回的是一个 Request，会把它放到调度队列，等待被调度
        """
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        """
        在发送 Response 响应结果到 Spider 解析之前调用此方法，可以修改响应结果
        :param request:
        :param response:
        :param spider:
        :return: 如果返回的是一个 Request，会把它放到调度队列，等待被调度
        """
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        """
        当 Downloader 或 process_request() 方法抛出异常时，会调用此方法
        :param request:
        :param exception:
        :param spider:
        :return: 如果返回的是一个 Request，会把它放到调度队列，等待被调度
        """
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
