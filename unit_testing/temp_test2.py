# -*- coding:utf-8 -*-
import requests
import threading
import re
import csv

from lxml import etree


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

    def draw_tendency_chart(self):
        pass

    def main(self):
        # 获取所有国家的URL
        all_country_url = self.get_all_country_url()

        if all_country_url:
            # 多线程爬取所有国家的确诊数量
            self.start_crawl(all_country_url)

        if self.all_country_info:
            # 写入到csv表格
            self.write_csv_data(write_info=self.all_country_info, file_name='全球疫情确诊数量汇总')

        # 画出数量排名前三的趋势图
        self.draw_tendency_chart()


if __name__ == '__main__':
    spider = Spider(thread_pool_max_value=10)
    spider.main()
