"""
爬取CCC网站 - Selenium
"""
# -*- coding:utf-8 -*-
import time
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

__author__ = 'Evan'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class CCCSpider(object):

    def __init__(self, account, url=''):
        chrome_options = webdriver.ChromeOptions()  # 不加载图片
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 设置为开发者模式，避免被识别
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 设置无界面模式
        self.driver = webdriver.Chrome(options=chrome_options)  # 初始化driver
        self.waiting = WebDriverWait(self.driver, 60)  # 设置显示等待60秒
        self.driver.implicitly_wait(60)  # 设置隐示等待60秒
        self.source_url = url
        self.account = account

    def switch_to_windows(self, to_parent_windows=False):
        """
        切换到不同的windows窗口
        :param to_parent_windows: 默认为False，如果设置为True则回到主窗口
        :return:
        """
        total = self.driver.window_handles
        if to_parent_windows:
            self.driver.switch_to.window(total[0])
        else:
            current_windows = self.driver.current_window_handle
            for window in total:
                if window != current_windows:
                    self.driver.switch_to.window(window)

    def switch_to_frame(self, index=0, to_parent_frame=False, to_default_frame=False):
        """
        切换到不同的frame框架
        :param index: expect by frame index value or id or name or webelement
        :param to_parent_frame: 默认为False，如果设置为True则切换到上一个frame框架
        :param to_default_frame: 默认为False，如果设置为True则切换到最上层的frame框架
        :return:
        """
        if to_parent_frame:
            self.driver.switch_to.parent_frame()
        elif to_default_frame:
            self.driver.switch_to.default_content()
        else:
            self.driver.switch_to.frame(index)

    def open_new_windows(self, new_url):
        """
        打开一个新的windows窗口
        :param new_url: 新的URL
        :return:
        """
        js = "window.open({})".format(new_url)
        self.driver.execute_script(js)
        time.sleep(2)

    def close_current_windows(self):
        # 关闭当前页面
        if self.driver:
            self.driver.close()

    def quit_browser(self):
        # 退出所有页面
        if self.driver:
            self.driver.quit()

    def login_ccc(self):
        """
        Login ccc website
        :return:
        """
        self.driver.get(self.source_url)
        # Login CCC
        username = self.waiting.until(EC.presence_of_element_located((By.XPATH, '//*[@id="userInput"]')))
        username.send_keys(self.account[0])
        self.waiting.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-button"]'))).click()
        password = self.waiting.until(EC.presence_of_element_located((By.XPATH, '//*[@id="passwordInput"]')))
        password.send_keys(self.account[1])
        self.waiting.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-button"]'))).click()
        # safety certificate
        self.switch_to_frame()
        self.waiting.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="login-form"]/div[2]/div/label/input'))).click()
        self.waiting.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="auth_methods"]/fieldset/div[1]/button'))).click()
        time.sleep(10)

    @staticmethod
    def ask_search_config():
        ask_info = {
            'serial_number': 'Serial Number: ',
            'uut_type': 'UUT Type: ',
            'machine': 'Machine: ',
            'area': 'Area: ',
            'from_data': 'From Data(格式: 月-日-年): ',
            'to_data': 'To Data(格式: 月-日-年): ',
            'use_debug_db': 'Use Debug DB(Y/N，默认N): '
        }
        while True:
            print('现在开始填入要搜索的信息，不需要填的参数直接按回车到下一个：')
            question = dict()
            question.update(ask_info)
            for key in question:
                question[key] = input(question[key])
            result = input('填写确认无误？(Y/N，默认Y)')
            if result.upper() == 'Y':
                break
            time.sleep(1)
        return question

    def test_record_search(self):
        """
        Test record search
        :return:
        """
        # 进入Log查找面板
        self.open_new_windows(new_url='https://cesium.cisco.com/apps/PolarisSearch/AdvanceSearch')
        self.switch_to_windows()

        # 依次填入要查找的LOG信息
        ask_info = self.ask_search_config()
        for key, value in ask_info.items():
            if value:
                if key == 'serial_number':
                    input_box = self.waiting.until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="searchHeader"]/form/div[1]/div[1]/div[1]/textarea')))
                elif key == 'uut_type':
                    input_box = self.waiting.until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="searchHeader"]/form/div[1]/div[1]/div[2]/textarea')))
                elif key == 'machine':
                    input_box = self.waiting.until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="searchHeader"]/form/div[1]/div[2]/div[1]/textarea')))
                elif key == 'area':
                    input_box = self.waiting.until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="searchHeader"]/form/div[1]/div[2]/div[2]/textarea')))
                elif key == 'from_data':
                    input_box = self.waiting.until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="searchHeader"]/form/div[2]/div[1]/div[1]/md-date-picker/div[1]/input')))
                elif key == 'to_data':
                    input_box = self.waiting.until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="searchHeader"]/form/div[2]/div[1]/div[2]/md-date-picker/div[1]/input')))
                elif key == 'use_debug_db':
                    input_box = self.waiting.until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="searchHeader"]/form/div[2]/div[3]/div[1]/label/input')))
                else:
                    raise ValueError('key is invalid')

                if key == 'use_debug_db':
                    input_box.click()
                else:
                    # input information
                    input_box.clear()
                    input_box.send_keys(value)
                    input_box.send_keys(Keys.ENTER)

        # click search
        time.sleep(1)
        self.waiting.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="searchHeader"]/form/div[4]/div[1]/button'))).click()

    def parse(self):
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        nodes = soup.find_all('a', class_='ui-grid-canvas')
        logger.info('nodes: {}'.format(nodes))

    def main(self):
        self.login_ccc()
        self.test_record_search()
        # self.parse()


if __name__ == '__main__':
    username = input('CEC Username: ')
    password = input('CEC Password: ')
    if username and password:
        spider = CCCSpider((username, password), url='https://cesium.cisco.com/')
        spider.main()
    else:
        raise ValueError('用户名或密码填写有误，请重新填写')
