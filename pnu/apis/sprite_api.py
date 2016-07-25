import csv
from pnu.core.http_client import PnuHTTPClient

API_URL = "https://img.pokemondb.net/sprites/emerald/normal/{}.png"

class PokeDBAPI (PnuHTTPClient):
    def __init__ (self, session=None):
        super().__init__(session)

        # load poke list
        with open('./pnu/etc/pokemon.csv') as f:
            reader = csv.reader(f)
            self._poke_list = list(reader)

    def get_name_from_id (poke_id):
        try:
            poke = self._poke_list[poke_id - 1]
        except Exception:
            poke = None
        return poke

    async def get_sprite_from_name (poke_name):
        url = API_URL.format(poke_name)
        return await self.get(url)

    async def get_sprite_from_id (poke_id):
        poke_name = self.get_name_from_id(poke_id)
        return await self.get_sprite_from_name(poke_name)
