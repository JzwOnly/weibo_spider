# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from Weibo_spider.weibo.weibo.items import InformationItem, TweetsItem, RelationshipsItem, SeedsItem
import logging
logger = logging.getLogger(__name__)


class MongoDBPipleline(object):
    def __init__(self):
        clinet = pymongo.MongoClient("localhost", 27017)
        db = clinet["weibo"]
        self.Information = db["Information"]
        self.Tweets = db["Tweets"]
        self.Relationships = db["Relationships"]
        self.Seeds = db["Seeds"]

    def process_item(self, item, spider):
        """判断item的类型, 进行相应的处理存入数据库"""
        if isinstance(item, InformationItem):
            try:
                uid = dict(item)["_id"]
                result = list(self.Information.find({'_id': uid}))
                if len(result) == 0:
                    self.Information.insert(dict(item))
                else:
                    logger.warning("用户id：{0} 已经录入过数据库了".format(uid))
            except Exception as e:
                logger.error('Information 存入出错', e)

        elif isinstance(item, RelationshipsItem):
            try:
                self.Relationships.insert(dict(item))
            except Exception as e:
                logger.error('Relationships 存入出错', e)
        elif isinstance(item, TweetsItem):
            try:
                id = dict(item)["_id"]
                result = list(self.Tweets.find({'_id': id}))
                if len(result) == 0:
                    self.Tweets.insert(dict(item))
                else:
                    logger.warning("该条微博：{0} 已经录入过数据库了".format(id))
            except Exception as e:
                logger.error('Tweets 存入出错', e)
        elif isinstance(item, SeedsItem):
            try:
                uids = item["Uids"]
                Depth_num = item["Depth_num"]
                for uid in uids:
                    document = {
                        "uid": uid,
                        "Depth_num": Depth_num
                    }
                    self.Seeds.insert(document)
            except Exception as e:
                logger.error('Seeds 存入出错', e)
