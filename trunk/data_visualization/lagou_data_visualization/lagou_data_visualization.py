# -*- coding:utf-8 -*-
import json
import re
import os

from matplotlib import pyplot as plt


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
    绘柱形图
    :param str title: 图片标题
    :param list data_list: 数据列表
    :param tuple x_label: （X轴标签，X轴刻度标签）
    :param tuple y_label:（Y轴标签，Y轴刻度标签）
    :return:
    """
    # 处理中文乱码
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    item_range = range(len(data_list[0]))  # 计算所有数据的长度
    plt.title(title)  # 添加标题

    # 绘X轴刻度的第一个柱形图（宽度0.4）
    plt.bar(item_range, data_list[0], align='center',
            alpha=0.8, width=0.4)
    # 向右移动0.4 绘X轴刻度的第二个柱形图（宽度0.4）
    plt.bar([i+0.4 for i in item_range], data_list[1], align='center',
            color='y', alpha=0.8, width=0.4)

    plt.xlabel(x_label[0])  # 添加X轴标签
    plt.xticks([i+0.2 for i in item_range], x_label[1])  # 添加X轴刻度标签（向右移动0.2居中摆放）

    plt.ylabel(y_label[0])  # 添加Y轴标签
    plt.ylim(y_label[1])  # 设置Y轴的刻度范围

    # 为X轴刻度的第一个柱形图加数值标签
    for x, y in enumerate(data_list[0]):
        plt.text(x, y+100, '%s' % round(y, 1), ha='center')
    # 向右移动0.4 为X轴刻度的第二个柱形图添加数值标签
    for x, y in enumerate(data_list[1]):
        plt.text(x+0.4, y+100, '%s' % round(y, 1), ha='center')

    plt.show()  # 显示图形
    # plt.savefig('./software_jobs.jpg')  # 保存图片


def analysis(data, json_file_name):
    """
    分析职位薪资
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
        ('background_development', ('后台开发', '后台|后端')),
        ('spider', ('爬虫开发', '爬虫')),
        ('automated_testing', ('自动化测试', '自动化|测试')),
        ('software_test', ('软件测试', '软件|软件测试')),
        ('hardware_test', ('硬件测试', '硬件|测试'))
    ]
    for info in data:
        salary = re.sub('k|K', '000', info['salary'], re.I).split('-')  # 把"k"转换为"000"，并分解为一个元组（最低薪，最高薪）
        minimum = int(salary[0])  # 最低薪资
        maximum = int(salary[1])  # 最高薪资
        # calculate = int((int(salary[0]) + int(salary[1])) // len(salary))  # 计算薪资平均值

        for mapper in mapping:
            if mapper[0] in str(json_file_name).lower():
                condition = re.search(mapper[1][1], str(info['position_name']).lower())
                if condition:
                    matched.append([minimum, maximum])  # 保存薪资最小值和最大值
                    position_name = mapper[1][0]  # 保存职位名称
                    break
                else:
                    continue
        else:
            not_matched.append({info['position_name']: info['salary']})

    # if not_matched:
    #     print('JSON file - ({}), not matched length: {}, data: {}'.format(json_file_name,
    #                                                                       len(not_matched), not_matched))

    if matched:
        return [position_name + '\n({})'.format(len(matched)),
                sum(i[0] for i in matched)//len(matched), sum(i[1] for i in matched)//len(matched)]
    else:
        return None


def main(root_path):
    result = []
    for file in os.listdir(root_path):
        # print('Read the file: {}'.format(file))
        json_data = read_json_data(file_name=os.path.join(root_path, file))
        parsed = analysis(data=json_data, json_file_name=file)
        if parsed:
            result.append(parsed)

    if result:
        print('Final result length: {}\ndata: {}'.format(len(result), result))
        plot(title='2019年软件岗位薪资大比拼',
             data_list=[[item[1] for item in result], [item[2] for item in result]],
             x_label=('深圳地区', [item[0] for item in result]),
             y_label=('Salary', [5000, 40000]))


if __name__ == '__main__':
    path = r'./json_file'
    main(root_path=path)
