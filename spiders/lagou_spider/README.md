# 拉勾网爬虫 + 职位数据分析

> 爬取拉钩招聘网站的公司招聘信息

**运行过程：**  
1. 多线程爬取指定职位的所有公司招聘信息   
字段如下：  
公司名称    职位名称   薪水     学历要求    工作地址    工作年限    工作性质    职位诱惑  
职位描述    城市       区域     公司人数    公司标签    行业领域    融资阶段  
2. 生成所有公司的招聘详情数据表（excel）  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/excel.JPG)
3. 绘制薪水比例饼图，分析行业薪资标准  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/薪水比例饼图-爬虫开发.jpg)
4. 绘制词云图，分析行业规模现状（薪水、工作地址、工作年限、职位诱惑、职位描述、公司人数、公司标签、行业领域）  
* 薪水  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/爬虫开发词云图-薪水.jpg)
* 工作地址  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/爬虫开发词云图-工作地址.jpg)
* 工作年限  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/爬虫开发词云图-工作年限.jpg)
* 职位诱惑  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/爬虫开发词云图-职位诱惑.jpg)
* 职位描述  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/爬虫开发词云图-职位描述.jpg)
* 公司人数  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/爬虫开发词云图-公司人数.jpg)
* 公司标签  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/爬虫开发词云图-公司标签.jpg)
* 行业领域  
![Running](https://github.com/pipipp/python-spiders/blob/master/spiders/lagou_spider/show/爬虫开发词云图-行业领域.jpg)
