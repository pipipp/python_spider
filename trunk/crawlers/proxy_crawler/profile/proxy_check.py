"""
此类包含所有代理IP验证的方法
"""
# -*- coding:utf-8 -*-
import requests
import pymongo
import logging
import threading
import time

from proxy_crawler.profile.proxy_spider import ProxySpider

__author__ = 'Evan'
logger = logging.getLogger(__name__)


class ProxyCheck(ProxySpider):

    def proxy_ip_check(self):
        """
        检查所有代理IP，保存有效的代理IP到valid_proxy_ip集合
        :return:
        """
        table_data = self.all_proxy_ip_table.find()
        for i in table_data:
            print(i)

        # ip_list = ['10:11', '12:13']
        # protocol_list = ['http', 'https']
        # for ip, protocol in zip(ip_list, protocol_list):
        #     self.valid_proxy_ip.insert_one({"ip": ip.split(':')[0],
        #                                     "port": ip.split(':')[1],
        #                                     "protocol": protocol})
