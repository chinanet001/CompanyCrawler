import aiohttp
import logging
from errors import DownloadFailed

logger = logging.getLogger("crawlLog")


class HtmlDownloader:
    def __init__(self):
        self.download_number = 0

    async def download(self, request):
        """
        根据请求下载网页
        :param request: 下载请求
        :return: 网页字符串
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(request.url) as response:
                    if response.status == 200:
                        body = await response.text()  # 获取请求的响应
                        logger.info(request.url + " 下载完成")
                        self.download_number += 1
                        return body
        except BaseException:
            raise DownloadFailed()
