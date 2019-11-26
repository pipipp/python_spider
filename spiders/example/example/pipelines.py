# -*- coding: utf-8 -*-
import pymongo
from scrapy.exceptions import DropItem


class TextPipeline(object):
    """
    自定义类
    """
    def __init__(self):
        self.limit = 50

    def process_item(self, item, spider):  # TODO 必须要实现的方法（必须返回 Item 类型的值或者抛出一个 DropItem 异常）
        if item['text']:
            if len(item['text']) > self.limit:  # 对超过50个字节长度的字符串进行切割
                item['text'] = item['text'][:self.limit].rstrip() + '...'
            return item
        else:
            return DropItem('Missing Text')  # TODO 如果抛出此异常，会丢弃此Item，不再进行处理


class MongoPipeline(object):
    """
    自定义类
    """
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        # TODO Pipelines的准备工作，通过crawler可以拿到全局配置的每个配置信息
        # 使用类方法，返回带有MONGO_URI和MONGO_DB值的类对象
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),  # MONGO_URI的值从settings.py获取
            mongo_db=crawler.settings.get('MONGO_DB')  # MONGO_DB的值从settings.py获取
        )

    def open_spider(self, spider):
        # TODO 当 Spider 开启时，这个方法会被调用
        self.client = pymongo.MongoClient(self.mongo_uri)  # 打开Mongodb连接
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):  # TODO 必须要实现的方法（必须返回 Item 类型的值或者抛出一个 DropItem 异常）
        name = item.__class__.__name__  # 创建一个集合，name='ExampleItem'
        self.db[name].insert_one(dict(item))  # 插入数据到ExampleItem集合中
        return item

    def close_spider(self, spider):
        # TODO 当 Spider 关闭时，这个方法会被调用
        self.client.close()  # 关闭Mongodb连接
