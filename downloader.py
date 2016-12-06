import aiohttp
import logging


logger = logging.getLogger("crawlLog")


class HtmlDownloader:
    def __init__(self, loop=None):
        self.conn = aiohttp.TCPConnector(limit=1000)
        self.session = aiohttp.ClientSession(connector=self.conn, loop=loop)
        self.download_number = 0

    async def download(self, request):
        """
        根据请求下载网页
        :param request: 下载请求
        :return: 网页字符串
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(request.url) as response:
                if response.status == 200:
                    body = await response.text()  # 获取请求的响应
                    # logger.info(request.url + " 下载完成")
                    self.download_number += 1
                    return body
                else:
                    logger.error(request.url + "下载失败")

    def close(self):
        """
        关闭客户端会话
        :return:
        """
        self.session.close()
