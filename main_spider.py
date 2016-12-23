from html_parser import HtmlParser
from store import Saver
from url_manager import UrlManager
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
    """调度类，控制运行流程"""

    def __init__(self, max_tasks=10, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.parser = HtmlParser()
        self.saver = Saver()
        self.url_manager = UrlManager()

        self.max_tasks = max_tasks

        # 初始化队列
        if not self.url_manager:
            self.url_manager.put("http://company.yellowurl.cn/")

    async def work(self):
        while self.url_manager:
            try:
                url = self.url_manager.get()
                urls_or_data = await self.parser.parse_url(url)

                if isinstance(urls_or_data, list):
                    self.url_manager.put_many(urls_or_data)
                else:
                    self.saver.save(urls_or_data)
                self.url_manager.complete(url)
            except errors.DataBaseNull:
                await asyncio.sleep(0.01)
                continue
            except errors.DownloadFailed:
                logger.error(url + "下载失败")
            except errors.WrongUrl:
                self.url_manager.complete(url)
                logger.error("错误的url: " + url)
            except errors.ExtractDataFailed:
                logger.error(url + "提取数据失败")
            except errors.SaveDataFailed:
                logger.error(url + "存储数据失败")

    def close(self):
        """释放资源"""
        self.saver.close()

    async def crawl(self):
        workers = [asyncio.ensure_future(self.work(), loop=self.loop)
                   for _ in range(self.max_tasks)]
        await asyncio.gather(*workers)

        self.close()

    def print_log(self, interval=60):
        minutes = 0
        while True:
            time.sleep(interval)
            minutes += 1
            logger.info("-------爬取{}个网页({}/min)， 保存{}条数据({}/min)".
                        format(self.parser.downloader.download_number, self.parser.downloader.download_number // minutes,
                               self.saver.num, self.saver.num // minutes) +
                        " 用时{}分钟".format(minutes) + "-------")


if __name__ == '__main__':
    from threading import Thread

    loop = asyncio.get_event_loop()
    s = MainSpider(max_tasks=1000, loop=loop)

    t = Thread(target=s.print_log, daemon=True)
    t.start()

    loop.run_until_complete(s.crawl())
