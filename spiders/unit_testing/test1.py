import json


def read_json_data(file_name='json_file'):
    """
    读取JSON数据
    :param file_name: json文件名称
    :return:
    """
    with open('{}.json'.format(file_name), 'r', encoding='utf-8') as rf:
        # 将JSON对象转换为字典
        json_dict = json.loads(rf.read())
        return json_dict


if __name__ == '__main__':
    result = read_json_data(file_name=r'C:\Evan\my_program\moon\spiders\cralwer_items\douban\douban')
    print(result)
    print(len(result))
