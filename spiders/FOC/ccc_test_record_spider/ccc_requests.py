"""
Cesium website crawler
"""
# -*- coding:utf-8 -*-
import os
import re
import json
import datetime
import base64
import requests
import threading
import tkinter as tk

from tkinter import messagebox
from urllib.parse import unquote

__author__ = 'Evan'


class CCCSpider(object):

    def __init__(self, login_account):
        self.login_account = login_account
        self.root_url = 'https://cesium.cisco.com/apps/cesiumhome/overview'
        self.verification_source_url = 'https://api-dbbfec7f.duosecurity.com'
        self.verification_prompt_url = self.verification_source_url + '/frame/prompt'
        self.verification_status_url = self.verification_source_url + '/frame/status'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/80.0.3987.132 Safari/537.36'
        })

    def login(self, authentication_code=''):
        """
        Login CCC website
        :param authentication_code: Fill in the Mobile pass code
        :return:
        """
        resp = self.session.get(self.root_url)
        if '302' in str(resp.history):  # Redirect to the account login screen
            login_url = re.search('name="login-form" action="(.+?)"', resp.text)
            data = {
                'pf.username': self.login_account[0],
                'pf.pass': self.login_account[1],
                'pf.userType': 'cco',
                'pf.TargetResource': '?'
            }
            resp = self.session.post(login_url.group(1), data=data)
            if resp.status_code == 200:
                # Enter the authentication interface "Two-Factor Authentication"
                sig_request = re.search("'sig_request': '(.+?)(:APP.+?)'", resp.text)
                post_action = re.search("'post_action': '(.+?)'", resp.text)
                referer = 'https://cloudsso.cisco.com/' + post_action.group(1)
                duo_security_url = 'https://api-dbbfec7f.duosecurity.com/frame/web/v1/auth?'
                authentication_url = '{}tx={}&parent={}&v={}'.format(duo_security_url, sig_request.group(1),
                                                                     referer, '2.6')
                data = {
                    'tx': sig_request.group(1),
                    'parent': referer,
                    'referer': referer,
                    'screen_resolution_width': '1920',
                    'screen_resolution_height': '1080',
                    'color_depth': '24',
                    'is_cef_browser': 'false',
                    'is_ipad_os': 'false'
                }
                # Request for certification --> https://api-dbbfec7f.duosecurity.com/frame/web/v1/auth?
                resp = self.session.post(authentication_url, data=data)
                if '302' in str(resp.history):  # Redirect into the mobile phone verification interface
                    sid = re.search('sid=(.+)', unquote(resp.url))
                    data = {
                        'sid': sid.group(1),
                        'device': 'phone1',
                        'factor': 'Passcode',  # Use mobile pass code login
                        'passcode': authentication_code,
                        'out_of_date': 'False',
                        'days_out_of_date': '0',
                        'days_to_block': 'None'
                    }
                    # data = {
                    #     'sid': sid.group(1),
                    #     'device': 'phone1',
                    #     'factor': 'Duo Push',  # Use mobile push login
                    #     'dampen_choice': 'true',
                    #     'out_of_date': 'False',
                    #     'days_out_of_date': '0',
                    #     'days_to_block': 'None'
                    # }
                    # Start validation
                    resp = self.session.post(self.verification_prompt_url, data=data)
                    if resp.status_code == 200:
                        # input('Please use your mobile phone to verify the login request'
                        #       ' [Press enter to continue after verification]: ')
                        data = {
                            'sid': sid.group(1),
                            'txid': resp.json()['response']['txid']
                        }
                        # Get validation results
                        resp = self.session.post(self.verification_status_url, data=data)
                        if resp.status_code == 200:
                            status_result_url = self.verification_source_url + resp.json()['response']['result_url']
                            data = {
                                'sid': sid.group(1)
                            }
                            # Gets the cookie for the validation result
                            resp = self.session.post(status_result_url, data=data)
                            if resp.status_code == 200:
                                authentication_url = resp.json()['response']['parent']
                                sig_response = resp.json()['response']['cookie']
                                data = {
                                    'sig_response': sig_response + sig_request.group(2)
                                }
                                # Retrieve the cookie and re-enter the authentication interface
                                self.session.post(authentication_url, data=data)
                                # Carry the authenticated cookie acquisition Token
                                token_url = 'https://cesium.cisco.com/apps/machineservices/MachineDetails.svc/getToken'
                                resp = self.session.get(token_url)
                                token = resp.json()['session']
                                # Add Token in session
                                self.session.headers.update({
                                    'csession': token,
                                    '_csession': token
                                })

    def set_ccc_cookie(self, cookie, session):
        """
        Add cookie and token to spider
        :param cookie: Request cookie
        :param session: Request token
        :return:
        """
        self.session.headers.update({
            'cookie': cookie,
            'csession': session,
            '_csession': session
        })

    def login_ccc(self, automatic_login=True, authentication_code=''):
        """
        Login http://cesium.cisco.com
        :param bool automatic_login: If the value is False, you need to manually add cookie and cession
        :param str authentication_code: Fill in the Mobile pass code
        :return:
        """
        if automatic_login:
            self.login(authentication_code=authentication_code)
        else:
            print('You need to login the CCC website and manually copy the cookie'
                  ' and csession values to start the crawler')
            cookie = input('Cookie: ')
            session = input('Session: ')
            if not cookie or not session:
                raise ValueError('Cookie and cession are filled in incorrectly, please fill in again')
            self.set_ccc_cookie(cookie=cookie, session=session)
        print('Login CCC website successfully')

    def get_all_test_data(self, data={}):
        """
        Get historical test data on the CCC website
        :param data: Fill in the request data for spider
        :return:
        """
        multi_search_url = 'https://cesium.cisco.com/polarissvcs/central_data/multi_search'
        resp = self.session.post(multi_search_url, data=json.dumps(data))
        if resp.status_code == 200:
            return resp.json()
        else:
            return None

    def get_measurement_data(self, serial_number='', specified_file_type=['sequence_log'], request_params={}):
        """
        Gets the specified measurement file for the specified serial number
        :param str serial_number: Test serial number
        :param list specified_file_type: Fill in the type of measurement document,example:['sequence_log','UUT_buffer']
        :param dict request_params: Fill in the request params for spider
        :return: (measurement type, measurement id)
        """
        measures_url = 'https://cesium.cisco.com/svclnx/cgi-bin/central_cs/services.py/meas/{}'.format(serial_number)
        resp = self.session.get(measures_url, params=request_params)
        if resp.status_code == 200:
            measures_data = resp.json()
            for each_data in measures_data['measurements']:  # Walk through each measurement file
                for file_type in specified_file_type:
                    if file_type in each_data['limit_id']:  # Matches the specified file type
                        yield (file_type, each_data['measurement'])  # return the measurement type and id for download
            else:
                yield None

    def download_measurement_log(self, file_name='measurement.log', binary_id=''):
        """
        Download the measurement log to local
        :param file_name: Log file name
        :param binary_id: Measurement log id
        :return:
        """
        download_url = 'https://cesium.cisco.com/svclnx/cgi-bin/central_cs/services.py/binarymeas_data/run'
        data = {
            'binary_id': binary_id,
            'source': 'Apollo'
        }
        resp = self.session.post(download_url, data=json.dumps(data))
        if resp.status_code == 200:
            content = base64.b64decode(resp.text)  # Base64 decode
            with open(file_name, 'wb') as wf:
                wf.write(content)  # Write measurement log

    def get_measurement_log_file(self, index, measurement_data, specified_file_type=[]):
        """
        Get measurement log file
        :param int index: measurement data index
        :param dict measurement_data: measurement data
        :param list specified_file_type: The specified file type to download
        :return:
        """
        serial_number = measurement_data['sernum']
        params = {
            'area': measurement_data['area'],
            'server': 'prod',
            'timeid': measurement_data['tst_id'],
            'uuttype': measurement_data['uuttype']
        }
        for measures in self.get_measurement_data(serial_number=serial_number,
                                                  specified_file_type=specified_file_type,
                                                  request_params=params):
            if measures:
                test_time = measurement_data['rectime'].replace(' ', '_').replace(':', '-')
                fail_info = measurement_data['attributes']['TEST']
                # Log name = 'ApolloServer - SN - TestTime - FailInfo - MeasuresType.log'
                log_name = '{}_{}_{}_{}_{}.log'.format(measurement_data['machine'], serial_number,
                                                       test_time, fail_info, measures[0])
                self.download_measurement_log(file_name=log_name, binary_id=measures[1])
                print('Index: {} --> Writing to file << {} >> succeeded'.format(index + 1, log_name))

    def main(self, automatic_login=True, first_request_data={}, download_file_type=[], authentication_code=''):
        """
        Login CCC website to crawl test data
        :param bool automatic_login: Automatic login requires mobile phone approve,
        If the value is False, you need to manually add cookie and cession for spider
        :param dict first_request_data: Fill in the first request data for spider
        :param list download_file_type: Fill in the specified file type to download
        :param str authentication_code: Fill in the Mobile pass code
        :return:
        """
        self.login_ccc(automatic_login, authentication_code)
        all_data = self.get_all_test_data(data=first_request_data)
        if not all_data or not all_data['results']:
            raise ValueError('No data was found, Please confirm the requested data')
        print('Crawling all test data is completed, Total: {}'.format(len(all_data['results'])))

        # Create a folder to store all the measurement files
        if not os.path.isdir('measurement_download_result'):
            os.mkdir('measurement_download_result')
        os.chdir('measurement_download_result')

        threads = []
        print('Start multi-threading to download the measurement file')
        for index, each_data in enumerate(all_data['results']):
            t = threading.Thread(target=self.get_measurement_log_file, args=(index, each_data, download_file_type))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        print('All the measurement files have been downloaded')


