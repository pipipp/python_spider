"""
爬取同花顺财经网站的证券数据
抓取龙虎榜历史数据和详细数据写入到JSON文本
"""
# -*- coding:utf-8 -*-
import requests
import json
import os
from lxml import etree

__author__ = 'Evan'


class Crawler(object):

    def __init__(self, keyword=''):
        self.resource_url = 'http://data.10jqka.com.cn/ifmarket/lhbhistory/orgcode/{}/field/ENDDATE/order/desc/page/{}/'
        self.stock_link_url = 'http://data.10jqka.com.cn/ifmarket/getnewlh/code'
        self.keyword = keyword  # 股票查询关键字
        self.stock_history_data = {}  # 保存所有的历史数据
        self.stock_detail_data = {}  # 保存所有的详细数据
        self.headers = {
            'Host': 'data.10jqka.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }

    @staticmethod
    def write_json_data(write_info, file_name='json_file'):
        """
        写入JSON文本
        :param write_info: 要写入的字典
        :param file_name: 文件名称
        :return:
        """
        with open('{}.json'.format(file_name), 'w', encoding='utf-8') as wf:
            wf.write(json.dumps(write_info, ensure_ascii=False, indent=2) + '\n')

    @staticmethod
    def parse_history_html(response):
        """
        解析营业部上榜历史数据的网页内容
        :param response:
        :return:
        """
        result = []
        html = etree.HTML(response)
        body = html.xpath('/html/body/table/tbody/*')
        for each_line in body:
            stock_info = dict()
            stock_info['股票简称'] = each_line.xpath('td/a/text()')[0]
            stock_info['股票链接'] = each_line.xpath('td/a/@href')[0]
            stock_info['上榜日期'] = each_line.xpath('td/text()')[0]
            stock_info['上榜原因'] = each_line.xpath('td/text()')[3]
            stock_info['涨跌幅(%)'] = each_line.xpath('td/text()')[4]
            stock_info['买入额（万）'] = each_line.xpath('td/text()')[5]
            stock_info['卖出额（万）'] = each_line.xpath('td/text()')[6]
            stock_info['买卖净额（万）'] = each_line.xpath('td/text()')[7]
            stock_info['所属板块'] = each_line.xpath('td/text()')[8]
            stock_info['页数'] = html.xpath('/html/body/div/span/text()')[0]
            result.append(stock_info)
        return result

    def get_historical_data(self):
        """
        获取营业部实例分析板块下的营业部上榜历史数据
        :return:
        """
        print('正在获取第1页历史数据...')
        resp = requests.get(self.resource_url.format(self.keyword, 1), headers=self.headers)
        if resp.status_code == 200:
            stock_info = self.parse_history_html(response=resp.text)
            if stock_info:
                self.stock_history_data['第1页'] = stock_info
                print('第1页历史数据收集完毕')

                # 获取第一页后续的页面数据
                max_page = stock_info[0]['页数'].split('/')[-1]
                print('一共有{}页'.format(max_page))
                for page in range(2, int(max_page) + 1):
                    print('正在获取第{}页历史数据...'.format(page))
                    resp = requests.get(self.resource_url.format(self.keyword, page), headers=self.headers)
                    if resp.status_code == 200:
                        stock_info = self.parse_history_html(response=resp.text)
                        if stock_info:
                            self.stock_history_data['第{}页'.format(page)] = stock_info
                            print('第{}页历史数据收集完毕'.format(page))
                        else:
                            print('第{}页没有找到任何的历史数据！！！'.format(page))
                    else:
                        print('第{}页URL访问失败！！！'.format(page))
        else:
            print('URL访问失败')

    @staticmethod
    def parse_stock_detail_html(response):
        """
        解析股票详情的网页内容
        :param response:
        :return:
        """
        result = []
        html = etree.HTML(response)
        # 添加股票名称和交易日期
        result.extend([i.strip() for i in html.xpath('/html/body/div//text()') if i.strip()])
        # 添加股票交易详细信息
        body = html.xpath('/html/body/table/tbody/*')
        for index, each_line in enumerate(body):
            if index == 0 or index == 6 or index == 12:
                result.append(''.join([i.strip() for i in each_line.xpath('td//text()') if i.strip()]))
            else:
                stock_info = dict()
                text_info = [i.strip() for i in each_line.xpath('td//text()') if i.strip()]
                stock_info['排序'] = text_info[0]
                stock_info['营业部名称'] = text_info[1]
                stock_info['买入金额/万'] = text_info[2]
                stock_info['买入占总成交比例'] = text_info[3]
                stock_info['卖出金额/万'] = text_info[4]
                stock_info['卖出占总成交比例'] = text_info[5]
                stock_info['净额/万'] = text_info[6]
                result.append(stock_info)
        return result

    def get_stock_detail(self):
        """
        获取股票的龙虎榜详细数据
        :return:
        """
        for page, data in self.stock_history_data.items():
            result = []
            print('正在获取{}股票详细数据...'.format(page))
            for each_line in data:
                resp = requests.get(self.stock_link_url + each_line['股票链接'].split('code')[-1], headers=self.headers)
                if resp.status_code == 200:
                    stock_detail_info = self.parse_stock_detail_html(response=resp.text)
                    if stock_detail_info:
                        result.append(stock_detail_info)
                    else:
                        print('{}没有找到任何的股票详细数据！！！'.format(page))
                else:
                    print('{}股票详细URL访问失败！！！'.format(page))

            if result:
                self.stock_detail_data[page] = result
                print('{}股票详细数据收集完毕'.format(page))
            else:
                print('第{}页没有找到任何的股票详细数据！！！'.format(page))

    def save_data(self):
        """
        保存数据到JSON文本
        :return:
        """
        if not os.path.isdir('stock_result'):
            os.mkdir('stock_result')
        self.write_json_data(write_info=self.stock_history_data, file_name='./stock_result/stock_history_data')
        self.write_json_data(write_info=self.stock_detail_data, file_name='./stock_result/stock_detail_data')
        print('全部数据写入完毕，爬取结束！')

    def main(self):
        # 获取营业部实例分析板块下的营业部上榜历史数据
        self.get_historical_data()
        # 获取股票的龙虎榜详细数据
        self.get_stock_detail()
        # 保存所有的爬取结果到JSON文本
        self.save_data()


if __name__ == '__main__':
    crawler = Crawler(keyword='GTJAZQGFYXGSSHXZLZQYYB')
    crawler.main()
