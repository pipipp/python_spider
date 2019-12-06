import json
from urllib.parse import unquote


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
    # result = read_json_data(file_name=r'C:\Evan\my_programs\scrapy_code\spiders\public_crawlers\bian_wallpaper.json')

    url = 'https://www.lagou.com/jobs/list_%E7%88%AC%E8%99%AB%E5%BC%80%E5%8F%91%E5%B7%A5%E7%A8%8B%E5%B8%88'
    print(unquote(url))
