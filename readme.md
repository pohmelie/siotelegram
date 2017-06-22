# Sans io implementation of telegram api
Tiny telegram bot-api wrapper library.

## Reasons
* [aiotg](https://github.com/szastupov/aiotg) is framework, not library and have no proxy support.
* Raw api calls translation is better for understanding and will not break if telegram api will be changed.
* `snake_case`

## Features
* support both, sync and async ways to deal with io.
* Simple as telegram api is.
* `snake_case` api converted to telegram `camelCase`.
* Polling `offset` handled for you via `get_updates` method.
* Handling timeout between requests automatically (via `delay` keyword-only argument).
* Use any io backend you want.

## Implementation
[Sans io](http://sans-io.readthedocs.io/) implementation based on generators
for simplifying flow and holding state. `siotelegram` have io backends based on:
* requests
* aiohttp
* [aiorequests](https://github.com/pohmelie/aiorequests)

## Example
``` python
import asyncio

import siotelegram


TOKEN = "token"


def requests_example():
    api = siotelegram.RequestsTelegramApi(TOKEN)
    response = api.get_updates()
    print(response)


async def aiohttp_example():
    async with siotelegram.AioHTTPTelegramApi(TOKEN) as api:
        response = await api.get_updates()
        print(response)


async def aiorequests_example():
    api = siotelegram.AioRequestsTelegramApi(TOKEN)
    response = await api.get_updates()
    print(response)


if __name__ == "__main__":
    import time
    # requests
    requests_example()
    time.sleep(1)
    # aiohttp
    loop = asyncio.get_event_loop()
    loop.run_until_complete(aiohttp_example())
    time.sleep(1)
    # aiorequests
    import aiorequests
    import concurrent
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        loop = asyncio.get_event_loop()
        loop.set_default_executor(executor)
        aiorequests.set_async_requests(loop=loop)
        loop.run_until_complete(aiorequests_example())
```
