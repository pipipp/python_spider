"""
Cesium website crawler
"""
# -*- coding:utf-8 -*-
import requests
import re
import time
import json
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

    def login(self):
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
                    # data = {
                    #     'sid': sid.group(1),
                    #     'device': 'phone1',
                    #     'factor: ': 'Passcode',
                    #     'passcode: ': '317138',  # login using mobile verification code
                    #     'dampen_choice': 'true',
                    #     'out_of_date': 'False',
                    #     'days_out_of_date': '0',
                    #     'days_to_block': 'None'
                    # }
                    data = {
                        'sid': sid.group(1),
                        'device': 'phone1',
                        'factor': 'Duo Push',
                        'dampen_choice': 'true',  # Use push to login
                        'out_of_date': 'False',
                        'days_out_of_date': '0',
                        'days_to_block': 'None'
                    }
                    # Start validation
                    resp = self.session.post(self.verification_prompt_url, data=data)
                    if resp.status_code == 200:
                        input('Please use your mobile phone to verify the login request'
                              ' [Press enter to continue after verification]: ')
                        time.sleep(1)
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
                                self.session.headers.update({'csession': token})

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
        })

    def login_ccc(self, automatic_login=True):
        """
        Login http://cesium.cisco.com
        :param automatic_login: If the value is False, you need to manually add cookie and cession
        :return:
        """
        if automatic_login:
            self.login()
        else:
            print('You need to login the CCC website and manually copy the cookie'
                  ' and csession values to start the crawler')
            cookie = input('Cookie: ')
            session = input('Session: ')
            if not cookie or not session:
                raise ValueError('Cookie and cession are filled in incorrectly, please fill in again')
            self.set_ccc_cookie(cookie=cookie, session=session)
        print('Login CCC website successfully')

    def test_record_search(self):
        multi_search_url = 'https://cesium.cisco.com/polarissvcs/central_data/multi_search'
        data = {
            'sernum': '',
            'uuttype': '',
            'area': '',
            'machine': 'fxcavp996',
            'location': '',
            'test': '',
            'passfail': 'P,F,A',
            'start_time': '2020-03-15 00:00:00',
            'end_time': '2020-03-16 00:00:00',
            'dataset': 'test_results',
            'database': None,
            'start': 0,
            'limit': '5000',
            'user': '',
            'attribute': '',
            'fttd': 0,
            'lttd': 0,
            'ftta': 0,
            'passedsampling': 0,
        }
        resp = self.session.post(multi_search_url, data=json.dumps(data))
        if resp.status_code == 200:
            print(resp.json())

    def main(self, automatic_login=True):
        """
        Visit the CCC website for resources
        :param automatic_login: If the value is False, you need to manually add cookie and cession
        :return:
        """
        self.login_ccc(automatic_login)
        self.test_record_search()


if __name__ == '__main__':
    account = ('evaliu', '*******')

    spider = CCCSpider(login_account=account)
    spider.main(automatic_login=True)
