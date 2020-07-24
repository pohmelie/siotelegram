import functools
from dataclasses import dataclass


__all__ = (
    "Request",
    "Protocol",
)


DEFAULT_DELAY = 1
DEFAULT_TIMEOUT = 30


@dataclass
class Request:
    method: str
    url: str
    data: dict
    files: dict


class Protocol:
    URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token):
        self.token = token
        self.offset = 0

    def _api_call(self, method, *, files_=None, **options):
        url = self.URL.format(token=self.token, method=method)
        yield Request(method="post", url=url, data=options, files=files_)
        yield None

    def __getattr__(self, method):
        if method in ("__getstate__", "__setstate__"):
            raise AttributeError
        return functools.partial(self._api_call, method.replace("_", ""))

    def get_updates(self):
        for request in self.getUpdates(offset=self.offset):
            if request is None:
                break
            response = yield request
        for update in response.get("result", []):
            self.offset = max(self.offset, update["update_id"] + 1)
        yield None
