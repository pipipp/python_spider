# -*- coding: utf-8 -*-
import scrapy
import time
import json

from ..items import LagouItem
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from urllib.parse import quote


class BianWallpaperSpider(scrapy.Spider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_url = 'https://www.lagou.com/jobs/list_{}?labelWords=&fromSearch=true&suginput='
    search_url = 'https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false'

    SEARCH_INFO = '爬虫开发工程师'  # 工作职位
    CITY_INFO = '深圳'  # 工作地点

    def start_requests(self):
        """
        构造初始请求，获取拉钩网首页Cookies
        :return:
        """
        return [Request(url=self.start_url.format(quote(self.SEARCH_INFO)), callback=self.after_requests)]

    def after_requests(self, response):
        """
        构造获取招聘岗位信息的AJAX请求，默认开始为第一页
        :param response:
        :return:
        """
        data = {
            'first': 'false',
            'pn': '1',  # 页数
            'kd': self.SEARCH_INFO
        }
        yield FormRequest(url=self.search_url.format(quote(self.CITY_INFO)), formdata=data,
                          meta={'page': 1}, callback=self.parse_company)

    def parse_company(self, response):
        """
        解析公司信息
        :param response:
        :return:
        """
        result = json.loads(response.text)['content']['positionResult']['result']
        if result:
            for each_company in result:
                company_details = dict(
                    position_name=each_company.get('positionName'),
                    company_fullname=each_company.get('companyFullName'),
                    company_size=each_company.get('companySize'),
                    company_label_list=[str(i) for i in each_company.get('companyLabelList', [])],
                    industry_field=each_company.get('industryField'),
                    finance_stage=each_company.get('financeStage'),
                    city=each_company.get('city'),
                    district=each_company.get('district'),
                    salary=each_company.get('salary'),
                    work_year=each_company.get('workYear'),
                    job_nature=each_company.get('jobNature'),
                    education=each_company.get('education'),
                    position_advantage=each_company.get('positionAdvantage'),
                    line_station=each_company.get('linestaion'),
                )
                html_id = each_company.get('positionId')
                show_id = json.loads(response.text)['content']['showId']
                next_url = 'https://www.lagou.com/jobs/{}.html?show={}'.format(html_id, show_id)
                # 保存当前页面信息
                yield Request(url=next_url, meta={'company_details': company_details},
                              callback=self.parse_job)
                # 进行下一页的请求
                next_page = response.meta['page'] + 1
                data = {
                    'first': 'false',
                    'pn': str(next_page),  # 页数每次增加1
                    'kd': self.SEARCH_INFO
                }
                yield FormRequest(url=self.search_url.format(quote(self.CITY_INFO)), formdata=data,
                                  meta={'page': next_page}, callback=self.parse_company)

    def parse_job(self, response):
        """
        解析工作地址和职位描述
        :return:
        """
        item = LagouItem()
        company_details = response.meta['company_details']
        # 职位信息
        item['position_name'] = company_details['position_name']
        item['salary'] = company_details['salary']
        item['education'] = company_details['education']
        item['work_year'] = company_details['work_year']
        item['job_nature'] = company_details['job_nature']
        item['position_advantage'] = company_details['position_advantage']
        item['position_description'] = ''.join(response.css('div .job-detail ::text').extract())
        # 公司信息
        item['work_address'] = response.css('div .work_addr ::text').extract()[-3]
        item['line_station'] = company_details['line_station']
        item['city'] = company_details['city']
        item['district'] = company_details['district']
        item['company_fullname'] = company_details['company_fullname']
        item['company_size'] = company_details['company_size']
        item['company_label_list'] = company_details['company_label_list']
        item['industry_field'] = company_details['industry_field']
        item['finance_stage'] = company_details['finance_stage']
        yield item