class SpiderGui(object):

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('CCC Spider Tool                        Author: ～Evan～')
        self.root.geometry('580x220')
        self.current_month = datetime.datetime.now().strftime('%Y-%m-%d')
        self.test_status = None
        self.log_status = None
        self.debug_status = None

        tk.Label(self.root, text='CEC Username').grid(row=0, column=0)
        self.username = tk.StringVar()
        tk.Entry(self.root, textvariable=self.username).grid(row=1, column=0)

        tk.Label(self.root, text='CEC Password').grid(row=0, column=1)
        self.password = tk.StringVar()
        tk.Entry(self.root, textvariable=self.password, show='*').grid(row=1, column=1)

        tk.Label(self.root, text='Mobile Pass Code').grid(row=0, column=2)
        self.pass_code = tk.StringVar()
        tk.Entry(self.root, textvariable=self.pass_code).grid(row=1, column=2)

        self.use_debug = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Use Debug DB", variable=self.use_debug, command=self.debug_button_event). \
            grid(row=6, column=2)

        tk.Label(self.root, text='Select Status').grid(row=2, column=2)
        self.fail_status = tk.BooleanVar()
        self.pass_status = tk.BooleanVar()
        self.about_status = tk.BooleanVar()
        tk.Checkbutton(self.root, text="F", variable=self.fail_status, command=self.status_button_event)\
            .grid(row=3, column=2, sticky=tk.NSEW)
        tk.Checkbutton(self.root, text="P", variable=self.pass_status, command=self.status_button_event). \
            grid(row=4, column=2, sticky=tk.NSEW)
        tk.Checkbutton(self.root, text="A", variable=self.about_status, command=self.status_button_event). \
            grid(row=5, column=2, sticky=tk.NSEW)

        tk.Label(self.root, text='Select Download Log').grid(row=2, column=3)
        self.seq_log = tk.BooleanVar()
        self.uut_buffer = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Sequence_log", variable=self.seq_log, command=self.log_button_event). \
            grid(row=3, column=3, sticky=tk.W)
        tk.Checkbutton(self.root, text="UUT_buffer", variable=self.uut_buffer, command=self.log_button_event). \
            grid(row=4, column=3, sticky=tk.W)

        self.label1 = tk.Label(self.root, text='Start Time').grid(row=2, column=0)
        self.start_time = tk.StringVar()
        self.entry1 = tk.Entry(self.root, textvariable=self.start_time)
        self.start_time.set(self.current_month + ' 08:00:00')
        self.entry1.grid(row=3, column=0, sticky=tk.W)

        self.label2 = tk.Label(self.root, text='End Time').grid(row=2, column=1)
        self.end_time = tk.StringVar()
        self.entry2 = tk.Entry(self.root, textvariable=self.end_time)
        self.end_time.set(self.current_month + ' 20:00:00')
        self.entry2.grid(row=3, column=1, sticky=tk.W)

        tk.Label(self.root, text='UUT Type').grid(row=4, column=0)
        self.uut_type = tk.StringVar()
        tk.Entry(self.root, textvariable=self.uut_type).grid(row=5, column=0)

        tk.Label(self.root, text='Serial Number').grid(row=4, column=1)
        self.serial_number = tk.StringVar()
        tk.Entry(self.root, textvariable=self.serial_number).grid(row=5, column=1)

        tk.Label(self.root, text='Area').grid(row=6, column=0)
        self.area = tk.StringVar()
        tk.Entry(self.root, textvariable=self.area).grid(row=7, column=0)

        tk.Label(self.root, text='Machine').grid(row=6, column=1)
        self.machine = tk.StringVar()
        tk.Entry(self.root, textvariable=self.machine).grid(row=7, column=1)

        tk.Button(self.root, text='Quit', command=self.root.quit, bg='GreenYellow').grid(row=7, column=2)
        tk.Button(self.root, text='Execute', command=self.start_crawl, bg='DodgerBlue', width=10)\
            .grid(row=7, column=3, sticky=tk.W)
        self.set_gui_center()

    def status_button_event(self):
        test_status = ''
        input_status = [self.fail_status.get(), self.pass_status.get(), self.about_status.get()]
        status_type = ['F', 'P', 'A']
        for status, types in zip(input_status, status_type):
            if status:
                test_status += types
        self.test_status = ','.join(test_status)

    def debug_button_event(self):
        debug_status = False
        if self.use_debug.get():
            debug_status = True
        self.debug_status = debug_status

    def log_button_event(self):
        log_status = []
        input_status = [self.seq_log.get(), self.uut_buffer.get()]
        status_type = ['sequence_log', 'UUT_buffer']
        for status, types in zip(input_status, status_type):
            if status:
                log_status.append(types)
        self.log_status = log_status

    def set_gui_center(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) / 3
        y = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) / 4
        self.root.geometry('+%d+%d' % (x, y))

    def get_all_input_info(self):
        result = {
            'username': self.username.get(),
            'password': self.password.get(),
            'pass_code': self.pass_code.get(),
            'start_time': self.start_time.get(),
            'end_time': self.end_time.get(),
            'uut_type': self.uut_type.get(),
            'serial_number': self.serial_number.get(),
            'area': self.area.get(),
            'machine': self.machine.get(),
            'select_status': self.test_status,
            'select_download_log': self.log_status,
            'use_debug': self.debug_status,
        }
        return result

    def start_crawl(self):
        all_input_info = self.get_all_input_info()
        if not all_input_info['username']:
            messagebox.showwarning('Warning', 'CEC username is null. Please enter again!')
            return
        if not all_input_info['password']:
            messagebox.showwarning('Warning', 'CEC password is null. Please enter again!')
            return
        if not all_input_info['pass_code']:
            messagebox.showwarning('Warning', 'Mobile pass code is null. Please enter again!')
            return
        if not all_input_info['select_download_log']:
            messagebox.showwarning('Warning', 'Select download log is null. Please enter again!')
            return
        if not all_input_info['select_status']:
            messagebox.showwarning('Warning', 'Select status is null. Please enter again!')
            return
        if not all_input_info['uut_type'] and not all_input_info['serial_number'] and \
                not all_input_info['area'] and not all_input_info['machine']:
            messagebox.showwarning('Warning', 'Search information cannot be empty. Please enter again!')
            return

        if all_input_info['use_debug']:
            all_input_info['use_debug'] = 'dev'
        else:
            all_input_info['use_debug'] = None

        request_data = {
            'sernum': all_input_info['serial_number'],
            'uuttype': all_input_info['uut_type'],
            'area': all_input_info['area'],
            'machine': all_input_info['machine'],
            'location': '',
            'test': '',
            'passfail': all_input_info['select_status'],
            'start_time': all_input_info['start_time'],
            'end_time': all_input_info['end_time'],
            'dataset': 'test_results',
            'database': all_input_info['use_debug'],
            'start': 0,
            'limit': '5000',
            'user': '',
            'attribute': '',
            'fttd': 0,
            'lttd': 0,
            'ftta': 0,
            'passedsampling': 0,
        }
        print('-' * 40)
        print('request_data:\n{}'.format(request_data))
        print('Select download log:\n{}'.format(all_input_info['select_download_log']))
        print('Mobile pass code:\n{}'.format(all_input_info['pass_code']))
        print('-' * 40)

        messagebox.showinfo('Info', 'Information read complete, start to crawl\nClick ok to continue...')
        try:
            spider = CCCSpider(login_account=(all_input_info['username'], all_input_info['password']))
            spider.main(automatic_login=True, first_request_data=request_data,
                        download_file_type=all_input_info['select_download_log'],
                        authentication_code=all_input_info['pass_code'])
        except Exception as es:
            messagebox.showerror('Error', 'Crawl failure\nError msg: {}'.format(es))
        else:
            messagebox.showinfo('Info', 'Crawl successful, All the measurement files have been downloaded')


if __name__ == '__main__':
    spider_gui = SpiderGui()
    spider_gui.root.mainloop()
