# -*- coding:utf-8 -*-
import requests
import threading
import re
import csv

from lxml import etree
from matplotlib import pyplot as plt

__author__ = 'Evan'


class Spider(object):

    def __init__(self, thread_pool_max_value=50):
        self.thread_pool = threading.Semaphore(value=thread_pool_max_value)  # 定义线程池
        self.all_country_info = []  # 保存所有的爬取信息
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/80.0.3987.132 Safari/537.36'
        })

    def get_all_country_url(self):
        url = 'http://www.sy72.com/world/'
        resp = self.session.get(url)
        resp.encoding = 'utf-8'
        result = []
        if resp.status_code == 200:
            html = etree.HTML(resp.text)
            for each_line in html.xpath('//*[@id="nav1"]/a'):
                country = each_line.xpath('li/dl/@name')[0]
                url = 'http://www.sy72.com' + each_line.xpath('@href')[0]
                result.append([country, url])
        if result:
            return result
        else:
            return []

    def get_each_country_info(self, country):
        with self.thread_pool:  # 控制线程进入数量
            url = country[1]
            resp = self.session.get(url)
            resp.encoding = 'utf-8'

            result = {}
            if resp.status_code == 200:
                html = etree.HTML(resp.text)
                for each_line in html.xpath('//*[@id="tableArea"]/div[@class="world"]/ul/li'):
                    title = each_line.xpath('a/@title')[0]
                    confirmed_number = re.search(r'(\d{4}/4/\d{1,2})确诊(\d+)', title)
                    if confirmed_number:
                        result[confirmed_number.groups()[0]] = confirmed_number.groups()[1]

            if result:
                count = 0
                for line in result.values():
                    count += int(line)
                result['汇总'] = count
                result['国家'] = country[0]
                self.all_country_info.append(result)
                print('[{}]爬取完成！'.format(country[0]))

    def start_crawl(self, all_country_url):
        threads = []
        print('--------------开始多线程爬取--------------')
        for each_url in all_country_url:  # 配置所有线程
            t = threading.Thread(target=self.get_each_country_info, args=(each_url,))
            threads.append(t)

        for thread in threads:  # 开启所有线程
            thread.start()

        for thread in threads:  # 主线程在此阻塞，等待所有线程结束
            thread.join()
        print('--------------全部爬取完毕--------------')

    @staticmethod
    def write_csv_data(write_info, file_name):
        all_day = ['2020/4/{}'.format(i) for i in range(1, 31)]
        csv_header = ['国家', '汇总']
        csv_header.extend(all_day)
        with open('{}.csv'.format(file_name), 'w', encoding='utf-8-sig', newline='') as wf:
            dict_write = csv.DictWriter(wf, fieldnames=csv_header)
            dict_write.writeheader()
            dict_write.writerows(write_info)
        print('全部数据写入完毕！')

    @staticmethod
    def draw_tendency_chart(data):
        # 处理中文乱码
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.figure(figsize=(10, 5), dpi=300)  # 提高画质
        plt.subplot(111)

        plt.xlabel('2020年4月份疫情确诊数量趋势图 <<全球排名前五国家>>（除中国）', size=10)  # 添加X轴标签
        x_label = ['{}'.format(i) for i in range(1, 31)]  # 设置X轴的刻度值
        plt.ylabel('确诊数量（人）', size=10)  # 添加Y轴标签
        plt.ylim([80000, 1250000])  # 设置Y轴的刻度范围

        # 获取排名前五国家的信息
        number_one = data[0]
        number_one_name = data[0]['国家']
        number_two = data[1]
        number_two_name = data[1]['国家']
        number_three = data[2]
        number_three_name = data[2]['国家']
        number_four = data[3]
        number_four_name = data[3]['国家']
        number_five = data[4]
        number_five_name = data[4]['国家']
        for i in [number_one, number_two, number_three, number_four, number_five]:  # 删除不要的字典
            del i['国家']
            del i['汇总']

        # 写入每天的确诊数量
        number_one_count = []
        number_two_count = []
        number_three_count = []
        number_four_count = []
        number_five_count = []
        for column in x_label:
            value = int(number_one['2020/4/' + column])
            number_one_count.append(value)
            plt.scatter('{:02d}'.format(int(column)), value, marker='D', s=20, color="#1E90FF")
        for column in x_label:
            value = int(number_two['2020/4/' + column])
            number_two_count.append(value)
            plt.scatter('{:02d}'.format(int(column)), int(number_two['2020/4/' + column]), marker='D', s=20, color="#FFA500")
        for column in x_label:
            value = int(number_three['2020/4/' + column])
            number_three_count.append(value)
            plt.scatter('{:02d}'.format(int(column)), int(number_three['2020/4/' + column]), marker='D', s=20, color="g")
        for column in x_label:
            value = int(number_four['2020/4/' + column])
            number_four_count.append(value)
            plt.scatter('{:02d}'.format(int(column)), int(number_four['2020/4/' + column]), marker='D', s=20, color="#00CED1")
        for column in x_label:
            value = int(number_five['2020/4/' + column])
            number_five_count.append(value)
            plt.scatter('{:02d}'.format(int(column)), int(number_five['2020/4/' + column]), marker='D', s=20, color="#DC143C")

        x_label_count = ['{:02d}'.format(int(i)) for i in x_label]
        plt.plot(x_label_count, number_one_count, linewidth=2, label=number_one_name, color="#1E90FF")
        plt.plot(x_label_count, number_two_count, linewidth=2, label=number_two_name, color='#FFA500')
        plt.plot(x_label_count, number_three_count, linewidth=2, label=number_three_name, color='g')
        plt.plot(x_label_count, number_four_count, linewidth=2, label=number_four_name, color='#00CED1')
        plt.plot(x_label_count, number_five_count, linewidth=2, label=number_five_name, color='#DC143C')

        # 显示曲线标注
        plt.legend(loc="right")
        plt.grid(linewidth=1.0, linestyle='--')
        plt.savefig('排名前五国家趋势图.jpg', bbox_inches='tight')  # 保存图片

    def main(self):
        # 获取所有国家的URL
        all_country_url = self.get_all_country_url()

        if all_country_url:
            # 多线程爬取所有国家的确诊数量
            self.start_crawl(all_country_url)
        else:
            print('没有爬取到任何的URL')

        if self.all_country_info:
            # 各个国家疫情确诊数量从大到小排序
            count = [i['汇总'] for i in self.all_country_info]
            count.sort(reverse=True)
            result = []
            for value in count:
                for each in self.all_country_info:
                    if value == each['汇总']:
                        result.append(each)
                        break
            # 写入到csv表格
            self.write_csv_data(write_info=result, file_name='全球疫情确诊数量汇总')
            # 画出数量排名前三的趋势图
            self.draw_tendency_chart(result)
        else:
            print('没有爬取到任何的国家信息！')


if __name__ == '__main__':
    spider = Spider(thread_pool_max_value=10)
    spider.main()
