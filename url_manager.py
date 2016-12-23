import pymongo
from pymongo import errors
from errors import DataBaseNull
import asyncio


class UrlManager:
    """爬虫队列管理类"""
    # 请求的状态
    OUTSTANDING = 1  # 待爬状态
    PROCESSING = 2  # 正在处理状态
    COMPLETE = 3  # 下载完成状态
    WRONG = 4  # 错误的url

    def __init__(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.CompanyCrawler
        self.urls = self.db.urls

        # 将上次运行时未完成的请求状态改为待爬状态
        self.change_status(self.PROCESSING, self.OUTSTANDING)
        # print(self.urls.find({'status': 1}).count())
        self.queue = asyncio.Queue()

    def __bool__(self):
        """是否还有请求需要爬取"""
        record = self.urls.find_one(
            {'status': {'$lt': self.COMPLETE}})
        return True if record else False

    def get(self):
        """获取一个待爬请求"""
        record = self.urls.find_and_modify(
            query={'status': self.OUTSTANDING},
            update={'$set': {'status': self.PROCESSING}}
        )
        if record:
            return record['_id']
        else:
            raise DataBaseNull()

    def put(self, url):
        try:
            self.urls.insert_one({"_id": url, "status": self.OUTSTANDING})
        except errors.DuplicateKeyError:
            pass

    def put_many(self, urls):
        if len(urls) <= 0 or urls is None:
            return
        documents = [{'_id': url, 'status': self.OUTSTANDING} for url in urls]
        try:
            self.urls.insert_many(documents, ordered=False)
        except errors.BulkWriteError:
            pass

    def complete(self, url):
        self.urls.update(
            {'_id': url},
            {'$set': {'status': self.COMPLETE}})

    def change_status(self, old_status, new_status):
        """改变状态"""
        self.urls.update(
            {'status': old_status},
            {'$set': {'status': new_status}}, multi=True)
