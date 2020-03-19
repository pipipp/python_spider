# -*- coding:utf-8 -*-
import os
import time
import datetime
import re
import xlwt
import threading
import tkinter as Tkinter
import tkinter.messagebox as tkMessageBox

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tkinter.ttk import Combobox

__author__ = 'Evan'


class Spider(object):

    def __init__(self, url=''):
        self.url = url
        self.drive = None
        self.waiting = None
        # 数据存放路径
        self.root_path = r'D:\116_failure_data_collection'

    def switch_to_windows(self, to_parent_windows=False):
        # 切换windows窗口
        total = self.drive.window_handles
        if to_parent_windows:
            self.drive.switch_to.window(total[0])
        else:
            current_windows = self.drive.current_window_handle
            for window in total:
                if window != current_windows:
                    self.drive.switch_to.window(window)

    def switch_to_frame(self, reference=None, to_parent_frame=False, to_default_frame=False):
        # 切换网页框架
        reference = reference or 0
        if to_default_frame:
            self.drive.switch_to.default_content()
        elif to_parent_frame:
            self.drive.switch_to.parent_frame()
        else:
            self.drive.switch_to.frame(reference)

    def quit_browser(self):
        # 关闭浏览器
        if self.drive:
            self.drive.quit()

    def open_new_windows(self, url):
        # 打开一个新的窗口
        js = 'window.open("{}")'.format(url)
        self.drive.execute_script(js)

    def close_current_windows(self):
        # 关闭浏览器
        if self.drive:
            self.drive.close()

    def login_web_page(self):
        self.drive = webdriver.Ie()
        # 显示等待10秒
        self.waiting = WebDriverWait(self.drive, 10)
        # 隐式等待10秒
        self.drive.implicitly_wait(10)
        self.drive.get(self.url)
        # 进入到116界面
        self.drive.find_element_by_xpath('/html/body/table/tbody/tr[7]/td[1]/a/img').click()
        username = self.drive.find_element_by_xpath('//*[@id="username"]')
        username.send_keys('an.wang')
        password = self.drive.find_element_by_xpath('//*[@id="password"]')
        password.send_keys('password')
        password.send_keys(Keys.ENTER)
        # 定位OEM PRODUCT
        while True:
            try:
                time.sleep(5)
                self.waiting.until(EC.frame_to_be_available_and_switch_to_it(0))
                self.drive.find_element_by_xpath('//*[@id="menu4"]/b/font').click()
                self.drive.find_element_by_xpath('//*[@id="submenu4"]/table/tbody/tr[2]/td/a').click()
                self.switch_to_frame(to_parent_frame=True)
                self.switch_to_frame(1)
                # 选择WNBU
                self.drive.find_element_by_xpath('//*[@id="objBuList"]/option[3]').click()
                break
            except Exception:
                self.drive.refresh()
                time.sleep(2)

    def select_product(self, start_date=None, end_date=None, line_data=None, product_data=None):
        # 选择产品料号
        if line_data == 'Barbados':
            if product_data == '2KVE':
                self.drive.find_element_by_xpath('//*[@id="objProdList"]/option[6]').click()
                self.drive.find_element_by_xpath('//*[@id="objSkuList"]/tbody/tr[3]/td/label').click()
                self.drive.find_element_by_xpath('//*[@id="objSkuList"]/tbody/tr[4]/td/label').click()
            elif product_data == '3KVE':
                self.drive.find_element_by_xpath('//*[@id="objProdList"]/option[6]').click()
                self.drive.find_element_by_xpath('//*[@id="objSkuList"]/tbody/tr[5]/td/label').click()
                self.drive.find_element_by_xpath('//*[@id="objSkuList"]/tbody/tr[6]/td/label').click()
            elif product_data == '4K':
                self.drive.find_element_by_xpath('//*[@id="objProdList"]/option[2]').click()
                self.drive.find_element_by_xpath('//*[@id="objSkuList"]/tbody/tr[1]/td/label').click()
                self.drive.find_element_by_xpath('//*[@id="objSkuList"]/tbody/tr[2]/td/label').click()
                self.drive.find_element_by_xpath('//*[@id="objSkuList"]/tbody/tr[3]/td/label').click()
                self.drive.find_element_by_xpath('//*[@id="objSkuList"]/tbody/tr[4]/td/label').click()

        # 输入时间
        self.drive.find_element_by_xpath('//*[@id="tbStime"]').send_keys(start_date)
        self.drive.find_element_by_xpath('//*[@id="tbEtime"]').send_keys(end_date)
        self.drive.find_element_by_xpath('//*[@id="btSubmit"]').click()

    def select_test_data(self, index=0):
        result_page = None
        station = ''
        text_list = ['PCBDL Total Test Information', 'PCBST Total Test Information', 'PCBVF Total Test Information']

        # 等待页面完全刷新出来
        self.waiting.until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@name="Form1"]/table[last()]/tbody/tr[1]/td[3]/b')))

        # 定位 PCBDL & PCBVF & PCBST Failure 测试数据
        text_data = self.waiting.until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@bgcolor="#ccffcc"][{}]/td[1]/b'.format(index + 1))))

        if text_data.text in text_list:
            # 保存station信息
            station = (text_data.text[:5])
            time.sleep(2)
            self.waiting.until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@bgcolor="#ccffcc"][{}]/td[3]/b'.format(index + 1)))).click()
            time.sleep(2)

            # 切换到failure窗口
            try:
                self.switch_to_windows()
            except Exception:
                self.waiting.until(EC.visibility_of_element_located(
                    (By.XPATH, '//*[@bgcolor="#ccffcc"][{}]/td[3]/b'.format(index + 1)))).click()
                time.sleep(2)
                self.switch_to_windows()
            # 获取failure数据
            page_source = self.parse_page(self.drive.page_source)
            result_page = page_source
            # 关闭当前failure数据窗口并定位parent窗口
            self.close_current_windows()
            self.switch_to_windows(to_parent_windows=True)
            while True:
                try:
                    self.waiting.until(EC.frame_to_be_available_and_switch_to_it(1))
                    break
                except Exception:
                    time.sleep(2)

        return result_page, station

    @staticmethod
    def parse_page(content=None):
        soup = BeautifulSoup(content, 'lxml')
        result = soup.find_all(name='td')
        # 保存所有Failure的文本数据
        total_list = ['None' if not r.string else r.string for r in result]
        return total_list

    @staticmethod
    def get_summary_data(test_data=None):
        # 循环取出Summary数据
        result_list = []
        i = 0
        while True:
            if test_data[1] == 'Sernum':
                break
            # 每次取出5个数值
            result_list.append(test_data[0:5])
            # 将取出的数值从列表里面删除
            loops = range(5) if i < 3 else range(6)
            for r in loops:
                test_data.pop(0)
            i += 1
        return result_list, test_data

    @staticmethod
    def format_control(data='', format=None):
        format = format or '^\d+$'

        r = re.match(format, data)
        if r:
            return True
        else:
            return False

    def get_analysis_data(self, test_data=None):
        # 循环取出Analysis数据
        index = None
        result_list = []
        loops = 0
        while True:
            if not test_data:
                break

            # 取出标题
            if loops == 0:
                result_list.append(test_data[0:9])
                # 将取出的数值从列表里面删除
                for r in range(10):
                    test_data.pop(0)
            else:
                # 取出每行数据
                if self.format_control(test_data[0]):
                    # 如果第一个是index值则保存index
                    index = test_data[0]
                    result_list.append(test_data[0:9])
                    # 将取出的数值从列表里面删除
                    for i in range(10):
                        test_data.pop(0)
                elif 'FOC' in test_data[0]:
                    # 添加index数值
                    each_line = []
                    each_line.append(index)
                    each_line.extend(test_data[0:8])

                    result_list.append(each_line)
                    # 将取出的数值从列表里面删除
                    for i in range(9):
                        test_data.pop(0)
                else:
                    raise ValueError('not find expect value')

            loops += 1
        return result_list

    @staticmethod
    def write_excel(sheet1_info=None, sheet2_info=None, excel_name='example', test_time=None):
        # 默认值为 "empty"
        sheet1_info = sheet1_info or ['empty']
        sheet2_info = sheet2_info or ['empty']

        f = xlwt.Workbook()
        sheet1 = f.add_sheet('Summary', cell_overwrite_ok=True)
        sheet2 = f.add_sheet('Analysis', cell_overwrite_ok=True)

        # 循环写入 "Summary" & "Analysis" 表格
        for sheet, info in zip([sheet1, sheet2], [sheet1_info, sheet2_info]):
            for index, value in enumerate(info):
                if isinstance(value, (list, tuple)):
                    # 单行写入多个数值
                    each_line = range(len(value))
                    for line in each_line:
                        sheet.write(index, line, value[line])
                else:
                    sheet.write(index, 0, value)
        start_time = test_time[0].replace(':', '_')
        end_time = test_time[1].replace(':', '_')
        f.save('{}-{}~{}.xls'.format(excel_name, start_time, end_time))

    def capture_loops(self):
        # 用生成器逐一保存需要的数据
        for index in range(4):
            page_source, station = self.select_test_data(index)
            yield page_source, station

    def create_test_data_folder(self, start_date, end_date, line_data, product_data):
        start_date = start_date.split()[0]
        end_date = end_date.split()[0]
        date = start_date + '~' + end_date
        # 查找date folder
        if date not in os.listdir(self.root_path):
            os.chdir(self.root_path)
            os.mkdir(date)
        # 查找line_data folder
        if line_data not in os.listdir(os.path.join(self.root_path, date)):
            os.chdir(os.path.join(self.root_path, date))
            os.mkdir(line_data)
        # 查找product_data folder
        if product_data not in os.listdir(os.path.join(self.root_path, date, line_data)):
            os.chdir(os.path.join(self.root_path, date, line_data))
            os.mkdir(product_data)
            os.chdir(product_data)
        else:
            # 如果都存在则直接切换到指定目录
            final_path = os.path.join(self.root_path, date, line_data, product_data)
            os.chdir(final_path)

    def open_url(self, start_date, end_date, line_data, product_data):
        # 登陆116网站
        self.login_web_page()
        # 选择测试数据
        self.select_product(start_date, end_date, line_data, product_data)
        # 抓取测试数据
        for page_source, station in self.capture_loops():
            # 清洗测试数据
            if page_source and station:
                summary_data, total_list = self.get_summary_data(page_source)
                analysis_data = self.get_analysis_data(total_list)
                # 创建数据存放目录
                self.create_test_data_folder(start_date, end_date, line_data, product_data)
                # 保存测试数据
                test_time = [start_date.split()[1], end_date.split()[1]]
                self.write_excel(summary_data, analysis_data, station.upper(), test_time)
        # 退出浏览器
        tkMessageBox.showinfo('提示', 'Failure数据已保存完毕\n请点击确定继续...')
        self.quit_browser()


