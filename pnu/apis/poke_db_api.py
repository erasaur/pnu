from pnu.core.http_client import PnuHTTPClient

API_URL = "https://img.pokemondb.net/sprites/emerald/normal/{}.png"

class PokeDBAPI (PnuHTTPClient):
    async def get_sprite_from_name (poke_name):
        url = API_URL.format(poke_name)
        return await self.get(url)

    async def get_sprite_from_id (poke_id):
        poke_name = self.get_name_from_id(poke_id)
        return await self.get_sprite_from_name(poke_name)
