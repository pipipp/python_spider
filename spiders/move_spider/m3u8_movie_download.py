# -*- coding:utf-8 -*-
import json
import time
import requests
import datetime
import os
import threading
import urllib3
import random
from urllib.parse import urljoin

__author__ = 'Evan'


class MovieDownload(object):

    def __init__(self, source_url=None, queue_count=30):
        """

        :param source_url: m3u8格式的url
        :param queue_count: ts文件同时下载个数
        """
        self.source_url = {}
        for each_url in source_url:
            if 'm3u8' in each_url:
                url = each_url.split('/')
                url.pop()
                base_url = '/'.join(url)

                if not base_url.endswith('/'):
                    base_url = base_url + '/'
                self.source_url[each_url] = base_url
            else:
                raise ValueError('这个url [{}] 不是m3u8的格式，请检查！'.format(each_url))
        self.directory_name = 'm3u8_movies'
        self.failed_ts_url = {}
        self.queue_count = queue_count

    @staticmethod
    def random_headers():
        ua_list = [
            # Chrome UA
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
            # IE UA
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            # Microsoft Edge UA
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
        ]
        ua = random.choice(ua_list)
        headers = {'User-Agent': ua}
        return headers

    def download_movies(self, index=None, ts_url=None, resource_url=None):
        fail_dict = {}
        ts_file_name = str(ts_url).split('/')[-1]
        try:
            print('{}, 正在下载第{}个TS >> {}'.format(datetime.datetime.now(), index, ts_url))
            resp = requests.get(url=ts_url, headers=self.random_headers(), stream=True, verify=False)
            # 保存TS数据流
            with open(ts_file_name, 'wb+') as file:
                file.write(resp.content)
            print('{}, 第{}个TS下载成功'.format(datetime.datetime.now(), index))
        except Exception as ex:
            fail_dict[index] = ts_url
            self.failed_ts_url[resource_url] = fail_dict
            print('{} 第{}下载失败, Error: {}'.format(datetime.datetime.now(), index, ex))

    def check_record_directory_path(self):
        record_path = os.path.join(os.getcwd(), self.directory_name)

        if not os.path.isdir(record_path):
            os.mkdir(self.directory_name)
        os.chdir(record_path)

    @staticmethod
    def check_record_movie_path(movie_name):
        if '/' in movie_name:
            movie_name = movie_name.split('/')[-2]
        movie_path = os.path.join(os.getcwd(), movie_name)

        if not os.path.isdir(movie_path):
            os.mkdir(movie_name)
        os.chdir(movie_path)

    def get_m3u8_movie(self, url=None, base_url=None):
        ts_list = []
        try:
            resp = requests.get(url=url, headers=self.random_headers())
            if resp.status_code == 200:
                # 从m3u8文件里面获取所有的TS文件（原视频数据分割为很多个TS流，每个TS流的地址记录在m3u8文件列表中）
                for line in resp.text.splitlines():
                    if '.ts' in line:
                        ts_list.append(urljoin(base_url, line))
        except Exception as ex:
            print('请求错误: {}'.format(ex))
            ts_list = None
        return ts_list

    @staticmethod
    def merge_ts_file():
        cmd = "copy /b *.ts movie.mp4"
        os.system(cmd)
        # 整合完mp4格式后后，删除ts文件
        os.system('del /Q *.ts')

    def main(self):
        # 禁用安全请求警告(requests.get(url, verify=False))
        urllib3.disable_warnings()
        # 创建保存所有电影的文件目录
        self.check_record_directory_path()

        for url, base_url in self.source_url.items():
            # 初始化failed_ts_url
            self.failed_ts_url = {}

            ts_list = self.get_m3u8_movie(url, base_url)
            if ts_list:
                # 创建每一个电影的存放目录
                self.check_record_movie_path(movie_name=base_url)

                print('url [{}]: 总共获取到{}个ts文件, 等待下载...'.format(url, len(ts_list)))
                start_time = datetime.datetime.now()
                queue_index = 1
                while ts_list:
                    queue = []
                    try:
                        # 设置队列个数上限
                        queue_count = range(self.queue_count)
                        for i in queue_count:
                            queue.append(ts_list.pop())
                    except IndexError:
                        pass

                    print('第{}个队列， 开始下载, 共计{}个'.format(queue_index, len(queue)))
                    print('*' * 100)
                    loops = range(len(queue))
                    threads = []

                    # 多线程爬取
                    for index, ts_url in enumerate(queue):
                        t = threading.Thread(target=self.download_movies, args=(index + 1, ts_url, url))
                        threads.append(t)

                    for i in loops:
                        threads[i].start()

                    for i in loops:
                        threads[i].join()

                    print('*' * 100)
                    print('第{}个队列， 下载完成\n'.format(queue_index))
                    queue_index += 1
                    time.sleep(10)

                end_time = datetime.datetime.now()
                print('url [{}]: 全部下载完毕： 累计{}分钟'.format(url, (end_time - start_time).seconds / 60))

                if self.failed_ts_url:
                    print('失败总数{}个'.format(len(self.failed_ts_url)))
                    with open('failed_ts_url.json', 'w') as file:
                        file.write(json.dumps(self.failed_ts_url, ensure_ascii=False, indent=2) + '\n')
                else:
                    # 如果ts文件全部下载成功，则整合成一个mp4格式的电影文件（可手动下命令整合）
                    print('现在开始整合成mp4格式文件')
                    self.merge_ts_file()
            else:
                print('这个url [{}] 没有发现任何ts文件, 请检查url的正确性！'.format(url))


if __name__ == '__main__':
    # 填入任意个m3u8网址开始下载
    source_url = [
        'https://xx.xxx-xxxx/xxx.m3u8',
        'https://yy.yyy-yyyy/yyy.m3u8'
    ]
    # ts文件同时下载数量
    queue_count = 100

    movie_download = MovieDownload(source_url=source_url, queue_count=queue_count)
    movie_download.main()
