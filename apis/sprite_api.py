from pnu.utils.http import PnuHTTPClient

API_URL = "https://img.pokemondb.net/sprites/emerald/normal/{}.png"

class PokeDBAPI (PnuHTTPClient):
    def __init__ (self, loop=None):
        super().__init__(loop)

        # load poke list
        with open('data/pokemon.csv') as f:
            reader = csv.reader(f)
            for line in reader:
                self._poke_list
            self._poke_list = list(reader)

    def get_name_from_id (poke_id):
        try:
            poke = self._poke_list[poke_id - 1]
        except Exception:
            poke = None
        return poke

    def get_sprite_from_name (poke_name):
        url = API_URL.format(poke_name)
        return await self.get(url)

    def get_sprite_from_id (poke_id):
        poke_name = self.get_name_from_id(poke_id)
        return self.get_sprite_from_name(poke_name)

    async def get_nearby_pokemon (self, lat, lon):
        url = API_URL.format(lat, lon)
        return await self.get(url)
