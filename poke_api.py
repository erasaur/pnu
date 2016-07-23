# import asyncio, aiohttp

class PokeApi ():
    def __init__ (self, loop=None):
        pass

    def _get_name_from_id (poke_id): # TODO csv file
        pass

    def get_sprite_from_name (poke_name):
        pass

    def get_sprite_from_id (poke_id):
        poke_name = _get_name_from_id(poke_id)
        return get_sprite_from_name(poke_name)

    # cache results and reuse if location is close enough?
    # batch-request a minimal set of hotspot locations in order to cover all
    # requests?
    def get_nearby_pokemon (self, lat, lon):
        pass
