# -*- coding:utf-8 -*-
import threading

from proxy_crawler.profile.proxy_spider import ProxySpider
from proxy_crawler.profile.proxy_check import ProxyCheck
from proxy_crawler.profile.settings import proxy_spider_settings
from proxy_crawler.profile.settings import proxy_check_settings

__author__ = 'Evan'


def crawl_xila_proxy():
    """
    多线程爬取西拉网站代理IP
    :return:
    """
    proxy_spider = ProxySpider(config=proxy_spider_settings)
    threads = []

    print('开始爬取西拉网站代理IP...')
    for page in range(1, proxy_spider_settings['MAX_PAGE'] + 1):
        t = threading.Thread(target=proxy_spider.get_xila_proxy_ip, args=(page,))
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    print('西拉网站代理IP爬取完毕')


def proxy_ip_check():
    """
    代理IP验证
    :return:
    """
    proxy_check = ProxyCheck(config=proxy_check_settings)
    print('开始验证代理IP...')
    proxy_check.proxy_ip_check()
    print('代理IP验证完毕')


def main():
    crawl_xila_proxy()
    proxy_ip_check()
    print('全部完成')


if __name__ == '__main__':
    main()
