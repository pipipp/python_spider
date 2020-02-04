# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline


class TextPipeline(object):
    """
    清洗过滤数据
    """
    def process_item(self, item, spider):
        """
        删除两边多余的空白行
        :param item:
        :param spider:
        :return:
        """
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = value.strip()
            elif isinstance(value, (tuple, list)):
                item[key] = [i.strip() for i in value]
        return item


class ImagePipeline(ImagesPipeline):
    """
    图片下载
    """
    def file_path(self, request, response=None, info=None):
        """
        截取图片链接的最后一部分当作文件名
        :param request:
        :param response:
        :param info:
        :return:
        """
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

    def item_completed(self, results, item, info):
        """
        丢弃下载失败的Item
        :param results:
        :param item:
        :param info:
        :return:
        """
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image downloaded failed')
        return item

    def get_media_requests(self, item, info):
        """
        构建新的Request下载图片
        :param item:
        :param info:
        :return:
        """
        image_url = item['image_url']  # TODO 填入图片的下载链接地址
        yield Request(image_url)


class MongoPipeline(object):
    """
    保存所有数据到Mongodb
    """
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        """
        使用类方法，返回带有MONGO_URI和MONGO_DB值的类实例
        :param crawler:
        :return:
        """
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        """
        打开Mongodb连接
        :param spider:
        :return:
        """
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        """
        插入数据到Mongodb
        :param item:
        :param spider:
        :return:
        """
        name = item.__class__.__name__
        self.db[name].insert_one(dict(item))
        return item

    def close_spider(self, spider):
        """
        关闭Mongodb连接
        :param spider:
        :return:
        """
        self.client.close()
