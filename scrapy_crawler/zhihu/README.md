爬取知乎网站的指定文章内容
===
**使用方法：**
* 填写配置参数（配置参数在zhihu文件夹下的`constants.py`）

*--constatns*

![配置参数](https://github.com/pipipp/python_spider/blob/master/trunk/python_scripts/spiders/scrapy_crawler/cralwer_projects/zhihu/images/config.PNG)

* 填写完配置参数后直接运行main.py即可
* 运行结束后会把爬虫结果写入到MongoDB数据库并依次生成TXT文件在result文件夹下

**效果展示：**

*--MongoDB数据库*

![MongoDB数据库](https://github.com/pipipp/python_spider/blob/master/trunk/python_scripts/spiders/scrapy_crawler/cralwer_projects/zhihu/images/zhihu_MongoDB.PNG)

*--result* (TXT)

![wallpapers](https://github.com/pipipp/python_spider/blob/master/trunk/python_scripts/spiders/scrapy_crawler/cralwer_projects/zhihu/images/zhihu_folder.PNG)
