# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LagouItem(scrapy.Item):
    """
    position_name            职位名称
    salary                   薪水
    education                学历要求
    company_fullname         公司名称
    work_address             工作地址
    work_year                工作年限
    job_nature               工作性质
    position_advantage       职位诱惑
    position_description     职位描述
    city                     城市
    district                 区域
    company_size             公司人数
    company_label_list       公司标签
    industry_field           行业领域
    finance_stage            融资阶段
    """
    position_name = scrapy.Field()
    salary = scrapy.Field()
    education = scrapy.Field()
    company_fullname = scrapy.Field()
    work_address = scrapy.Field()
    work_year = scrapy.Field()
    job_nature = scrapy.Field()
    position_advantage = scrapy.Field()
    position_description = scrapy.Field()
    city = scrapy.Field()
    district = scrapy.Field()
    company_size = scrapy.Field()
    company_label_list = scrapy.Field()
    industry_field = scrapy.Field()
    finance_stage = scrapy.Field()
