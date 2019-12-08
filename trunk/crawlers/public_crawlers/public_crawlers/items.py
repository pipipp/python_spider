# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BianItem(scrapy.Item):
    """
    1. title       图片标题
    2. image_url   图片链接
    """
    title = scrapy.Field()
    image_url = scrapy.Field()


class LagouItem(scrapy.Item):
    """
    From ajax information
    1.  company_fullname         公司名称
    2.  company_size             公司人数
    3.  company_label_list       公司标签
    4.  industry_field           行业领域
    5.  finance_stage            融资阶段
    6.  city                     城市
    7.  district                 区域
    8.  salary                   薪水
    9.  work_year                工作年限
    10. job_nature               工作性质
    11. education                学历要求
    12. position_advantage       职位诱惑
    13. line_station             路线站点

    From html information
    14. work_address             工作地址
    15. job_description          职位描述
    """
    company_fullname = scrapy.Field()
    company_size = scrapy.Field()
    company_label_list = scrapy.Field()
    industry_field = scrapy.Field()
    finance_stage = scrapy.Field()
    city = scrapy.Field()
    district = scrapy.Field()
    salary = scrapy.Field()
    work_year = scrapy.Field()
    job_nature = scrapy.Field()
    education = scrapy.Field()
    position_advantage = scrapy.Field()
    line_station = scrapy.Field()
    work_address = scrapy.Field()
    job_description = scrapy.Field()
