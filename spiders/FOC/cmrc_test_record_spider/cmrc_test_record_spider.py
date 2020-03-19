# -*- coding:utf-8 -*-
import requests
import threading
import re
import json
import os
import datetime
import time

from urllib.parse import urljoin

__author__ = 'Evan'


class Crawler(object):

    def __init__(self, base_url=None, start_date=None, end_date=None, station_path=None):
        self.base_url = base_url
        self.source_url = urljoin(self.base_url, 'CMRC/rpUUT_HistoryData.aspx')
        self.login_url = urljoin(self.base_url, 'CMRC/CmrcLogin.aspx')
        self.source_path = os.path.join(os.getcwd(), 'test_record_result')

        self.station_path = station_path
        self.start_date = start_date
        self.end_date = end_date
        self.username = 'evanliu'
        self.password = '**********'
        self.auth_value = None

        self.test_record_exist = {}
        self.test_record_nothingness = {}
        self.failed_server = []
        self.all_test_data = {}
        self.session = requests.Session()

    def read_machine_list(self):
        def open_machine_file(machine_file):
            with open(os.path.join(self.station_path, str(machine_file)), 'r') as rf:
                lines = rf.read()
                return lines

        def start_search(listdir=None):
            for machine_file in listdir:
                if 'fx' in machine_file:
                    lines = open_machine_file(machine_file)

                    product_line = re.search("PRODUCT_LINE = '(\w+)'", lines)
                    test_area = re.search("TEST_AREA = '(\w+)'", lines)
                    stations = re.match('(\w+)\.py', machine_file)

                    if product_line and test_area and stations:
                        product = product_line.groups()[0]
                        area = test_area.groups()[0]
                        station = stations.groups()[0]
                        yield [product, area, station]
                    else:
                        print('no station information found in the file - {}'.format(machine_file))
                        yield None

        machine_list = []
        listdir = os.listdir(self.station_path)
        for machine in start_search(listdir):
            # Save each machine information
            if machine:
                machine_list.append(machine)
        return machine_list

    def parameter(self, do_login=False, machine=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
        }

        if do_login:
            params = {
                '__VIEWSTATE': self.auth_value,
                'tbxUserID': '{}'.format(self.username),
                'txtPassword': '{}'.format(self.password),
                'BtnLogin.x': '0',
                'BtnLogin.y': '0',
            }
        else:
            params = {
                'Date1': '{}'.format(self.start_date),
                'Date2': '{}'.format(self.end_date),
                'DbType': 'All',
                'Machine': '{}'.format(machine),
                'ShowPass': '1'
            }
        return headers, params

    def login_cmrc(self):
        resp = self.session.get(url=self.source_url)

        auth_value = re.findall('name="__VIEWSTATE" value="(.+?)"', resp.text, re.S)
        self.auth_value = str(auth_value[0])

        if '302' in str(resp.history):
            print('Login CMRC website...')
            headers, params = self.parameter(do_login=True)
            self.session.post(url=self.login_url, headers=headers, data=params)
            print('login CMRC successful!')

    def start_query(self, machine_list=None):
        machine_info = '-'.join(machine_list)
        machine = machine_list[2]
        if '_' in machine:
            machine_name = machine.split('_')[0]
        else:
            machine_name = machine

        try:
            final_page_source = []
            headers, params = self.parameter(machine=machine_name)

            resp = self.session.get(url=self.source_url, headers=headers, params=params)
            if resp.status_code == 200:
                # record first page html
                final_page_source.append(resp.text)
                query_url = resp.url

                # search auth_value
                auth_values = re.findall('name="__VIEWSTATE" value="(.+?)"', resp.text, re.S)
                auth_value = str(auth_values[0])

                # search final page index
                total_page_index = re.findall('</option><option value="(\d)">', resp.text)
                if len(total_page_index) > 1:
                    final_page_index = int(total_page_index[-1])

                    # search each page html
                    for index in range(2, final_page_index + 1):
                        headers = self.parameter()[0]
                        params = {
                            '__EVENTARGUMENT': 'GOTOPAGE:BB:{}:0~7'.format(index),
                            '__EVENTTARGET': 'ctrlRpt_UUT_HistoryData0:grdSN',
                            '__VIEWSTATE': '{}'.format(auth_value),
                            'ab18af8010_MainBTabStrip_Selected': 'MainBTabStrip:-1',
                            'ab18af8010_TS_UutHistory_Selected': 'TS_UutHistory:0',
                            'ca1bcf481c_MP_UutHistory_Selected': '0',
                            'cbxShowStartbyDefault': 'on',
                            'CtrlQuickSearch1:ddSearchOpt': 'SNHistory'
                        }
                        resp = self.session.post(url=query_url, headers=headers, data=params)
                        if resp.status_code == 200:
                            final_page_source.append(resp.text)

                return final_page_source
            else:
                return None

        except Exception as ex:
            print('Server ({}) search error, error msg: {}'.format(machine_info, ex))
            self.failed_server.append([machine_info, ex])
            return None

    def cmrc_query(self, machine_list=None):
        machine_info = '-'.join(machine_list)

        total_page = self.start_query(machine_list=machine_list)
        if total_page:
            final_info = []
            for page in total_page:
                test_info = re.findall(re.compile('title=(\d+-\d+-\d+).+?id=.+?>(\w+)</td', re.S), page)
                if test_info:
                    final_info.extend(test_info)

            if final_info:
                print('The Server << {} >> queries for {} slices of test pass data'.format(machine_info, len(final_info)))
                self.all_test_data[machine_info] = '{} pieces of test pass data'.format(len(final_info))

                # Delete duplicate values
                result = set(final_info)
                self.test_record_exist[machine_info] = list(result)
            else:
                print('The server << {} >> test record does not exist'.format(machine_info))
                self.test_record_nothingness[machine_info] = 'Test record does not exist'

    def record_collection_info(self):
        if not os.path.isdir(self.source_path):
            os.mkdir('test_record_result')
        os.chdir(self.source_path)

        if self.failed_server:
            with open('failed_server.txt', 'w') as file:
                for i in self.failed_server:
                    file.write('{}:\nError msg: {}\n\n'.format(i[0], i[1]))

        if self.test_record_exist:
            with open('test_record_exist.json', 'w') as file:
                file.write(json.dumps(self.test_record_exist, ensure_ascii=False, indent=2))

        if self.test_record_nothingness:
            with open('test_record_nothingness.json', 'w') as file:
                file.write(json.dumps(self.test_record_nothingness, ensure_ascii=False, indent=2))

        if self.all_test_data:
            final_test_data = {}
            test_date = dict(From=self.start_date, To=self.end_date)
            final_test_data['Query_date'] = test_date
            final_test_data['Query_result'] = self.all_test_data

            with open('test_data_summary.json', 'w') as file:
                file.write(json.dumps(final_test_data, ensure_ascii=False, indent=2))

    def cmrc_crawler(self):
        machine_list = self.read_machine_list()
        print('The total number of machines is {}'.format(len(machine_list)))

        start_time = datetime.datetime.now()
        # Login http://cmrc.cisco.com
        self.login_cmrc()

        loop_index = 1
        while machine_list:
            queue = []

            try:
                for i in range(20):
                    queue.append(machine_list.pop())
            except IndexError:
                pass

            print('{} Queue {} start, length is {}'.format(datetime.datetime.now(), loop_index, len(queue)))
            print('*' * 100)
            threads = []
            loops = range(len(queue))

            for machines in queue:
                t = threading.Thread(target=self.cmrc_query, args=(machines, ))
                threads.append(t)

            for i in loops:
                threads[i].start()

            for i in loops:
                threads[i].join()

            print('*' * 100)
            print('{} Queue {} is complete\n'.format(datetime.datetime.now(), loop_index))
            loop_index += 1
            time.sleep(5)

        end_time = datetime.datetime.now()
        print('Query all CMRC data completed, it took {} minutes!'.format((end_time - start_time).seconds / 60))

        # Record all CMRC test data
        self.record_collection_info()

    def main(self):
        self.cmrc_crawler()


if __name__ == '__main__':
    station_path = '/home/evanliu/Desktop/gitbucket_code/trunk/trunk/stations/foc'
    base_url = 'http://cmrc.cisco.com'
    start_date = '5/25/2019'
    end_date = '5/31/2019'

    crawler = Crawler(base_url=base_url, start_date=start_date, end_date=end_date, station_path=station_path)
    crawler.main()
