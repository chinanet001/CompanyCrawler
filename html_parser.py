from request import Request
from lxml import etree
import logging

logger = logging.getLogger("crawlLog")


class HtmlParser:
    """
    解析器类，定义各层页面的解析函数
    """
    def parse_index(self, body):
        """
        解析首页：'http://company.yellowurl.cn/'
        :param body: 网页的字符串
        """
        html = self._get_dom(body)
        for category_url in html.xpath("//div[@id='category']//a[@target='_blank']/@href"):
            category_url += "1/index.html"
            yield Request(category_url, callback=self.parse_category)

    def parse_category(self, body):
        """
        分类目录页面的解析
        :param body: 网页字符串
        :return:
        """
        html = self._get_dom(body)
        # 未访问的公司链接
        for company_url in html.xpath("//ul[@class='searchResultList']//a[@class='comtitle']/@href"):
            company_url += "introduce/"
            yield Request(company_url, callback=self.parse_company)

        # 未访问的目录链接
        for next_page in html.xpath("//input[@id='destoon_next']/@value"):
            yield Request(next_page, callback=self.parse_category)

    def parse_company(self, body):
        """
        解析公司介绍页，获取需要的数据
        :param body: 网页内容
        :return: 公司信息数据
        """
        try:
            html = self._get_dom(body)
            info = html.xpath("//div[@class='main_body'][2]")[0]

            name = ''.join(info.xpath("//td[text()='公司名称：']/following-sibling::td[1]//text()")).strip()
            classify = ''.join(info.xpath("//td[text()='公司类型：']/following-sibling::td[1]//text()")).strip()
            location = ''.join(info.xpath("//td[text()='所 在 地：']/following-sibling::td[1]//text()")).strip()
            scale = ''.join(info.xpath("//td[text()='公司规模：']/following-sibling::td[1]//text()")).strip()
            capital = ''.join(info.xpath("//td[text()='注册资本：']/following-sibling::td[1]//text()")).strip()
            year = ''.join(info.xpath("//td[text()='注册年份：']/following-sibling::td[1]//text()")).strip()
            dataAuthentication = ''.join(info.xpath("//td[text()='资料认证：']/following-sibling::td[1]//text()")).strip()
            margin = ''.join(info.xpath("//td[text()='保 证 金：']/following-sibling::td[1]//text()")).strip()
            sale = ''.join(info.xpath("//td[text()='经营范围：']/following-sibling::td[1]//text()")).strip()
            products = ''.join(info.xpath("//td[text()='销售的产品：']/following-sibling::td[1]//text()")).strip()
            procurement = ''.join(info.xpath("//td[text()='采购的产品：']/following-sibling::td[1]//text()")).strip()
            mainIndustry = ''.join(info.xpath("//td[text()='主营行业：']/following-sibling::td[1]//text()")).strip()

            data = [name, classify, location, scale, capital, year, dataAuthentication,
                    margin, sale, products, procurement, mainIndustry]
            yield data
        except Exception as e:
            logger.error("提取数据失败" + e)

    def _get_dom(self, body):
        dom = etree.HTML(body)
        return dom
