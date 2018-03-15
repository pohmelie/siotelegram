import functools
import time
import threading

import requests

from ..protocol import Protocol


__all__ = (
    "RequestsTelegramApi",
)


class RequestsTelegramApi:

    def __init__(self, token, delay=1, proxy=None, lock=None, timeout=None):
        self.session = requests.Session()
        if proxy is not None:
            self.session.proxies = dict(http=proxy, https=proxy)
        self.proto = Protocol(token)
        self.delay = delay
        self.lock = lock or threading.Lock()
        self.timeout = timeout
        self.last_request_time = 0

    @property
    def token(self):
        return self.proto.token

    def __getattr__(self, name):
        method = getattr(self.proto, name)

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return self._run(method(*args, **kwargs))

        return wrapper

    def _run(self, generator):
        with self.lock:
            response = None
            while True:
                request = generator.send(response)
                if request is None:
                    break
                now = time.perf_counter()
                t = max(0, self.delay - (now - self.last_request_time))
                time.sleep(t)
                self.last_request_time = time.perf_counter()
                kw = request._asdict()
                kw["timeout"] = self.timeout
                response = self.session.request(**kw).json()
        return response
