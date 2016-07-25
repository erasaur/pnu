import asyncio, aiohttp

class PnuHTTPClient ():
    def __init__ (self, session=None):
        if session is None:
            raise ValueError("missing session")
        self._session = session

    async def get_json (self, url):
        async with self._session.get(url) as resp:
            try:
                res = await resp.json()
            except Exception as e:
                logging.info("failed decoding response, got exception: {}".format(e))
                res = {}
            return { "status": resp.status, "res": res }
