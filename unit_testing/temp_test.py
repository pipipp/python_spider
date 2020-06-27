# -*- coding:utf-8 -*-
import requests
import json
from tkinter import *


__author__ = 'Evan'


class Translate(object):
    def __init__(self, input_str, from_language, to_language):
        self.input_str = input_str  # 要翻译的字符串
        self.from_language = from_language  # 要翻译的语言
        self.to_language = to_language  # 翻译后的语言
        # 定义一个字典，用来替换接收到的语言变为post的参数
        self.replace_dic = {'自动': 'Auto', '中文': 'zh-CH', '英语': 'en', '日语': 'ja', '韩语': 'ko', '法语': 'fr',
                            '俄语': 'ru', '西班牙语': 'es', '葡萄牙语': 'pt', '越南语': 'vi', '德语': 'de',
                            '印尼语': 'id', '阿拉伯语': 'ar'}

    def spider(self):
        # 请求头
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '38',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'aidemo.youdao.com',
            'Origin': 'http://ai.youdao.com',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/64.0.3282.186 Safari/537.36',
            'Referer': 'http://ai.youdao.com/product-fanyi-text.s',
        }
        # 请求链接
        url = 'https://aidemo.youdao.com/trans'
        # 请求参数
        payload = {'q': self.input_str, 'from': self.replace_dic[self.from_language], 'to': self.replace_dic[self.to_language]}
        try:
            response = requests.post(url, data=payload, headers=headers)  # 请求数据
        except Exception:
            return '请求出错'
        data = json.loads(response.text)  # 将数据转为json格式
        return data['translation'][0]  # 返回翻译后的字符串


class App:
    def __init__(self, windows):
        windows.geometry("300x240")
        windows.title("翻译软件")  # 设置标题
        # 设置第一行
        self.label = Label(windows, text="要翻译的单词").grid(row=0, column=0)  # 设置标签在第一行第一列
        self.e = Entry(windows, show=None, width=30)
        self.e.grid(row=0, column=1)  # 设置输入框在第一行第二列
        # 设置第二行
        self.label2 = Label(windows, text="要翻译的语言").grid(row=1, column=0)  # 设置标签在第二行第一列
        self.e2 = Entry(windows, show=None, width=30)
        self.e2.grid(row=1, column=1)  # 设置输入框在第二行第二列
        # 设置第三行
        self.label3 = Label(windows, text="翻译后的语言").grid(row=2, column=0)  # 设置标签在第三行第一列
        self.e3 = Entry(windows, show=None, width=30)
        self.e3.grid(row=2, column=1)  # 设置输入框在第三行第二列
        # 设置第四行
        self.label4 = Label(windows, text="翻译后的语言").grid(row=3, column=0)  # 设置标签在第四行第一列
        self.t = Text(windows, height=10, width=30)  # 设置文本框在第四行第二列
        self.t.grid(row=3, column=1)
        Button(windows, text="翻译", command=self.translate).grid(row=4, column=1)   # 设置按钮在第五行第二列

    def translate(self):
        # 判断三个输入框是否都有值
        if self.e.get() and self.e2.get() and self.e3.get():
            # 调用Translate翻译类，传入 要翻译的字符串， 要翻译的语言， 翻译后的语言
            x = Translate(self.e.get().strip(), self.e2.get().strip(), self.e3.get().strip())
            result = x.spider()  # 调用翻译类的spider方法，返回翻译结果
            self.t.delete(1.0, 'end')  # 每次清空文本框
            self.t.insert("end", result)  # 将翻译结果显示在文半框


# 创建一个toplevel的根窗口，并把它作为参数实例化app对象
windows = Tk()
app = App(windows)

# 开始主事件循环
windows.mainloop()
