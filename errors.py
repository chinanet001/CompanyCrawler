class ExtractDataFailed(BaseException):
    """提取数据失败"""
    pass


class SaveDataFailed(BaseException):
    """存储数据失败"""
    pass


class DataBaseNull(BaseException):
    """数据库暂时为空，用于阻塞的实现"""
    pass


class DownloadFailed(BaseException):
    """下载页面失败"""
    pass
