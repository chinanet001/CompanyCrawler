
class Request:

    def __init__(self, url, callback=None):
        self.url = url
        self.callback = callback

    def __str__(self):
        return self.url
