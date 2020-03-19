"""
爬取CCC网站 - Requests
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
        if '302' in str(resp.history):  # 重定向进入账号登陆界面
            login_url = re.search('name="login-form" action="(.+?)"', resp.text)
            data = {
                'pf.username': self.login_account[0],
                'pf.pass': self.login_account[1],
                'pf.userType': 'cco',
                'pf.TargetResource': '?'
            }
            resp = self.session.post(login_url.group(1), data=data)
            if resp.status_code == 200:
                # 登陆账号后进入认证界面 "Two-Factor Authentication"
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
                # 申请认证请求 --> https://api-dbbfec7f.duosecurity.com/frame/web/v1/auth?
                resp = self.session.post(authentication_url, data=data)
                if '302' in str(resp.history):  # 重定向进入手机验证界面
                    sid = re.search('sid=(.+)', unquote(resp.url))
                    # data = {
                    #     'sid': sid.group(1),
                    #     'device': 'phone1',
                    #     'factor: ': 'Passcode',
                    #     'passcode: ': '317138',  # 使用手机验证码登陆
                    #     'dampen_choice': 'true',
                    #     'out_of_date': 'False',
                    #     'days_out_of_date': '0',
                    #     'days_to_block': 'None'
                    # }
                    data = {
                        'sid': sid.group(1),
                        'device': 'phone1',
                        'factor': 'Duo Push',
                        'dampen_choice': 'true',  # 使用手机push登陆
                        'out_of_date': 'False',
                        'days_out_of_date': '0',
                        'days_to_block': 'None'
                    }
                    # 开始验证
                    resp = self.session.post(self.verification_prompt_url, data=data)
                    if resp.status_code == 200:
                        # TODO 使用手机进入验证软件进行确认
                        input('Please use your mobile phone to verify the login request [Press enter to continue]: ')
                        time.sleep(1)
                        data = {
                            'sid': sid.group(1),
                            'txid': resp.json()['response']['txid']
                        }
                        # 获取验证结果
                        resp = self.session.post(self.verification_status_url, data=data)
                        if resp.status_code == 200:
                            status_result_url = self.verification_source_url + resp.json()['response']['result_url']
                            data = {
                                'sid': sid.group(1)
                            }
                            # 获取验证结果的cookie
                            resp = self.session.post(status_result_url, data=data)
                            if resp.status_code == 200:
                                authentication_url = resp.json()['response']['parent']
                                sig_response = resp.json()['response']['cookie']
                                data = {
                                    'sig_response': sig_response + sig_request.group(2)
                                }
                                # 获取cookie后重新进入认证界面
                                self.session.post(authentication_url, data=data)
                                # 携带认证后的cookie获取Token
                                token_url = 'https://cesium.cisco.com/apps/machineservices/MachineDetails.svc/getToken'
                                resp = self.session.get(token_url)
                                token = resp.json()['session']
                                # 在session中添加Token
                                self.session.headers.update({'csession': token})
                                print('Login CCC website successfully')

    def set_ccc_cookie(self, cookie, csession):
        """
        设置访问CCC网站的请求头 [ cookie & 认证令牌 ]
        :param cookie: 会话cookie
        :param csession: 认证令牌
        :return:
        """
        self.session.headers.update({
            'cookie': cookie,
            'csession': csession,
        })

    def login_ccc(self, whether_manually_get_cookie=False):
        """
        登陆CCC网站
        :param bool whether_manually_get_cookie: 选择是否手动添加Cookie或者自动获取Cookie，默认为自动获取
        :return:
        """
        if whether_manually_get_cookie:
            cookie = input('Cookie: ')
            csession = input('Csession: ')
            if not cookie or not csession:
                raise ValueError('Cookie或Csession填写有误，请重新填写')
            self.set_ccc_cookie(cookie=cookie, csession=csession)
        else:
            self.login()

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
            print('Search result:')
            print(resp.json())

    def main(self, whether_manually_get_cookie=False):
        """
        访问CCC网站获取资源
        :param bool whether_manually_get_cookie: 选择是否手动添加Cookie或者自动获取Cookie
        :return:
        """
        self.login_ccc(whether_manually_get_cookie)
        self.test_record_search()


if __name__ == '__main__':
    username = input('CEC Username: ')
    password = input('CEC Password: ')
    if username and password:
        spider = CCCSpider(login_account=(username, password))
        spider.main(whether_manually_get_cookie=False)
    else:
        raise ValueError('用户名或密码填写有误，请重新填写')
