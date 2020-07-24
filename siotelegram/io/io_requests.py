import functools
import time
import threading

import requests

from ..protocol import Protocol, DEFAULT_TIMEOUT, DEFAULT_DELAY


__all__ = (
    "RequestsTelegramApi",
)


class RequestsTelegramApi:

    def __init__(self, token, delay=DEFAULT_DELAY, proxy=None, lock=None, timeout=DEFAULT_TIMEOUT):
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
        if name in ("__getstate__", "__setstate__"):
            raise AttributeError
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
                now = time.monotonic()
                t = max(0, self.delay - (now - self.last_request_time))
                time.sleep(t)
                self.last_request_time = time.monotonic()
                req = {
                    "method": request.method,
                    "url": request.url,
                    "data": request.data,
                    "timeout": self.timeout,
                }
                response = self.session.request(**req).json()
        return response
