from downloader import HtmlDownloader
from html_parser import HtmlParser
from store import Storer
from request import Request
from request_manager import RequestManager
import asyncio
import logging
import time
import errors

# 日志配置
logger = logging.getLogger("crawlLog")

console = logging.StreamHandler()
console.setLevel(logging.INFO)

fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
console.setFormatter(fmt)

logger.addHandler(console)
logger.setLevel(logging.INFO)


class MainSpider:
    def __init__(self, max_tasks=10, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.downloader = HtmlDownloader()
        self.parser = HtmlParser()
        self.storer = Storer()
        self.request_manager = RequestManager()

        self.max_tasks = max_tasks

        # 初始化队列
        if not self.request_manager:
            self.request_manager.put(Request("http://company.yellowurl.cn/",
                                             self.parser.parse_index))

    async def work(self):
        while self.request_manager:
            try:
                request = self.request_manager.get()
                html = await self.downloader.download(request)
                for req_or_data in request.callback(html):
                    if isinstance(req_or_data, Request):
                        self.request_manager.put(req_or_data)
                    else:
                        self.storer.save(req_or_data)
                self.request_manager.complete(request)
            except errors.DataBaseNull:
                await asyncio.sleep(0.01)
                continue
            except errors.DownloadFailed:
                logger.error(request.url + "下载失败")
            except errors.ExtractDataFailed:
                logger.error(request.url + "提取数据失败")
            except errors.SaveDataFailed:
                logger.error(request.url + "存储数据失败")

    def close(self):
        """释放资源"""
        pass

    async def bound_worker(self, sem):
        async with sem:
            await self.work()

    async def crawl(self):
        try:
            sem = asyncio.Semaphore(1000)
            workers = [asyncio.ensure_future(self.bound_worker(sem), loop=self.loop)
                       for _ in range(self.max_tasks)]
            await asyncio.gather(*workers)
        except Exception as e:
            print("something was wrong")
            raise e
        finally:
            self.close()

    def print_log(self, interval=60):
        minutes = 0
        while True:
            time.sleep(interval)
            minutes += 1
            logger.info("-------爬取{}个网页({}/min)， 保存{}条数据({}/min)".
                        format(self.downloader.download_number, self.downloader.download_number // minutes,
                               self.storer.num, self.storer.num // minutes) +
                        " 用时{}分钟".format(minutes) + "-------")

if __name__ == '__main__':
    from threading import Thread

    loop = asyncio.get_event_loop()
    s = MainSpider(max_tasks=10000, loop=loop)

    t = Thread(target=s.print_log, daemon=True)
    t.start()

    loop.run_until_complete(s.crawl())
