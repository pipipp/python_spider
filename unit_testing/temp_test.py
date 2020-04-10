"""
Cesium website crawler
Download the test log file specified in the web site
"""
# -*- coding:utf-8 -*-
import os
import re
import json
import base64
import requests
import threading

from urllib.parse import unquote

__author__ = 'Evan'


class CCCSpider(object):

    def __init__(self, login_account, thread_pool_max=10):
        self.login_account = login_account
        self.download_results = None
        self.thread_pool = None
        self.thread_pool_max = thread_pool_max
        self.root_url = 'https://cesium.cisco.com/apps/cesiumhome/overview'
        self.verification_source_url = 'https://api-dbbfec7f.duosecurity.com'
        self.verification_prompt_url = self.verification_source_url + '/frame/prompt'
        self.verification_status_url = self.verification_source_url + '/frame/status'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/80.0.3987.132 Safari/537.36'
        })
        self.build_storage_folder()

    @staticmethod
    def build_storage_folder():
        # Create a folder to store all the download results
        if not os.path.isdir('download_results'):
            os.mkdir('download_results')
        os.chdir('download_results')

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
            try:
                self.login(authentication_code=authentication_code)
            except Exception:
                raise ValueError('The mobile pass code expires, Please fill in again!')
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
        flag = False
        resp = self.session.post(download_url, data=json.dumps(data))
        if resp.status_code == 200:
            content = base64.b64decode(resp.text)  # Base64 decode
            with open(file_name, 'wb') as wf:
                wf.write(content)  # Write measurement log
            flag = True
        return flag

    def get_measurement_log_file(self, measurement_data, specified_file_type=[]):
        """
        Get measurement log file
        :param dict measurement_data: measurement data
        :param list specified_file_type: The specified file type to download
        :return:
        """
        with self.thread_pool:  # Controls the number of thread pools
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
                    test_status = measurement_data['attributes'].get('TEST') or 'PASS'
                    if ':' in test_status:
                        test_status = test_status.split(':')[0]
                    # Log name = 'ApolloServer - SN - TestTime - TestStatus - MeasuresType.log'
                    log_name = '{}_{}_{}_{}_{}.log'.format(measurement_data['machine'], serial_number,
                                                           test_time, test_status, measures[0])
                    # Skip duplicate test logs
                    if log_name in self.download_results:
                        continue
                    # Download the test log file
                    flag = self.download_measurement_log(file_name=log_name, binary_id=measures[1])
                    if flag:
                        self.download_results.append(log_name)
                        print('Download the file << {} >> succeeded'.format(log_name))
                    else:
                        # If download the test log fail, try again
                        flag = self.download_measurement_log(file_name=log_name, binary_id=measures[1])
                        if flag:
                            self.download_results.append(log_name)
                            print('Download the file << {} >> succeeded'.format(log_name))
                        else:
                            print('Download the file << {} >> failed !!!')

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
            raise ValueError('No data was found, Please check that the information you entered is correct!')
        print('Crawling all test data is completed, Total: {}'.format(len(all_data['results'])))

        self.download_results = []
        threads = []
        self.thread_pool = threading.Semaphore(value=self.thread_pool_max)  # Set thread pool
        print('Start multi-threading to download the measurement file')
        for each_data in all_data['results']:
            t = threading.Thread(target=self.get_measurement_log_file, args=(each_data, download_file_type))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        print('All the measurement files have been downloaded')


if __name__ == '__main__':
    cec_username = 'evaliu'
    cec_password = '***'
    pass_code = '777195'
    request_data = {
        'sernum': '',
        'uuttype': '',
        'area': '',
        'machine': 'fxcavp996',
        'location': '',
        'test': '',
        'passfail': 'F',  # 'passfail': 'P,F,A',
        'start_time': '2020-03-22 00:00:00',
        'end_time': '2020-03-23 00:00:00',
        'dataset': 'test_results',
        'database': None,  # debug database: 'dev'
        'start': 0,
        'limit': '5000',
        'user': '',
        'attribute': '',
        'fttd': 0,
        'lttd': 0,
        'ftta': 0,
        'passedsampling': 0,
    }
    download_file = ['sequence_log']  # ['sequence_log', 'UUT_buffer']
    # Run crawler
    spider = CCCSpider(login_account=(cec_username, cec_password), thread_pool_max=10)
    spider.main(automatic_login=True,  first_request_data=request_data,
                download_file_type=download_file, authentication_code=pass_code)
