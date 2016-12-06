from downloader import HtmlDownloader
from html_parser import HtmlParser
from store import Storer
from request import Request
import asyncio
import logging
import time

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
        self.downloader = HtmlDownloader(self.loop)
        self.parser = HtmlParser()
        self.storer = Storer()

        self.visited_requests = set()
        self.unvisited_requests = asyncio.Queue()

        self.max_tasks = max_tasks

        self.unvisited_requests.put_nowait(Request("http://company.yellowurl.cn/", self.parser.parse_index))

    async def work(self):
        while True:
            new_request = await self.unvisited_requests.get()
            if new_request not in self.visited_requests:
                html = await self.downloader.download(new_request)
                # 该链接爬取完成，添加到爬取过的队列
                self.visited_requests.add(new_request)
                if new_request.callback:
                    for req_or_data in new_request.callback(html):
                        if isinstance(req_or_data, Request):
                            if req_or_data not in self.visited_requests:
                                await self.unvisited_requests.put(req_or_data)
                        else:
                            await self.storer.save(req_or_data)
                self.unvisited_requests.task_done()

    def close(self):
        """释放资源"""
        self.storer.close()
        self.downloader.close()

    async def crawl(self):
        try:
            workers = [asyncio.ensure_future(self.work(), loop=self.loop)
                       for _ in range(self.max_tasks)]
            await self.unvisited_requests.join()
            for worker in workers:
                worker.cancel()
        except Exception as e:
            print(e)
        finally:
            self.close()


def print_log(spider, interval=60):
    while True:
        logger.info("爬取{}个网页， 保存{}条数据".
                    format(spider.downloader.download_number, spider.storer.num))
        time.sleep(interval)

if __name__ == '__main__':
    from threading import Thread
    loop = asyncio.get_event_loop()
    s = MainSpider(500, loop=loop)

    t = Thread(target=print_log, args=(s,), daemon=True)
    t.start()

    loop.run_until_complete(s.crawl())
