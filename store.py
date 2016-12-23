import logging
import pymongo
from errors import SaveDataFailed

logger = logging.getLogger("crawlLog")


class Saver:
    """
    存储类，提供数据存储功能
    使用mongoDB数据库
    """
    def __init__(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.CompanyCrawler
        self.collection = self.db.test

        self.num = 0  # 存储的数据量

    def save(self, data):
        """存储数据"""
        try:
            self.collection.insert(data)
            self.num += 1
        except BaseException:
            raise SaveDataFailed()

    def close(self):
        """关闭数据库连接"""
        self.client.close()
