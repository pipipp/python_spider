# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class ZhihuPipeline(object):
    """
    清洗过滤数据
    """
    def process_item(self, item, spider):
        """
        删除多余的空白行
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
        :return: 类实例
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
        保存所有数据到Mongodb
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
