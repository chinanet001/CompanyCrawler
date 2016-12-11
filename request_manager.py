import pymongo
from pymongo import errors
import pickle
from errors import DataBaseNull


class RequestManager:
    """爬虫队列管理类"""
    OUTSTANDING = 1  # 初始状态
    PROCESSING = 2  # 正在下载状态
    COMPLETE = 3  # 下载完成状态

    def __init__(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.CompanyCrawler
        self.requests = self.db.requests

        self.change_status(self.PROCESSING, self.OUTSTANDING)

    def __bool__(self):
        record = self.requests.find_one(
            {'status': {'$ne': self.COMPLETE}})
        return True if record else False

    def get(self):
        record = self.requests.find_and_modify(
            query={'status': self.OUTSTANDING},
            update={'$set': {'status': self.PROCESSING}}
        )
        if record:
            return pickle.loads(record['_id'])
        else:
            raise DataBaseNull()

    def put(self, request):
        req = pickle.dumps(request)
        try:
            self.requests.insert({"_id": req, "status": self.OUTSTANDING})
        except errors.DuplicateKeyError:
            pass

    def complete(self, request):
        self.requests.update(
            {'_id': pickle.dumps(request)},
            {'$set': {'status': self.COMPLETE}})

    def change_status(self, old_status, new_status):
        """改变状态"""
        self.requests.update(
            {'status': old_status},
            {'$set': {'status': new_status}})
