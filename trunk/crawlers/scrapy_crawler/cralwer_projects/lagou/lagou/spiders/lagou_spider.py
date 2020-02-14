"""
爬取拉钩网站的指定招聘信息
"""
# -*- coding: utf-8 -*-
import time
import scrapy
import json

from ..items import LagouItem
from ..constants import SEARCH_INFO, CITY_INFO

from scrapy.http import Request, FormRequest
from urllib.parse import quote

__author__ = 'Evan'


class LagouSpider(scrapy.Spider):
    name = 'lagou_spider'
    allowed_domains = ['www.lagou.com']
    start_url = 'https://www.lagou.com/jobs/list_{}?labelWords=&fromSearch=true&suginput='
    search_url = 'https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false'

    def start_requests(self):
        """
        构造初始请求，获取拉钩网首页Cookies
        :return:
        """
        self.start_url = self.start_url.format(quote(SEARCH_INFO))
        return [Request(url=self.start_url, callback=self.after_requests)]

    def after_requests(self, response):
        """
        构造获取招聘岗位信息的AJAX请求
        :param response:
        :return:
        """
        data = {
            'first': 'false',
            'pn': '1',  # 页数
            'kd': SEARCH_INFO
        }
        return [FormRequest(url=self.search_url.format(quote(CITY_INFO)), formdata=data,
                            meta={'page': 1}, callback=self.parse)]

    def parse(self, response):
        """
        解析公司信息
        :param response:
        :return:
        """
        if json.loads(response.text).get('msg'):
            # 如果出现“您操作太频繁,请稍后再访问”的提示就等待3秒后再重新访问
            time.sleep(3)
            self.logger.error('Error msg: {}'.format(json.loads(response.text).get('msg')))
            headers = {
                'Referer': self.start_url
            }
            data = {
                'first': 'false',
                'pn': str(response.meta['page']),
                'kd': SEARCH_INFO,
                'sid': str(response.meta.get('sid'))
            }
            self.logger.warning('Now retry the page ({})'.format(response.meta['page']))
            return [FormRequest(url=self.search_url.format(quote(CITY_INFO)), headers=headers, formdata=data,
                                meta={'page': response.meta['page']}, dont_filter=True, callback=self.parse)]

        # 请求成功
        result = json.loads(response.text)['content']['positionResult'].get('result')
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
                    line_station=each_company.get('linestaion', 'None'),
                )
                html_id = each_company.get('positionId')
                show_id = json.loads(response.text)['content']['showId']
                next_url = 'https://www.lagou.com/jobs/{}.html?show={}'.format(html_id, show_id)
                yield Request(url=next_url, meta={'company_details': company_details}, callback=self.parse_job)

            # 进行下一页的请求
            next_page = response.meta['page'] + 1
            sid = json.loads(response.text)['content']['showId']
            headers = {
                'Referer': self.start_url
            }
            data = {
                'first': 'false',
                'pn': str(next_page),  # 页数每次增加1
                'kd': SEARCH_INFO,
                'sid': sid
            }
            self.logger.warning('Next page: {}'.format(next_page))
            yield FormRequest(url=self.search_url.format(quote(CITY_INFO)), headers=headers, formdata=data,
                              meta={'page': next_page, 'sid': sid}, dont_filter=True, callback=self.parse)

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
        item['company_fullname'] = company_details['company_fullname']
        item['work_address'] = str(response.css('div .work_addr ::text')
                                   .extract()[-3]).strip() + '[' + str(company_details['line_station']).strip() + ']'
        item['work_year'] = company_details['work_year']
        item['job_nature'] = company_details['job_nature']
        item['position_advantage'] = company_details['position_advantage']
        item['position_description'] = ''.join(response.css('div .job-detail ::text').extract())
        # 公司信息
        item['city'] = company_details['city']
        item['district'] = company_details['district']
        item['company_size'] = company_details['company_size']
        item['company_label_list'] = company_details['company_label_list']
        item['industry_field'] = company_details['industry_field']
        item['finance_stage'] = company_details['finance_stage']
        yield item
