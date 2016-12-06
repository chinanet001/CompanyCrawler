import logging
import aiomysql

logger = logging.getLogger("crawlLog")


class Storer:
    def __init__(self):
        # 连接数据库
        # 将要执行的添加数据语句
        self.sql = "INSERT IGNORE INTO company1(name, classify, location, scale, capital, year, " \
                   "dataAuthentication, margin, sale, products, procurement, mainIndustry) " \
                   "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.num = 0

    async def save(self, data):
        try:
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='wang19960307',
                                          db='kraken', charset="utf8",
                                          use_unicode=True)
            async with conn.cursor() as cur:
                await cur.execute(self.sql, data)
                await conn.commit()
            conn.close()
            self.num += 1
            # logger.info(" 存储 " + data[0] + " 的信息")
        except Exception as e:
            logger.error(data[0] + " 存储失败" + e)

    def close(self):
        pass
