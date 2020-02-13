# -*- coding:utf-8 -*-
import time
import random
import requests
import xlwt

from pymongo import MongoClient
from scrapy.selector import Selector


class Crawler(object):
    database = None
    collection = None

    def __init__(self, source_url=''):
        self.source_url = source_url
        self.session = requests.Session()

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

    def login_mongodb(self, database_name, collection_name):
        """
        连接Mongodb客户端
        :param database_name: 数据库名称
        :param collection_name: 集合名称
        :return:
        """
        client = MongoClient(host='localhost', port=27017)
        self.database = client[database_name]
        self.collection = self.database[collection_name]
        print('Login mongodb successfully, database_name="{}", collection_name="{}"'.format(database_name,
                                                                                            collection_name))

    @staticmethod
    def write_excel_table(write_info, table_name='excel_example.xls', sheet_name='first_page'):
        """
        写入Excel表格
        :param write_info: 要写入Excel表格的数据
        :param table_name: Excel表格名称
        :param sheet_name: Excel页面名称
        :return:
        """
        ex_wt = xlwt.Workbook()
        sheet1 = ex_wt.add_sheet(sheet_name, cell_overwrite_ok=True)

        for row_index, each_row in enumerate(write_info):
            if isinstance(each_row, (list, tuple)):
                # 如果是列表或者元组，循环写入每条数据
                for column_index, each_column in enumerate(each_row):
                    sheet1.write(row_index, column_index, each_column)
            else:
                # 写入一条数据
                sheet1.write(row_index, 0, each_row)
        ex_wt.save(table_name)

    def main(self):
        resp = requests.get(self.source_url, headers={'User-Agent': self.random_user_agent()})
        if resp.status_code == 200:
            print(resp.text)

            # selector = Selector(resp)
        else:
            print('No data found!')
            print('url: {}'.format(resp.url))
            print('history: {}'.format(resp.history))


if __name__ == '__main__':
    url = 'https://www.baidu.com/'
    crawler = Crawler(source_url=url)
    crawler.main()
