import json


def read_json_data(file_name='json_file.json'):
    """
    读取JSON数据
    :param file_name: json文件名称
    :return:
    """
    with open(file_name, 'r', encoding='utf-8') as rf:
        # 将JSON对象转换为字典
        json_dict = json.loads(rf.read())
        return json_dict


if __name__ == '__main__':
    result = read_json_data(file_name=r'C:\Evan\my_programs\scrapy_code\spiders\public_crawlers\bian_wallpaper.json')
    print(result)
    print(len(result))
