"""
此类包含所有代理IP爬取的方法

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
        self.all_proxy_ip_table, self.valid_proxy_ip_table = self.config_mongodb()  # 初始化Mongodb数据库
        self.thread_pool = threading.Semaphore(value=self.config['THREAD_POOL_MAX'])  # 初始化线程池

    @staticmethod
    def config_mongodb(host='localhost', port=27017):
        """
        初始化Mongodb数据库
        :param host: 主机名
        :param port: 端口号
        :return: 返回两个集合句柄（所有代理IP集合，有效代理IP集合）
        """
        client = pymongo.MongoClient(host=host, port=port)
        database = client['proxy_info']
        all_proxy_ip_table = database['all_proxy_ip']
        valid_proxy_ip_table = database['valid_proxy_ip']
        return all_proxy_ip_table, valid_proxy_ip_table

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
        URL - http://www.xiladaili.com/https/
        爬取西拉代理网站的IP地址、端口号、协议类型、代理IP响应速度、代理IP得分保存到MongoDB数据库（all_proxy_ip集合）
        :param page: 爬取页数
        :return:
        """
        with self.thread_pool:
            try:
                resp = requests.get(self.config['PROXY_URL'].format(page),
                                    headers={'User-Agent': self.random_user_agent()})
                # 如果请求失败，再试一次
                if resp.status_code != 200:
                    time.sleep(1)
                    resp = requests.get(self.config['PROXY_URL'].format(page),
                                        headers={'User-Agent': self.random_user_agent()})

                if resp.status_code == 200:
                    html = etree.HTML(resp.text)
                    # 获取所有代理IP和端口号
                    ip_list = html.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[1]/text()')
                    # 获取所有代理协议
                    protocol_list = html.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[2]/text()')
                    # 获取所有代理IP响应速度
                    speed_list = html.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[5]/text()')
                    # 获取所有代理IP得分
                    score_list = html.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[8]/text()')
                    for ip, protocol, speed, score in zip(ip_list, protocol_list, speed_list, score_list):
                        # 过滤掉响应速度大于3或者代理得分小于10000的IP
                        if float(speed) > 3.0 or int(score) < 10000:
                            continue
                        data = {
                            "ip": ip.split(':')[0],
                            "port": ip.split(':')[1],
                            "protocol": protocol,
                            "speed": speed,
                            "score": score
                        }
                        # 数据去重，保存到all_proxy_ip集合
                        self.all_proxy_ip_table.update_one(data, {"$set": data}, upsert=True)
                    logger.debug('Page: {} --> The request is successful'.format(page))
                else:
                    logger.debug('Page: {} --> Failed, [Request error], status code: {}'.format(page, resp.status_code))
            except Exception as ex:
                logger.debug('Page: {} --> Failed, [Exception error], error msg: {}'.format(page, ex))
