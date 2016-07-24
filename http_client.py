import asyncio, aiohttp

class PnuHTTPClient ():
    def __init__ (self, session=None):
        if session is None:
            raise ValueError('missing session')
        self._session = session

    async def get (self, url):
        async with self._session.get(url) as resp:
            print(resp.status)
            return await resp.text()
