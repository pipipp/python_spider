"""
爬取代理网站的IP地址、端口号、协议类型保存到MongoDB数据库

目前已写代理网站：
西拉免费代理网站 --> get_xila_proxy_ip()

"""
# -*- coding:utf-8 -*-
import requests
import pymongo
import threading
import random
import time
import logging
from lxml import etree

__author__ = 'Evan'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ProxySpider(object):

    def __init__(self, config):
        self.config = config  # 全局配置文件
        self.proxy_table = self._config_mongodb()  # 初始化Mongodb数据库
        self.thread_pool = threading.Semaphore(value=self.config['THREAD_POOL_MAX'])  # 初始化线程池

    @staticmethod
    def _config_mongodb(host='localhost', port=27017):
        """
        初始化Mongodb数据库
        :param host: 主机名
        :param port: 端口
        :return: 返回集合句柄
        """
        client = pymongo.MongoClient(host=host, port=port)
        database = client['proxy_info']
        proxy_table = database['all_proxy_ip']
        return proxy_table

    @staticmethod
    def random_user_agent():
        """
        返回一个随机请求头
        :return:
        """
        ua_list = [
            # Chrome UA
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/73.0.3683.75 Safari/537.36',
            # IE UA
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            # Microsoft Edge UA
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
        ]
        return random.choice(ua_list)

    def get_xila_proxy_ip(self, page):
        """
        获取西拉网站代理IP
        :param page: 爬取页数
        :return:
        """
        with self.thread_pool:
            try:
                resp = requests.get(self.config['PROXY_URL'].format(page),
                                    headers={'User-Agent': self.random_user_agent()})
                # 如果请求失败，重试一次
                if resp.status_code != 200:
                    time.sleep(1)
                    resp = requests.get(self.config['PROXY_URL'].format(page),
                                        headers={'User-Agent': self.random_user_agent()})

                if resp.status_code == 200:
                    html = etree.HTML(resp.text)
                    # 获取当前页所有代理IP和端口号
                    ip_list = html.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[1]/text()')
                    # 获取当前页所有代理协议
                    protocol_list = html.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[2]/text()')
                    # 保存到MongoDB数据库
                    for ip, protocol in zip(ip_list, protocol_list):
                        self.proxy_table.insert_one({"ip": ip.split(':')[0],
                                                     "port": ip.split(':')[1],
                                                     "protocol": protocol})
                    logger.info('Page: {} --> Succeed'.format(page))
                else:
                    logger.info('Page: {} --> Failed, [Request error], status code: {}'.format(page, resp.status_code))
            except Exception as ex:
                logger.info('Page: {} --> Failed, [Exception error], error msg: {}'.format(page, ex))
