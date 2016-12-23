class ExtractDataFailed(Exception):
    """提取数据失败"""
    pass


class SaveDataFailed(Exception):
    """存储数据失败"""
    pass


class DataBaseNull(Exception):
    """数据库暂时为空，用于阻塞的实现"""
    pass


class DownloadFailed(Exception):
    """下载页面失败"""
    pass


class WrongUrl(Exception):
    """url错误"""
    pass
