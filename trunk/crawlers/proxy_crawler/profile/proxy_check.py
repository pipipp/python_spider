"""
此类包含所有代理IP验证的方法
"""
# -*- coding:utf-8 -*-
import requests
import logging
import time
from proxy_crawler.profile.proxy_spider import ProxySpider

__author__ = 'Evan'
logger = logging.getLogger(__name__)


class ProxyCheck(ProxySpider):

    def verify_proxy_ip(self, proxy_info, delete_invalid_proxy=False):
        """
        验证代理IP的有效性，保存有效的代理IP到MongoDB数据库（valid_proxy_ip集合）
        :param proxy_info: [dict] - 代理IP字典信息
        :param delete_invalid_proxy: [bool] - 如果设置为True，则删除无效的代理
        :return:
        """
        with self.thread_pool:
            data = {
                "ip": proxy_info['ip'],
                "port": proxy_info['port'],
                "protocol": proxy_info['protocol'],
                "speed": proxy_info['speed'],
                "score": proxy_info['score']
            }
            proxies = {
                'http': '{}:{}'.format(data['ip'], data['port']),
                'https': '{}:{}'.format(data['ip'], data['port'])
            }
            try:
                resp = requests.get(self.config['VALIDATE_URL'], proxies=proxies, timeout=5,
                                    headers={'User-Agent': self.random_user_agent()})
                # 如果请求失败，再试一次
                if resp.status_code != 200:
                    time.sleep(1)
                    resp = requests.get(self.config['VALIDATE_URL'], proxies=proxies, timeout=5,
                                        headers={'User-Agent': self.random_user_agent()})

                if resp.status_code == 200:
                    # 数据去重，保存有效代理到valid_proxy_ip集合
                    self.valid_proxy_ip_table.update_one(data, {"$set": data}, upsert=True)
                    logger.debug('The proxy - {} is valid'.format(proxy_info))
                else:
                    if delete_invalid_proxy:
                        # 删除无效代理
                        self.all_proxy_ip_table.delete_one(data)
                        self.valid_proxy_ip_table.delete_one(data)
            except Exception:
                if delete_invalid_proxy:
                    # 删除无响应代理
                    self.all_proxy_ip_table.delete_one(data)
                    self.valid_proxy_ip_table.delete_one(data)
