import asyncio, aiohttp, time
from pnu.core.data_store import PnuUserDataStore
from pnu.apis.pokevision_api import PokevisionAPI
from pnu.apis.sprite_api import PokeDBAPI
from pnu.config import pub_config
from pnu.models.user import User
from pnu.models.pokemon import Pokemon
from pnu.models.alert import Alert

class PnuPokeApi ():
    def __init__ (self, session=None):
        # TODO add other apis for backup
        self._pokevision_api = PokevisionAPI(session=session)
        self._poke_db_api = PokeDBAPI(session=session)
        # self._scan_lat_dist = pub_config["poke_api"]["scan_lat_dist"]
        # self._scan_lon_dist = pub_config["poke_api"]["scan_lon_dist"]
        self._last_update = 0
        self._users = []

    def update_data (self):
        # TODO find the minimal set of locations to cover everybody
        if PnuUserDataStore.changed_since(self._last_update):
            self._users = [User(data=l) for l in PnuUserDataStore.list()]
            self._last_update = time.time()

    async def get_pokemon_alerts (self):
        # XXX cache results and reuse if location is close enough?
        # XXX batch-request a minimal set of hotspot locations in order to 
        # cover all requests?

        # update list of locations we need to query for nearby pokes
        self.update_data()

        # for each such location, get the nearby pokes, and filter out the
        temp = {} # result to return
        fut_list = []
        for user in self._users:
            fut = asyncio.ensure_future(
                self._pokevision_api.get_nearby(user.get_lat(), user.get_lon())
            )
            fut_list.append((user, fut,))

        for user, fut in fut_list:
            pokes_nearby = await fut
            curr = set() # don't want duplicates

            for poke in pokes_nearby:
                poke_id = poke.get_id()
                curr.add((
                    poke_id, 
                    poke.get_lat(), 
                    poke.get_lon(),
                    poke.get_expiration_time()
                ))
                # if poke_id in user.get_pokemon_wanted():
                #     curr.add(poke_id)

            if len(curr) > 0:
                # sort so that multiple tuples with the same elements (but
                # potentially in different order) still map to same key
                curr = sorted(curr)

                # convert poke tuples into poke objects
                poke_list = []
                for poke_args in curr:
                    poke_list.append(Pokemon(*poke_args))

                # convert back to tuple because dicts need immutable keys
                poke_tuple = tuple(poke_list)
                if poke_tuple in temp:
                    temp[poke_tuple].append(user.get_phone_number())
                else:
                    temp[poke_tuple] = [user.get_phone_number()]

        res = []
        for poke_tuple, phone_list in temp:
            res.append(Alert(poke_tuple, phone_list))

        return res

    # def is_nearby (self, first, second, lat_dist=None, lon_dist=None):
    #     if lat_dist is None:
    #         lat_dist = self._scan_lat_dist
    #     if lon_dist is None:
    #         lon_dist = self._scan_lon_dist

    #     return abs(first["lat"] - second["lat"]) < lat_dist &&
    #         abs(first["lon"] - second["lon"]) < lon_dist