class Magic_gui(object):

    def __init__(self, url=''):
        self.root = Tkinter.Tk()
        self.photo = Tkinter.PhotoImage(file='Star.png')
        self.root.title('116查询器                       Author:  ★～Evan～★')
        self.line = 'Barbados'
        self.product = ('2KVE', '3KVE', '4K')
        self.current_month = datetime.datetime.now().strftime('%Y-%m-%d')
        self.crawler = Spider(url)
        # self.root.geometry('200x150')
        # self.root.destroy()

        # 放入图片
        Tkinter.Label(self.root, height=120, image=self.photo).grid(row=0, column=1, columnspan=2, rowspan=2)

        # 选择开始日期
        self.label1 = Tkinter.Label(self.root, text='请输入开始日期').grid(row=2, column=1, sticky=Tkinter.W)
        self.input1 = Tkinter.StringVar()
        self.entry1 = Tkinter.Entry(self.root, textvariable=self.input1)
        self.input1.set(self.current_month + ' 08:00')
        self.entry1.grid(row=3, column=1, sticky=Tkinter.W)

        # 选择结束日期
        self.label2 = Tkinter.Label(self.root, text='请输入结束日期').grid(row=4, column=1, sticky=Tkinter.W)
        self.input2 = Tkinter.StringVar()
        self.entry2 = Tkinter.Entry(self.root, textvariable=self.input2)
        self.input2.set(self.current_month + ' 20:00')
        self.entry2.grid(row=5, column=1, sticky=Tkinter.W)

        # 选择机种下拉框
        self.label3 = Tkinter.Label(self.root, text='请选择机种名称').grid(row=2, column=2, sticky=Tkinter.W)
        self.input3 = Tkinter.StringVar()
        self.box1 = Combobox(self.root, textvariable=self.input3, state='readonly')
        self.box1['values'] = self.line
        self.box1.current(0)
        self.box1.grid(row=3, column=2, sticky=Tkinter.W)

        # 选择料号下拉框
        self.label4 = Tkinter.Label(self.root, text='请选择料号').grid(row=4, column=2, sticky=Tkinter.W)
        self.input4 = Tkinter.StringVar()
        self.box2 = Combobox(self.root, textvariable=self.input4, state='readonly')
        self.box2['values'] = self.product
        self.box2.current(0)
        self.box2.grid(row=5, column=2, sticky=Tkinter.W)

        # 分割线
        Tkinter.Label(self.root).grid(row=6, column=1)

        # 事件按钮
        self.entry_button = Tkinter.Button(self.root, text='确认', command=self.thread_open).grid(row=7, column=1, sticky=Tkinter.E)
        self.quit_button = Tkinter.Button(self.root, text='清空日期', command=self.erase_user_info).grid(row=7, column=1, sticky=Tkinter.W)
        self.quit_button = Tkinter.Button(self.root, text='退出', command=self.quit_gui, bg='red', fg='white').grid(row=7, column=2, sticky=Tkinter.E)

    def erase_user_info(self):
        for i in [self.input1, self.input2]:
            i.set('')

    @staticmethod
    def format_control(data='', format=None):
        format = format or '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'
        r = re.search(format, data)
        if r:
            return r.group()
        else:
            return None

    def get_start_date(self):
        start_date = self.format_control(self.input1.get())
        return start_date

    def get_end_date(self):
        end_date = self.format_control(self.input2.get())
        return end_date

    def get_line_data(self):
        line = self.input3.get()
        return line

    def get_product_date(self):
        product = self.input4.get()
        return product

    def quit_gui(self):
        # self.crawler.quit_browser()
        self.root.quit()

    def handle_browser(self):
        # get label info
        start_date = self.get_start_date()
        end_date = self.get_end_date()
        line_data = self.get_line_data()
        product_data = self.get_product_date()

        if start_date and end_date:
            tkMessageBox.showinfo('提示', '输入成功，请点击确定继续...')
            # run browser
            self.crawler.open_url(start_date, end_date, line_data, product_data)
        else:
            tkMessageBox.showwarning('警告', '您输入的时间格式不对\n请重新输入，谢谢！')

    def thread_open(self):
        # 多线程操作GUI
        threading.Thread(target=self.handle_browser, args=()).start()


if __name__ == '__main__':
    magic = Magic_gui(url='http://10.132.32.116')
    root = magic.root
    # 让GUI始终处于居中位置
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    root.geometry('+%d+%d' % (x, y))
    root.mainloop()
