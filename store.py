import logging
import pymongo
from errors import SaveDataFailed

logger = logging.getLogger("crawlLog")


class Storer:
    """
    存储类，提供数据存储功能
    使用mongoDB数据库
    """
    def __init__(self):
        self.duplicate_num = 0
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.CompanyCrawler
        self.collection = self.db.company
        self.num = 0  # 存储的数据量

    def save(self, data):
        try:
            self.collection.insert(data)
            self.num += 1
        except BaseException:
            raise SaveDataFailed()

    def close(self):
        self.client.close()
