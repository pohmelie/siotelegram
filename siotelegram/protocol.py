import functools
import collections


__all__ = (
    "Request",
    "Protocol",
)


Request = collections.namedtuple("Request", "method url data")


class Protocol:
    URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token):
        self.token = token
        self.offset = 0

    def _api_call(self, method, **options):
        url = str.format(Protocol.URL, token=self.token, method=method)
        yield Request(method="post", url=url, data=options)
        yield None

    def __getattr__(self, method):
        return functools.partial(self._api_call, str.replace(method, "_", ""))

    def get_updates(self):
        for request in self.getUpdates(offset=self.offset):
            if request is None:
                break
            response = yield request
        for update in response.get("result", []):
            self.offset = max(self.offset, update["update_id"] + 1)
        yield None
