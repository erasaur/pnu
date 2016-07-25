from pnu.utils.http import PnuHTTPClient

API_URL = "https://pokevision.com/map/data/{}/{}"

class PokevisionAPI (PnuHTTPClient):
    async def get_nearby (self, lat, lon):
        url = API_URL.format(lat, lon)
        resp = await self.get(url).get_json()
        res = []
        
        if resp.status != 200:
            logging.info("pokevision returned non-200 status code!")
        elif "pokemon" in resp:
            for poke in resp["pokemon"]:
                try:
                    res.append(Pokemon(poke))
                except Exception as e:
                    logging.info("failed decoding pokevision res: {}".format(e))
        return res
