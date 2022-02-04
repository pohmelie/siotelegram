import asyncio
import functools
import time

from async_timeout import timeout
from httpx import AsyncClient

from ..protocol import Protocol, DEFAULT_TIMEOUT, DEFAULT_DELAY


__all__ = (
    "HTTPxTelegramApi",
)


class HTTPxTelegramApi:

    def __init__(self, token, delay=DEFAULT_DELAY, proxy=None, lock=None, timeout=DEFAULT_TIMEOUT):
        self.client = AsyncClient(proxies=proxy)
        self.proxy = proxy
        self.proto = Protocol(token)
        self.delay = delay
        self.lock = lock or asyncio.Lock()
        self.timeout = timeout
        self.last_request_time = 0

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

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

    async def _run(self, generator):
        async with self.lock:
            response = None
            while True:
                request = generator.send(response)
                if request is None:
                    break
                if request.files is not None:
                    raise NotImplementedError("files upload functionality for httpx is not implemented yet")
                now = time.monotonic()
                t = max(0, self.delay - (now - self.last_request_time))
                await asyncio.sleep(t)
                self.last_request_time = time.monotonic()
                req = {
                    "method": request.method,
                    "url": request.url,
                    "data": request.data,
                }
                async with timeout(self.timeout):
                    resp = await self.client.request(**req)
                    response = resp.json()
        return response
