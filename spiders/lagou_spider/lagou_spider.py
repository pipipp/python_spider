"""
拉勾网爬虫 + 数据分析
1> 爬取指定职位的所有公司招聘信息
公司名称      职位名称      薪水          学历要求    工作地址      工作年限      工作性质      职位诱惑
职位描述      城市          区域          公司人数    公司标签      行业领域      融资阶段
2> 生成所有公司的招聘详情数据表（excel）
3> 绘制薪水比例饼图，分析行业薪资标准
4> 绘制词云图，分析行业现状（薪水、工作地址、工作年限、职位诱惑、职位描述、公司人数、公司标签、行业领域）
"""
# -*- coding:utf-8 -*-
import re
import os
import time
import random
import logging
import requests
import threading
import jieba
import pandas as pd

from wordcloud import WordCloud
from bs4 import BeautifulSoup
from urllib.parse import quote
from matplotlib import pyplot as plt

__author__ = 'Evan'

# 配置日志模块
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class LagouSpider(object):

    def __init__(self, search_info, thread_pool_max=5):
        # 拉勾网首页URL
        self.root_url = 'https://www.lagou.com/jobs/list_{}?labelWords=&fromSearch=true&suginput='
        # 资源接口
        self.search_url = 'https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false'.format(quote(search_info['city']))
        # 资源详情页
        self.detail_url = 'https://www.lagou.com/jobs/{}.html?show={}'
        # 初始化
        self.save_folder = None
        self.search_info = search_info  # 搜索信息
        self.required_parameter = {}  # 请求每一页的特殊参数
        self.company_result = {}  # 所有页的公司信息爬取结果
        self.detail_result = {}  # 所有公司的详情信息爬取结果
        self.item = {}  # 数据规整结果
        self.time_sleep = [3, 5, 7]  # 等待时间（加延时）
        self.thread_pool = threading.Semaphore(value=thread_pool_max)  # 初始化线程池
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
        })
        # 处理绘图中文乱码
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False

    def initial_request(self, position):
        """
        构造初始请求，保存拉钩网首页cookies和第一页信息
        :param position: 爬取职位
        :return:
        """
        root_url = self.root_url.format(quote(position))
        self.session.get(root_url)
        # 构造资源接口的初始请求，保存总页数和sid
        self.session.headers.update({'Referer': root_url})
        data = {
            'first': 'true',
            'pn': 1,
            'kd': position
        }
        for i in range(5):
            try:
                resp = self.session.post(self.search_url, data=data)
                if resp.status_code == 200:
                    logger.info('当前爬取职位：( {} ) 最大页数：[{}]'.format(position, resp.json()['content']['pageSize']))
                    self.required_parameter['max_page'] = resp.json()['content']['pageSize']
                    self.required_parameter['sid'] = resp.json()['content']['showId']
                    contents = resp.json()['content']['positionResult'].get('result', [])
                    if contents:
                        self.company_result[position].extend(contents)
                        logger.info('当前爬取职位：( {} ) 第[{}]页爬取成功...'.format(position, 1))
                        break
                    else:
                        logger.info('当前爬取职位：( {} ) 第[{}]页爬取失败（无返回内容 - {}）'.format(position, 1, resp.json()))
                else:
                    logger.info('当前爬取职位：( {} ) 第[{}]页爬取失败（状态码：{}）'.format(position, 1, resp.status_code))
            except Exception:
                # 如果数据获取异常，等待数秒重新请求
                times = random.choice(self.time_sleep)
                time.sleep(times)
        else:
            raise ValueError('Initial request error')

    def crawl_detail_info(self, position, contents, show_id):
        """
        保存详情页的岗位描述和工作地址
        :param position: 请求职位
        :param contents: 公司信息
        :param show_id: 详情页关键参数
        :return:
        """
        with self.thread_pool:
            result = []
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                              ' (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
            }
            html_id = contents.get('positionId')
            next_url = 'https://www.lagou.com/jobs/{}.html?show={}'.format(html_id, show_id)
            for i in range(3):
                resp = requests.get(next_url, headers=headers)
                if resp.status_code == 200:
                    try:
                        soup = BeautifulSoup(resp.text, 'lxml')
                        contents['position_description'] = '\n'.join([i.strip() for i in soup.find(class_='job-detail').text.splitlines() if i.strip()])
                        contents['work_address'] = soup.find(class_='work_addr').text.splitlines()[-2].split()[-1].strip() + '[' + str(contents['linestaion']).strip() + ']'
                        break
                    except Exception:
                        # 如果数据获取异常，等待数秒重新请求
                        times = random.choice(self.time_sleep)
                        time.sleep(times)
                        logger.warning('next_url: {}, sleep: {}, retry times: {}'.format(next_url, times, i+1))
            else:
                contents['position_description'] = 'empty'
                contents['work_address'] = '[' + str(contents.get('linestaion', '')).strip() + ']'
            result.append(contents)
            # 保存所有公司的招聘详情信息
            self.detail_result[position].extend(result)

    def start_crawl(self, page, position):
        """
        爬取每一页的招聘公司信息
        :param page: 爬取页数
        :param position: 爬取职位
        :return:
        """
        with self.thread_pool:
            data = {
                'first': 'false',
                'pn': page,
                'kd': position,
                'sid': self.required_parameter['sid']
            }
            # 获取当前页的所有招聘公司信息
            for i in range(3):
                resp = self.session.post(self.search_url, data=data)
                if resp.status_code == 200:
                    try:
                        contents = resp.json()['content']['positionResult']['result']  # result存在就跳出循环
                        if contents:
                            break
                    except Exception:
                        # 如果没有获取到result，等待数秒重新请求
                        times = random.choice(self.time_sleep)
                        time.sleep(times)
                        logger.warning('data: {}, sleep: {}, retry times: {}'.format(data, times, i+1))
            else:
                # 请求失败就返回
                logger.info('当前爬取职位：( {} ) 第[{}]页爬取失败（无返回内容 - {}）'.format(position, page, resp.json()))
                return

            self.company_result[position].extend(contents)
            logger.info('当前爬取职位：( {} ) 第[{}]页爬取成功...'.format(position, page))

    def crawl_position_info(self, position):
        """
        爬取指定职位的招聘信息
        :param position: 职位名称
        :return:
        """
        # 构造初始请求，保存拉钩网首页cookies和第一页所有公司信息
        self.company_result[position] = []
        self.initial_request(position=position)

        # 多线程爬取后续每一页的公司信息
        threads = []
        for each_page in range(2, self.required_parameter['max_page'] + 1):
            t = threading.Thread(target=self.start_crawl, args=(each_page, position))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        logger.info('当前爬取职位：( {} ) 所有页的公司信息爬取完毕!!!'.format(position))

        # 多线程爬取所有公司详情页的岗位描述和工作地址
        threads = []
        self.detail_result[position] = []
        for position_info in self.company_result[position]:
            t = threading.Thread(target=self.crawl_detail_info,
                                 args=(position, position_info, self.required_parameter['sid']))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        logger.info('当前爬取职位：( {} ) 所有公司的详情信息爬取完毕!!! 总数：{}'.format(position, len(self.detail_result[position])))

    def data_structured(self, position):
        """
        数据规整
        :param position: 职位名称
        :return:
        """
        # 格式化item
        item = dict(职位名称=[], 薪水=[], 学历要求=[], 公司名称=[], 工作地址=[], 工作年限=[], 工作性质=[],
                    职位诱惑=[], 职位描述=[], 城市=[], 区域=[], 公司人数=[], 公司标签=[], 行业领域=[], 融资阶段=[])
        # 保存每个职位的所有公司招聘信息
        for each in self.detail_result[position]:
            item['公司名称'].append(each.get('companyFullName', 'empty'))
            item['职位名称'].append(each.get('positionName', 'empty'))
            item['薪水'].append(each.get('salary', 'empty'))
            item['学历要求'].append(each.get('education', 'empty'))
            item['工作地址'].append(each.get('work_address', 'empty'))
            item['工作年限'].append(each.get('workYear', 'empty'))
            item['工作性质'].append(each.get('jobNature', 'empty'))
            item['职位诱惑'].append(each.get('positionAdvantage', 'empty'))
            item['职位描述'].append(each.get('position_description', 'empty'))
            item['城市'].append(each.get('city', 'empty'))
            item['区域'].append(each.get('district', 'empty'))
            item['公司人数'].append(each.get('companySize', 'empty'))
            item['公司标签'].append(', '.join([str(i) for i in each['companyLabelList']]) if each.get('companyLabelList') else 'empty')
            item['行业领域'].append(each.get('industryField', 'empty'))
            item['融资阶段'].append(each.get('financeStage', 'empty'))
        self.item[position] = item

    def plot_pie(self, position, data):
        """
        绘制饼图（薪水比例）
        :param position: 职位
        :param data: 数据源
        :return:
        """
        mapping = ['1k-4k', '5k-8k', '9k-12k', '13k-18k', '19k-25k', '26k-30k', '31k-35k', '36k-40k', '41k-50k']
        result = {}
        # 统计所有薪水比例数量
        for value in data['薪水'].values:
            salary = [int(i.lower().split('k')[0]) for i in str(value).split('-')]
            mean = sum(salary)//2  # 计算薪水平均值
            for each in mapping:
                limit_min, limit_max = [int(i.lower().split('k')[0]) for i in each.split('-')]
                if limit_min <= mean <= limit_max:
                    result[each] = result.get(each, 0) + 1  # 统计薪水的比例数量
                    break
                elif mean >= 51:
                    result['51k+'] = result.get('51k+', 0) + 1  # 统计超出51k薪水的数量
                    break
        # 计算所有薪水比例的占比
        count = sum(result.values())
        for key, value in result.items():
            result[key] = float('{:.2f}'.format(value/count*100))

        # 绘制饼图
        plt.figure(figsize=(10, 5), dpi=120)
        plt.title('薪水比例饼图-（{}）'.format(position))  # 添加标题
        plt.axis(aspect='equal')  # 设置横轴和纵轴大小相等
        plt.pie(x=[i for i in result.values()], labels=[i for i in result.keys()], pctdistance=0.6, labeldistance=1.1,
                autopct='%.2f%%', shadow=False, startangle=180, radius=1.1)
        plt.legend(loc='best', fontsize=4)  # 添加图例
        plt.savefig('{0}/薪水比例饼图-{1}.jpg'.format(self.save_folder, position), dpi=260)  # 保存图片
        # plt.show()  # 预览图片

    def plot_word_cloud(self, position, data):
        """
        绘制词云图（薪水、工作地址、工作年限、职位诱惑、职位描述、公司人数、公司标签、行业领域）
        :param position: 职位
        :param data: 数据源
        :return:
        """
        if not os.path.isdir('{}/词云图'.format(self.save_folder)):
            os.mkdir('{}/词云图'.format(self.save_folder))
        mapping = {
            '薪水': data['薪水'],
            '工作地址': data['工作地址'],
            '工作年限': data['工作年限'],
            '职位诱惑': data['职位诱惑'],
            '职位描述': data['职位描述'],
            '公司人数': data['公司人数'],
            '公司标签': data['公司标签'],
            '行业领域': data['行业领域'],
        }
        skip_list = ['薪水', '工作年限', '工作地址', '公司人数', '行业领域', '职位描述', '职位诱惑']  # 跳过jieba分词，使用原始字符串
        drop_list = ['-', '岗位要求', '任职要求', '工作要求', '职位要求', '岗位职责', '工作职责', '任职资格', '熟悉']  # 过滤的字符串
        for field, item in mapping.items():
            wc = WordCloud(background_color='white',
                           width=600,
                           height=800,
                           font_path=r'C:\Windows\Fonts\simkai.ttf',  # 如果是中文必须要添加这个，否则会显示成框框
                           max_words=5000,  # 设置最大字数
                           random_state=30,  # 设置有多少种随机生成状态，即有多少种配色方案
                           )
            filter_value = [str(i).strip() for i in item.values if str(i) != 'empty']  # 过滤无效值
            text = ''
            for each_value in filter_value:  # 过滤字符串
                new = each_value
                for drop_value in drop_list:
                    new = new.replace(drop_value, ' ')
                text += '{} '.format(new)

            if field not in skip_list:  # 使用jieba分词，精确模式切分中文
                text = ' '.join([str(i).strip() for i in jieba.cut(text) if str(i).strip()])

            try:
                wc.generate_from_text(text)  # 生成词云
            except Exception:
                continue
            plt.imshow(wc)  # 使用plt加载图片
            plt.axis('off')  # 不显示坐标轴
            # plt.show()  # 预览图片
            wc.to_file('{0}/词云图/{1}词云图-{2}.jpg'.format(self.save_folder, position, field))  # 保存词云图片到本地

    def data_visualization(self, position):
        """
        数据建表、绘图
        :param position: 职位名称
        :return:
        """
        if not os.path.isdir(self.save_folder):
            # 在当前路径下创建保存爬虫结果的文件夹
            os.mkdir(self.save_folder)

        data = pd.DataFrame(self.item[position])
        # 生成Excel表
        data.to_excel('{}/{}.xls'.format(self.save_folder, position), sheet_name=position)
        logging.info('{}.xls 写入成功...'.format(position))

        # 绘制薪水比例饼图
        self.plot_pie(position, data=data)
        logging.info('薪水比例饼图-（{}）.jpg 绘制成功...'.format(position))

        # 绘制词云图
        self.plot_word_cloud(position, data=data)
        logging.info('词云图-（{}） 绘制成功...'.format(position))

    def debug_func(self):
        for each_position in self.search_info['position']:
            self.save_folder = '职位爬取结果-{}'.format(each_position)  # 保存爬虫结果的文件夹名称（保存到当前路径）
            if not os.path.isdir(self.save_folder):
                # 在当前路径下创建保存爬虫结果的文件夹
                os.mkdir(self.save_folder)
            data = pd.read_excel('{}/{}.xls'.format(self.save_folder, each_position), sheet_name=each_position)

            # 绘制薪水比例饼图
            self.plot_pie(each_position, data=data)
            logging.info('薪水比例饼图-（{}）.jpg 绘制成功...'.format(each_position))

            # 绘制词云图
            self.plot_word_cloud(each_position, data=data)
            logging.info('词云图-（{}） 绘制成功...'.format(each_position))

    def main(self):
        for each_position in self.search_info['position']:
            # 爬取指定职位的所有公司招聘信息
            self.crawl_position_info(position=each_position)
            # 数据规整
            self.data_structured(position=each_position)
            # 数据建表、绘图
            self.save_folder = '职位爬取结果-{}'.format(each_position)  # 保存爬虫结果的文件夹名称（保存到当前路径）
            self.data_visualization(position=each_position)
            time.sleep(random.choice(self.time_sleep))


if __name__ == '__main__':
    positions = ['爬虫开发']  # 职位
    city_info = '深圳'  # 工作地点
    lagou_spider = LagouSpider(search_info={'position': positions, 'city': city_info}, thread_pool_max=10)
    lagou_spider.main()
