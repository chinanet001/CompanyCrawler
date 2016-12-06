class Request:

    def __init__(self, url, callback=None):
        self.url = url
        self.callback = callback

    def __eq__(self, other):
        """
        判断两个对象是否相等
        默认是使用对象地址判断
        此处改为用url和callback来判断
        :param other: 另一个对象
        :return:
        """
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)
