# -*- coding:utf-8 -*-
import datetime
import json
import re
import requests
import os

from bs4 import BeautifulSoup
from urllib.parse import urljoin

__author__ = 'Evan'


class Crawler(object):

    def __init__(self, base_url=None):
        self.base_url = base_url
        self.all_movie_info = {}
        self.all_movies = {}

    @staticmethod
    def open_url(url=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        }
        try:
            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                return response
        except requests.ConnectionError as e:
            print('Connection error, error msg: {}'.format(e.args))

    def find_each_movie(self, content, page_index=None):
        soup = BeautifulSoup(content, 'lxml')
        movie_info = soup.find('ul', attrs={'class': 'movering'})
        movie_names = {}
        movies = {}

        # 保存电影 & 电影名字 & 图片
        for index, line in enumerate(movie_info.find_all(name='li')):
            movie_name = re.findall('\S+', line.text)[0]
            # movie_picture = urljoin(self.base_url, line.find(name='img')['src'])

            movie = urljoin(self.base_url, line.find(name='a')['href'])
            if movie:
                resp = self.open_url(url=movie)
                search_movie = re.search('var vMp4url = "(.+?mp4)', resp.text)
                if search_movie:
                    final_movie = search_movie.groups()[0]
                else:
                    search_movie = re.search('var vMp4url = "(.+?flv)', resp.text)
                    if search_movie:
                        final_movie = search_movie.groups()[0]
                    else:
                        final_movie = None

                final_movie = urljoin(self.base_url, final_movie)
            else:
                final_movie = None

            if movie_name and movie:
                movie_names[index + 1] = movie_name
                movies[movie_name] = final_movie

        if movie_names and movies:
            self.all_movie_info['第{}页：'.format(page_index)] = movie_names
            self.all_movies['第{}页'.format(page_index)] = movies
            return True
        else:
            return False

    def get_total_movies(self):
        loop = 1
        movie_url = 'Video/List/99?page={}'
        while True:
            final_url = urljoin(self.base_url, movie_url.format(loop))
            html = self.open_url(url=final_url)
            # 查找每一页的电影
            flag = self.find_each_movie(html.text, loop)
            if flag:
                loop += 1
            else:
                # 没有找到电影信息则跳出循环
                break

    def main(self):
        self.get_total_movies()

        if not os.path.isdir('movie_search_result'):
            os.mkdir('movie_search_result')
        source = os.getcwd()
        source_path = os.path.join(source, 'movie_search_result')

        if self.all_movie_info:
            os.chdir(source_path)
            if not os.path.isdir('movie_name_summary'):
                os.mkdir('movie_name_summary')
            os.chdir(os.path.join(source_path, 'movie_name_summary'))

            with open('movie_name_summary.txt', 'w', encoding='utf-8') as file:
                file.write(json.dumps(self.all_movie_info, indent=2, ensure_ascii=False) + '\n')

        if self.all_movies:
            start_time = datetime.datetime.now()
            for index, movies in self.all_movies.items():
                print('{}'.format(index))
                for name, movie in movies.items():
                    os.chdir(source_path)
                    if not os.path.isdir('{}电影'.format(index)):
                        os.mkdir('{}电影'.format(index))
                    os.chdir(os.path.join(source_path, '{}电影'.format(index)))

                    if movie:
                        # 截取电影格式
                        movie_format = movie[-3:]

                        print('{} 正在下载：{}'.format(datetime.datetime.now(), name))
                        try:
                            resp = self.open_url(url=movie)
                            with open('{}.{}'.format(name, movie_format), 'wb') as file:
                                file.write(resp.content)
                            print('{} 下载成功'.format(datetime.datetime.now()))
                        except Exception as ex:
                            print('{} 下载失败, Error: {}'.format(datetime.datetime.now(), ex))

            end_time = datetime.datetime.now()
            print('全部下载完毕： 累计{}分钟'.format((end_time - start_time).seconds / 60))


if __name__ == '__main__':
    base_url = 'http://tv.efoxconn.com'
    crawler = Crawler(base_url=base_url)
    crawler.main()
