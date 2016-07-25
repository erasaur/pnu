from ..http import PnuHTTPClient

API_URL = "https://pokevision.com/map/data/{}/{}"

class PokevisionAPI (PnuHTTPClient):
    async def get_nearby (self, lat, lon):
        url = API_URL.format(lat, lon)
        resp = await self.get(url).get_json()
        res = []

        if "pokemon" in resp:
            for poke in resp["pokemon"]:
                try:
                    res.append(Pokemon(poke))
                except:
                    print("invalid response, skipping")
        return res
