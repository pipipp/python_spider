# -*- coding:utf-8 -*-
import re
import os
import time
import datetime
import json
import random
import requests
import pandas as pd

from pprint import pprint
from urllib.parse import quote, unquote
from collections import OrderedDict
from pymongo import MongoClient

__author__ = 'Evan'


class RequestTest(object):

    def __init__(self, source_url):
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
        return random.choice(ua_list)

    @staticmethod
    def login_mongodb(database_name, collection_name):
        """
        连接Mongodb客户端
        :param database_name: 数据库名称
        :param collection_name: 集合名称
        :return:
        """
        client = MongoClient(host='localhost', port=27017)
        database = client[database_name]
        collection = database[collection_name]
        print('Login mongodb successfully, database_name="{}", collection_name="{}"'.format(database_name,
                                                                                            collection_name))
        return database, collection

    @staticmethod
    def write_to_table(raw_data, columns, file_name='result.xls', to_file='excel'):
        """
        写入数据到csv or excel，默认excel
        Args：
            # 传入数据
            raw_data = {
                'sheet1_name': {
                    'name': ['Evan', 'Jane'],
                    'id': ['11', '22']
                },
                'sheet2_name': {
                    'name': ['Liu', 'Jang'],
                    'id': ['33', '44']
                }
            }
            # 指定列的顺序
            columns = ['id', 'name']

        :param raw_data: 写入的数据
        :param columns: 指定列的顺序
        :param file_name: 文件名称
        :param to_file: 生成的文件格式，csv or excel
        :return:
        """
        if to_file == 'csv':
            assert file_name.endswith('.csv'), f'请提供正确的csv文件名: {file_name}'

            for sheet_name, each_data in raw_data.items():
                new_file_name = f'{sheet_name}_{file_name}'
                pd_data = pd.DataFrame(each_data, columns=columns)
                pd_data.to_csv(new_file_name, mode='w', index=False)
                print(f'写入({new_file_name})成功')

        elif to_file == 'excel':
            assert re.findall('.xlsx?$', file_name), f'请提供正确的excel文件名: {file_name}'

            if len(raw_data) > 1:
                # 写入多页sheet到Excel
                writer = pd.ExcelWriter(file_name)
                for sheet_name, each_data in raw_data.items():
                    df = pd.DataFrame(each_data, columns=columns)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()
                writer.close()
            else:
                pd_data = pd.DataFrame(raw_data, columns=columns)
                pd_data.to_excel(file_name, index=False)
            print(f'写入({file_name})成功')

        else:
            raise ValueError(f'to_file值不在范围内: {to_file}，有效的to_file值: csv or excel')

    @ staticmethod
    def cookie_format_conversion(raw_cookies=''):
        """
        转换cookies为字典格式
        :param raw_cookies: 浏览器上保存下来的cookies
        :return:
        """
        cookies = {}
        for line in raw_cookies.split(';'):
            name, value = line.strip().split('=', 1)
            cookies[name] = value
        return cookies

    def main(self):
        params = {
            "uuttype": "73-100743%", "area": "pcbpm2", "location": "foxch",
            "passfail": "P,F,A",
            "start_time": "2020-09-08 00:00:00",
            "end_time": "2020-09-10 00:00:00",
            "dataset": "test_results", "database": None, "start": 0,
            "limit": "5000", "fttd": 0, "lttd": 0, "ftta": 0, "passedsampling": 0
        }

        headers = {
            'User-Agent': self.random_user_agent(),
            'csession': 'FE290CFF-06A7-4B8A-BCC1-8AE9AB12BCB4',
            '_csession': 'FE290CFF-06A7-4B8A-BCC1-8AE9AB12BCB4',
        }

        resp = requests.post(self.source_url, headers=headers, data=json.dumps(params))
        assert resp.status_code == 200, 'URL: {} -> 请求失败，status code: {}, history: {}'.format(resp.url,
                                                                                              resp.status_code,
                                                                                              resp.history)


if __name__ == '__main__':
    test = RequestTest(source_url='https://cesium.cisco.com/polarissvcs/central_data/multi_search')
    test.main()
