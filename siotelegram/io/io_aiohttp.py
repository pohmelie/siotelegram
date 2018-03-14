import asyncio
import functools

import aiohttp
from async_timeout import timeout

from ..protocol import Protocol


__all__ = (
    "AioHTTPTelegramApi",
)


class AioHTTPTelegramApi:

    def __init__(self, token, delay=1, proxy=None, loop=None, lock=None, timeout=None):
        self.session = aiohttp.ClientSession(loop=loop)
        self.proxy = proxy
        self.proto = Protocol(token)
        self.delay = delay
        self.loop = loop or asyncio.get_event_loop()
        self.lock = lock or asyncio.Lock(loop=self.loop)
        self.timeout = timeout
        self.last_request_time = 0

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc, tb):
        return await self.close()

    @property
    def token(self):
        return self.proto.token

    def __getattr__(self, name):
        method = getattr(self.proto, name)

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return self._run(method(*args, **kwargs))

        return wrapper

    async def _run(self, generator):
        with (await self.lock):
            response = None
            while True:
                request = generator.send(response)
                if request is None:
                    break
                now = self.loop.time()
                timeout = max(0, self.delay - (now - self.last_request_time))
                await asyncio.sleep(timeout, loop=self.loop)
                self.last_request_time = self.loop.time()
                kw = request._asdict()
                kw["proxy"] = self.proxy
                async with timeout(self.timeout):
                    async with self.session.request(**kw) as resp:
                        response = await resp.json()
        return response
