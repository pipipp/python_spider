# -*- coding:utf-8 -*-
import json
import re
import os

import matplotlib.pyplot as plt


def read_json_data(file_name):
    """
    读取JSON文件
    :param file_name: JSON文件的路径名
    :return:
    """
    with open(file_name, 'r', encoding='utf-8') as rf:
        json_dict = json.loads(rf.read())
    return json_dict


def plot(title, data_list=[], x_label=(), y_label=()):
    """
    绘图
    :param str title: 图片标题
    :param list data_list: 数据列表
    :param tuple x_label: （X轴标签，X轴刻度标签）
    :param tuple y_label:（Y轴标签，Y轴刻度标签）
    :return:
    """
    # 处理中文乱码
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.title(title)  # 添加标题
    plt.bar(range(len(data_list)), data_list, align='center', color='steelblue', alpha=0.8)  # 绘柱形图

    plt.xlabel(x_label[0])  # 添加X轴标签
    plt.xticks(range(len(data_list)), x_label[1])  # 添加X轴刻度标签

    plt.ylabel(y_label[0])  # 添加Y轴标签
    plt.ylim(y_label[1])  # 设置Y轴的刻度范围

    # 为每个条形图添加数值标签
    for x, y in enumerate(data_list):
        plt.text(x, y+100, '%s' % round(y, 1), ha='center')

    plt.show()  # 显示图形
    # plt.savefig('./123.jpg')  # 保存图片


def analysis(data, json_file_name):
    """

    :param data: JSON数据
    :param json_file_name: JSON文件名
    :return:
    """
    matched = []
    not_matched = []
    position_name = 'None'

    # mapping = (JSON文件名，(职位名称, 正则匹配关键字))
    mapping = [
        ('ai', ('人工智能', '智能|机器学习|区块链')),
        ('big_data', ('大数据', '大数据')),
        ('web_development', ('Web开发', 'web')),
        ('background_development', ('后台开发', '后台')),
        ('spider', ('爬虫开发', '爬虫')),
        ('automated_testing', ('自动化测试', '自动化|测试')),
        ('software_test', ('软件测试', '软件|软件测试')),
        ('hardware_test', ('硬件测试', '硬件|测试'))
    ]
    for info in data:
        salary = re.sub('k|K', '000', info['salary'], re.I).split('-')  # 把"k"转换为"000"，并分解为一个元组（最低薪，最高薪）
        calculate = str(salary[0])  # 计算最低薪资
        # calculate = str(salary[1])  # 计算最高薪资
        # calculate = str((int(salary[0]) + int(salary[1])) // len(salary))  # 计算薪资平均值

        for mapper in mapping:
            if mapper[0] in str(json_file_name).lower():
                condition = re.search(mapper[1][1], str(info['position_name']).lower())
                if condition:
                    matched.append(calculate)
                    position_name = mapper[1][0]
                    break
                else:
                    continue
        else:
            not_matched.append({info['position_name']: info['salary']})

    # if not_matched:
    #     print('Not matched length: {}, data: {}'.format(len(not_matched), not_matched))
    if matched:
        return [position_name + '\n({})'.format(len(matched)), eval('+'.join(matched))//len(matched)]
    else:
        return None


def main():
    root_path = r'C:\Evan\my_programs\scrapy_code\trunk\data_visualization\lagou_data_visualization\json_file\\'
    result = []
    for file in os.listdir(root_path):
        # print('Read the file: {}'.format(file))
        json_data = read_json_data(file_name=os.path.join(root_path, file))
        parsed = analysis(data=json_data, json_file_name=file)
        if parsed:
            result.append(parsed)

    if result:
        print('Final result length: {}\ndata: {}'.format(len(result), result))
        plot(title='软件岗位最低薪资大比拼',
             data_list=[item[1] for item in result],
             x_label=('深圳地区', [item[0] for item in result]),
             y_label=('Salary', [5000, 25000]))


if __name__ == '__main__':
    main()
