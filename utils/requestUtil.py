import requests

class ReqHandler:
    def __init__(self, headers=None, *args, **kwargs):
        if not headers:
            headers = {
                "Content-Type": "application/json"
            }

        self.session = requests.Session()
        self.session.headers.update(headers)

    def post(self, url, payload):
        return self.session.post(url, data=payload)

    def get(self, url, params=None):
        return self.session.get(url, params=params)

    def close(self):
        self.session.close()

def buildURL(protocol, host, uri):
    return f"{protocol}://{host}{uri}"

def getURLs(URLInfo):
    urls = list()
    for subType, urlInfo in URLInfo.items():
        urls.append(buildURL(**urlInfo))
    return urls