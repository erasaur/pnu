import logging
logger = logging.getLogger(__name__)
from pnu.core.http_client import PnuHTTPClient
from pnu.models.pokemon import Pokemon

API_URL = "https://pokevision.com/map/data/{}/{}"

class PokevisionAPI (PnuHTTPClient):
    async def get_nearby (self, lat, lon):
        res = []
        if lat is not None and lon is not None:
            url = API_URL.format(lat, lon)
            resp = await self.get_json(url)

            if resp["status"] != 200:
                logging.info("pokevision returned non-200 status code!")

            resp = resp["res"]
            if "pokemon" in resp:
                for poke in resp["pokemon"]:
                    try:
                        res.append(Pokemon(poke))
                    except Exception as e:
                        logging.info("failed decoding pokevision res: {}".format(e))
        return res
