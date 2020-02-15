# -*- coding:utf-8 -*-
import json
from urllib.parse import urlencode, quote, unquote

__author__ = 'Evan'


def read_json_data(file_name='json_file.json'):
    """
    读取JSON数据
    :param file_name: json文件名称
    :return:
    """
    with open(file_name, 'r', encoding='utf-8') as rf:
        # 将JSON对象转换为字典
        json_dict = json.loads(rf.read())

    print('Load json file:\n{}'.format(json_dict))
    print('Json data length: {}'.format(len(json_dict)))
    return json_dict


if __name__ == '__main__':
    # result = read_json_data(file_name=r'C:\Evan\my_programs\scrapy_code\trunk\public_crawlers\bian_wallpaper.json')

    url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E6%B7%B1%E5%9C%B3&needAddtionalResult=false'
    print(unquote(url))
