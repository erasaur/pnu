from pgoapi import pgoapi
from pgoapi import utilities as util
from pnu.config import private_config
from s2sphere import Cell, CellId, LatLng
import time, random

class PgoAPI ():
    def __init__ (self):
        self._api = None

    def get_cell_ids (self, lat, lon, radius = 10):
        origin = CellId.from_lat_lng(LatLng.from_degrees(lat, lon)).parent(15)
        walk = [origin.id()]
        right = origin.next()
        left = origin.prev()

        # Search around provided radius
        for i in range(radius):
            walk.append(right.id())
            walk.append(left.id())
            right = right.next()
            left = left.prev()

        # Return everything
        return sorted(walk)

    def find_poi (self, lat, lng):
        api = self._api
        res = {}
        step_size = 0.0015
        step_limit = 49
        coords = self.generate_spiral(lat, lng, step_size, step_limit)
        for coord in [coords[0]]:
            lat = coord['lat']
            lng = coord['lng']
            api.set_position(lat, lng, 0)

            #get_cellid was buggy -> replaced through get_cell_ids from pokecli
            #timestamp gets computed a different way:
            cell_ids = self.get_cell_ids(lat, lng)
            timestamps = [0,] * len(cell_ids)
            response_dict = api.get_map_objects(latitude=util.f2i(lat), longitude=util.f2i(lng), since_timestamp_ms=timestamps, cell_id=cell_ids)
            if (response_dict['responses']):
                if 'status' in response_dict['responses']['GET_MAP_OBJECTS']:
                    if response_dict['responses']['GET_MAP_OBJECTS']['status'] == 1:
                        for map_cell in response_dict['responses']['GET_MAP_OBJECTS']['map_cells']:
                            if 'wild_pokemons' in map_cell:
                                for pokemon in map_cell['wild_pokemons']:
                                    pokekey = self.get_key_from_pokemon(pokemon)
                                    pokemon['hides_at'] = time.time() + pokemon['time_till_hidden_ms']/1000
                                    res[pokekey] = pokemon
        return res

    def get_key_from_pokemon (self, pokemon):
        return '{}-{}'.format(pokemon['spawn_point_id'], pokemon['pokemon_data']['pokemon_id'])

    def generate_spiral (self, starting_lat, starting_lng, step_size, step_limit):
        coords = [{'lat': starting_lat, 'lng': starting_lng}]
        steps,x,y,d,m = 1, 0, 0, 1, 1
        rlow = 0.0
        rhigh = 0.0005

        while steps < step_limit:
            while 2 * x * d < m and steps < step_limit:
                x = x + d
                steps += 1
                lat = x * step_size + starting_lat + random.uniform(rlow, rhigh)
                lng = y * step_size + starting_lng + random.uniform(rlow, rhigh)
                coords.append({'lat': lat, 'lng': lng})
            while 2 * y * d < m and steps < step_limit:
                y = y + d
                steps += 1
                lat = x * step_size + starting_lat + random.uniform(rlow, rhigh)
                lng = y * step_size + starting_lng + random.uniform(rlow, rhigh)
                coords.append({'lat': lat, 'lng': lng})

            d = -1 * d
            m = m + 1
        return coords

    async def get_nearby (self, lat, lon):
        if self._api is None:
            self._api = pgoapi.PGoApi()

            auth_service = private_config["pgoapi"]["auth_service"]
            username = private_config["pgoapi"]["username"]
            password = private_config["pgoapi"]["password"]
            self._api.set_position(lat, lon, 0.0) # set altitude to 0

            if not self._api.login(auth_service, username, password, app_simulation=True):
                raise ValueError("invalid or missing pgoapi config")

        self._api.set_position(lat, lon, 0.0)
        res = self.find_poi(lat, lon)
        print(res)
        return res
