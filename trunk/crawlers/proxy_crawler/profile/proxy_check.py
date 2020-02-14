"""
代理IP验证，保存有效的代理IP
"""
# -*- coding:utf-8 -*-
import requests
import pymongo
import threading
import time

from proxy_crawler.profile.settings import proxy_check_settings
from proxy_crawler.profile.proxy_spider import ProxySpider

__author__ = 'Evan'


class ProxyCheck(ProxySpider):

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
        proxy_table = database['valid_proxy_ip']
        return proxy_table

    def proxy_ip_check(self):
        # TODO 待完成
        ip_list = ['10:11', '12:13']
        protocol_list = ['http', 'https']
        for ip, protocol in zip(ip_list, protocol_list):
            self.proxy_table.insert_one({"ip": ip.split(':')[0],
                                         "port": ip.split(':')[1],
                                         "protocol": protocol})
