# -*- coding:utf-8 -*-
import re
import random
import requests
import xlwt

from bs4 import BeautifulSoup
from urllib.parse import unquote


class Crawler(object):

    def __init__(self, url=''):
        self.source_url = url

    @staticmethod
    def random_user_agent():
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

    @staticmethod
    def write_excel_table(write_info, table_name='excel_example.xls'):
        """
        写入Excel表格
        :param write_info: 要写入Excel表格的数据
        :param table_name: Excel表格名称
        :return:
        """
        ex_wt = xlwt.Workbook()

        for i in write_info:
            title = i[0]
            body = i[1]
            sheet1 = ex_wt.add_sheet(title, cell_overwrite_ok=True)

            index = 0
            for row_index, each_row in enumerate(body.split('。')):
                condetion1 = each_row.count(' ')
                condetion2 = each_row.count('，')
                condetion3 = each_row.count('！')
                if condetion1 > condetion2:
                    if condetion1 > condetion3:
                        each_info = each_row.split()
                    else:
                        each_info = each_row.split('！')
                else:
                    if condetion2 > condetion3:
                        each_info = each_row.split('，')
                    else:
                        each_info = each_row.split('！')

                for each_data in each_info:
                    sheet1.write(index, 0, each_data)
                    index += 1
        ex_wt.save(table_name)

    def parse(self, parse_url, note_id):
        """
        解析网页数据，抓取title和body
        :param parse_url: 请求的URL
        :param note_id: 解析的note_id
        :return: [title, body] or []
        """
        resp = requests.get(parse_url, headers={'User-Agent': self.random_user_agent()})
        result = []
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'lxml')
            content = soup.find('div', id='note-{}'.format(note_id))
            title = content.find('div', class_='note-header note-header-container').find('h1').text
            body = content.find('div', id='note_{}_full'.format(note_id)).text
            for info in [title, body]:
                result.append(str(info).strip())
        return result

    def start_search(self, params):
        """
        请求AJAX数据，抓取所有页的URL
        :param params: 请求参数
        :return: [totalURL] or []
        """
        resp = requests.get(self.source_url, headers={'User-Agent': self.random_user_agent()}, params=params)
        result = []
        if resp.status_code == 200:
            for i in resp.json()['items']:
                if params['q'] in str(i):
                    url_info = re.search('a href="(.+?)"', i)
                    if url_info:
                        result.append(url_info.group(1))
        return result

    def run(self):
        loops = 1  # 循环次数
        start_increment = 5  # 参数增量
        break_limit = 50  # 抓取结果总数
        final_list = []  # 抓取结果列表

        while True:
            print('loops: {}'.format(loops))
            print('final_list length: {}'.format(len(final_list)))

            # TODO This is the only exit
            if len(final_list) >= break_limit:
                self.write_excel_table(write_info=final_list, table_name='DouBan.xls')
                print('Write excel table successful')
                break

            # TODO Request params
            param = {
                'q': 'python',  # 要搜索的信息填入这里
                'start': start_increment,  # 偏移参数（每次增加20）
                'cat': 1015
            }
            # 获取所有页面的URL
            url_list = self.start_search(params=param)
            if url_list:
                print('Found url list length: {}'.format(len(url_list)))

                parsed_info = []
                for url in url_list:
                    note = re.search('note/(.+?)/&amp', unquote(url))
                    if note:
                        # 解析所有URL
                        contents = self.parse(parse_url=url, note_id=note.group(1))
                        if contents:
                            parsed_info.append(contents)

                print('parsed_info length: {}'.format(len(parsed_info)))
                final_list.extend(parsed_info)  # 保存所有URL解析结果
                print('url list pares done')

            start_increment += 20  # AJAX数据每次增加20
            loops += 1
            print('current start_increment value: {}\n----------------------------\n'.format(start_increment))


if __name__ == '__main__':
    crawler = Crawler(url='https://www.douban.com/j/search')
    crawler.run()
