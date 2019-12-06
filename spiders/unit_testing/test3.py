"""
拉勾网selenium爬虫
"""
import urllib.parse
import time
import json
import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException


class Lagou(object):
    # 初始化
    def init(self):
        self.data = list()
        self.isEnd = False
        opt = webdriver.chrome.options.Options()
        opt.set_headless()
        self.browser = webdriver.Chrome(chrome_options = opt)
        self.wait = WebDriverWait(self.browser,10)
        self.position = input('请输入职位：')
        self.browser.get('https://www.lagou.com/jobs/list_' + urllib.parse.quote(self.position) + '?labelWords=&fromSearch=true&suginput=')
        cookie = input('请输入cookie：')
        for item in cookie.split(';'):
            k,v = item.strip().split('=')
            self.browser.add_cookie({'name':k,'value':v})

    # 爬取网页数据
    def parse_page(self):
        try:
            link = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//a[@class="position_link"]')))
            link = [item.get_attribute('href') for item in link]
            position = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//a[@class="position_link"]/h3')))
            position = [item.text for item in position]
            city = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//a[@class="position_link"]/span/em')))
            city = [item.text for item in city]
            ms_we_eb = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[@class="p_bot"]/div[@class="li_b_l"]')))
            monthly_salary = [item.text.split('/')[0].strip().split(' ')[0] for item in ms_we_eb]
            working_experience = [item.text.split('/')[0].strip().split(' ')[1] for item in ms_we_eb]
            educational_background = [item.text.split('/')[1].strip() for item in ms_we_eb]
            company_name = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[@class="company_name"]/a')))
            company_name = [item.text for item in company_name]
            print(link)
            print(position)
            print(city)
            print(ms_we_eb)
            print(monthly_salary)
        except TimeoutException:
            self.isEnd = True
        except StaleElementReferenceException:
            time.sleep(3)
            self.parse_page()
        else:
            temp = list(map(lambda a,b,c,d,e,f,g: {'link':a,'position':b,'city':c,'monthly_salary':d,'working_experience':e,'educational_background':f,'company_name':g}, link, position, city, monthly_salary, working_experience, educational_background, company_name))
            self.data.extend(temp)

    # 进行翻页操作
    def turn_page(self):
        try:
            pager_next = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'pager_next')))
        except TimeoutException:
            self.isEnd = True
        else:
            pager_next.click()
            time.sleep(3)

    # 爬取数据
    def crawl(self):
        count = 0
        while not self.isEnd :
            count += 1
            print('正在爬取第 ' + str(count) + ' 页 ...')
            self.parse_page()
            self.turn_page()
        print('爬取结束')

    # 保存数据
    def save(self):
        with open('lagou.json','w',encoding='utf-8') as f:
            for item in self.data:
                json.dump(item,f,ensure_ascii=False)

    # 数据可视化
    def draw(self):
        count_we = {'经验不限':0,'经验应届毕业生':0,'经验1年以下':0,'经验1-3年':0,'经验3-5年':0,'经验5-10年':0}
        total_we = {'经验不限':0,'经验应届毕业生':0,'经验1年以下':0,'经验1-3年':0,'经验3-5年':0,'经验5-10年':0}
        count_eb = {'不限':0,'大专':0,'本科':0,'硕士':0,'博士':0}
        total_eb = {'不限':0,'大专':0,'本科':0,'硕士':0,'博士':0}
        for item in self.data:
            count_we[item['working_experience']] += 1
            count_eb[item['educational_background']] += 1
            try:
                li = [float(temp.replace('k','000')) for temp in item['monthly_salary'].split('-')]
                total_we[item['working_experience']] += sum(li) / len(li)
                total_eb[item['educational_background']] += sum(li) / len(li)
            except:
                count_we[item['working_experience']] -= 1
                count_eb[item['educational_background']] -= 1
        # 解决中文编码问题
        plt.rcParams['font.sans-serif'] = ['SimHei']
        # 工作经验-职位数量
        plt.title(self.position)
        plt.xlabel('工作经验')
        plt.ylabel('职位数量')
        x = ['经验不限','经验应届毕业生','经验1-3年','经验3-5年','经验5-10年']
        y = [count_we[item] for item in x]
        plt.bar(x,y)
        plt.show()
        # 工作经验-平均月薪
        plt.title(self.position)
        plt.xlabel('工作经验')
        plt.ylabel('平均月薪')
        x = list()
        y = list()
        for item in ['经验不限','经验应届毕业生','经验1-3年','经验3-5年','经验5-10年']:
            if count_we[item] != 0:
                x.append(item)
                y.append(total_we[item]/count_we[item])
        plt.bar(x,y)
        plt.show()
        # 学历-职位数量
        plt.title(self.position)
        plt.xlabel('学历')
        plt.ylabel('职位数量')
        x = ['不限','大专','本科','硕士','博士']
        y = [count_eb[item] for item in x]
        plt.bar(x,y)
        plt.show()
        # 学历-平均月薪
        plt.title(self.position)
        plt.xlabel('学历')
        plt.ylabel('平均月薪')
        x = list()
        y = list()
        for item in ['不限','大专','本科','硕士','博士']:
            if count_eb[item] != 0:
                x.append(item)
                y.append(total_eb[item]/count_eb[item])
        plt.bar(x,y)
        plt.show()


if __name__ == '__main__':
    obj = Lagou()
    obj.init()
    obj.crawl()
    obj.save()
    obj.draw()
