"""
爬取西拉免费代理网站的IP地址，保存有效的代理IP到MongoDB数据库
"""
import requests
import pymongo
import threading
import random
import time

from lxml import etree


class SpiderAgency(object):

    def __init__(self):
        self.agency_url = 'http://www.xiladaili.com/gaoni/{}/'  # 西拉免费代理网址
        self.validate_url = 'http://icanhazip.com'  # 代理IP验证网址（Get请求会返回请求的IP地址）
        self.all_agency_ip, self.valid_agency_ip = self._config_mongodb()
        self.thread_pool = None

    @staticmethod
    def _config_mongodb(host='localhost', port=27017):
        """
        初始化Mongodb数据库
        :param host: 主机名
        :param port: 端口
        :return: 返回两个集合句柄（所有代理IP表，有效代理IP表）
        """
        client = pymongo.MongoClient(host=host, port=port)
        database = client['agency_ip']
        all_agency_ip = database['all_agency_ip']
        valid_agency_ip = database['valid_agency_ip']
        return all_agency_ip, valid_agency_ip

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
        ua = random.choice(ua_list)
        return ua

    def get_maximum_page_value(self):
        """
        获取西拉免费代理网站的最大页面值
        :return:
        """
        resp = requests.get(self.agency_url.format('1'), headers={'User-Agent': self.random_user_agent()})
        if resp.status_code == 200:
            html = etree.HTML(resp.text)
            total_pages = html.xpath('/html/body/div/div[3]/nav/ul/li[15]/a/@href')[0].split('/')[-2]
            return int(total_pages)
        else:
            raise ValueError('Agency URL error, the maximum page value was not found')

    def get_agency_ip(self, page):
        """
        获取西拉代理网站IP
        :param page: 爬取页数
        :return:
        """
        with self.thread_pool:
            resp = requests.get(self.agency_url.format(page), headers={'User-Agent': self.random_user_agent()})
            if resp.status_code == 200:
                html = etree.HTML(resp.text)
                # 获取当前页所有代理ip
                ip_list = html.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[1]/text()')
                # 获取当前页所有代理协议
                protocol_list = html.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[2]/text()')
                # 保存到MongoDB数据库
                for ip, protocol in zip(ip_list, protocol_list):
                    self.all_agency_ip.insert_one({"ip": ip.split(':')[0],
                                                   "port": ip.split(':')[1],
                                                   "protocol": protocol})
                print('End of page {} crawl'.format(page))
            else:
                print('Agency URL error, current page: {}, status code: {}'
                      .format(page, resp.status_code, resp.history))
            time.sleep(2)

    def main(self):
        # total_pages = self.get_maximum_page_value()
        # print('Total pages: {}'.format(total_pages))

        self.thread_pool = threading.Semaphore(value=3)  # 设置线程池为3
        threads = []

        for page in range(1, 10 + 1):  # 配置所有线程
            t = threading.Thread(target=self.get_agency_ip, args=(page,))
            threads.append(t)

        for thread in threads:  # 开启所有线程
            thread.start()

        for thread in threads:  # 主线程在此阻塞，等待所有线程结束
            thread.join()


if __name__ == '__main__':
    spider_agency = SpiderAgency()
    spider_agency.main()
