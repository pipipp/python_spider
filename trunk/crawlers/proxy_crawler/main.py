"""
代理爬虫和代理检查程序执行者
"""
# -*- coding:utf-8 -*-
import threading
import logging

from proxy_crawler.profile.proxy_spider import ProxySpider
from proxy_crawler.profile.proxy_check import ProxyCheck

from proxy_crawler.profile.settings import proxy_spider_settings
from proxy_crawler.profile.settings import proxy_check_settings

__author__ = 'Evan'
logger = logging.getLogger(__name__)


class ProxyHandle(object):

    def __init__(self):
        self.proxy_spider = ProxySpider(config=proxy_spider_settings)  # 实例化代理爬虫类
        self.proxy_check = ProxyCheck(config=proxy_check_settings)  # 实例化代理检查类

    def crawl_xila_proxy(self):
        """
        多线程爬取西拉网站代理IP
        :return:
        """
        threads = []
        logger.info('开始多线程爬取西拉网站代理IP...')
        for page in range(1, proxy_spider_settings['MAX_PAGE'] + 1):
            t = threading.Thread(target=self.proxy_spider.get_xila_proxy_ip, args=(page,))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        logger.info('西拉网站代理IP爬取完毕\n')

    def proxy_ip_check(self):
        """
        代理IP验证
        :return:
        """
        logger.info('开始验证代理IP...')
        self.proxy_check.proxy_ip_check()
        logger.info('代理IP验证完毕\n')


def main():
    proxy_handle = ProxyHandle()
    proxy_handle.crawl_xila_proxy()
    proxy_handle.proxy_ip_check()


if __name__ == '__main__':
    main()
