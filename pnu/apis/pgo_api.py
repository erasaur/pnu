from pgoapi import pgoapi
from pgoapi import exceptions
from pgoapi import utilities as util
from pnu.config import private_config
from pnu.models.pokemon import Pokemon
from s2sphere import Cell, CellId, LatLng
import time, random

class PgoAPI ():
    def __init__ (self):
        self._api = None
        self._lat = self.

    def get_cell_ids (self, lat, lon, radius=10):
        origin = CellId.from_lat_lng(LatLng.from_degrees(lat, lon)).parent(15)
        walk = [origin.id()]
        right = origin.next()
        left = origin.prev()

        # Search around provided radius
        for i in range(radius):
            # TODO: don't append if close_enough to something we've added
            walk.append(right.id())
            walk.append(left.id())
            right = right.next()
            left = left.prev()

        # Return everything
        return sorted(walk)

    def find_poi (self, lat, lng, offset):
        # TODO: increase search radius based on offset
        api = self._api
        res = []
        step_size = 0.003
        step_limit = 20
        delay = 0.11 # seconds
        add_delay = 0.01
        # coords = self.generate_spiral(lat, lng, step_size, step_limit)

        for coord in coords:
            lat = coord['lat']
            lng = coord['lng']
            api.set_position(lat, lng, 0)

            #get_cellid was buggy -> replaced through get_cell_ids from pokecli
            #timestamp gets computed a different way:
            cell_ids = self.get_cell_ids(lat, lng)
            timestamps = [0,] * len(cell_ids)

            try:
                response_dict = api.get_map_objects(latitude=util.f2i(lat), longitude=util.f2i(lng), since_timestamp_ms=timestamps, cell_id=cell_ids)

                if (response_dict['responses']):
                    if 'status' in response_dict['responses']['GET_MAP_OBJECTS']:
                        if response_dict['responses']['GET_MAP_OBJECTS']['status'] == 1:
                            for map_cell in response_dict['responses']['GET_MAP_OBJECTS']['map_cells']:
                                if 'wild_pokemons' in map_cell:
                                    for pokemon in map_cell['wild_pokemons']:
                                        res.append(Pokemon({
                                            "pokemonId": pokemon["pokemon_data"]["pokemon_id"],
                                            "latitude": pokemon["latitude"],
                                            "longitude": pokemon["longitude"],
                                            "expiration_time": time.time() +
                                            pokemon["time_till_hidden_ms"]/1000
                                        }))
                                        print(pokemon)
            except exceptions.ServerSideRequestThrottlingException:
                delay += add_delay
                print(delay)

            time.sleep(delay)
        return res

    def get_coords (self, lat, lon, offset):
        pass 

    def generate_spiral (self, starting_lat, starting_lng, step_size, step_limit):
        coords = [{'lat': starting_lat, 'lng': starting_lng}]
        steps,x,y,d,m = 1, 0, 0, 1, 1
        rlow = 0.0
        rhigh = 0.0005

        # TODO: don't append if coor is close_enough to one of the ones we've
        # already appended

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

    def auth (self):
        auth_service = private_config["pgoapi"]["auth_service"]
        username = private_config["pgoapi"]["username"]
        password = private_config["pgoapi"]["password"]

        # for some reason, need to set position before we can login
        if None in self._api.get_position():
            self._api.set_position(lat, lon, 0.0)

        if not self._api.login(auth_service, username, password, app_simulation=True):
            raise ValueError("invalid or missing pgoapi config")

    async def get_nearby (self, lat, lon, offset):
        print("STARTING")

        try:
            if self._api is None:
                self._api = pgoapi.PGoApi()
                self.auth()
            elif self._api._auth_provider._ticket_expire:
                remaining_time = self._api._auth_provider._ticket_expire/1000 - time.time()

                if remaining_time > 60:
                    logging.info("Already logged in for another {:.2f} seconds".format(remaining_time))
                else:
                    self.auth()

            res = self.query_locations(lat, lon, offset)
        except Exception as e:
            logging.info("Got exception when trying to get nearby pokes: {}".format(e))

        print("ENDING")
        return res
