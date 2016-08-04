from pgoapi import PGoApi
from pgoapi import pgoapi
from pgoapi import exceptions
from pgoapi import utilities as util

from pnu.config import pub_config, private_config
from pnu.models.pokemon import Pokemon
from s2sphere import Cell, CellId, LatLng
from google.protobuf.internal import encoder
import math, time, random

import threading
from threading import Thread, Lock
from queue import Queue

import logging
logging = logging.getLogger(__name__)

class PgoAPI ():
    def __init__ (self):
        self._api = None
        self._changed = False
        self._queue = Queue()
        self._result = []

        self._earth_radius = pub_config["poke_api"]["earth_radius"]
        self._max_tries = pub_config["poke_api"]["max_tries_per_request"]
        self._recovery_time = pub_config["poke_api"]["sleep_after_max_tries"]
        self._sleep_time = pub_config["poke_api"]["sleep_per_request"]
        self._accounts = []
        self._threads = []

    def encode (self, cellid):
        output = []
        encoder._VarintEncoder()(output.append, cellid)
        return ''.join(output)

    def get_cell_ids (self, lat, lon, radius=10):
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

    def start_threads (self, num):
        for i in range(num): 
            t = Thread(target=self.search_thread, name='search_thread-{}'.format(i))
            t.daemon = True
            t.start()
            self._threads.append(t)

    def send_map_request (self, position):
        try:
            api = self._api
            api.set_position(*position)
            cell_ids = self.get_cell_ids(position[0], position[1])
            timestamps = [0,] * len(cell_ids)
            res = api.get_map_objects(
                latitude=util.f2i(position[0]),
                longitude=util.f2i(position[1]),
                since_timestamp_ms=timestamps,
                cell_id=cell_ids
            )
            return res
        except Exception as e:
            logging.info("Uncaught exception when downloading map: {}".format(e))
            return False

    def parse_map (self, map_dict, step, step_location):
        if map_dict["responses"]["GET_MAP_OBJECTS"]["status"] != 1:
            return

        cells = map_dict["responses"]["GET_MAP_OBJECTS"]["map_cells"]
        for cell in cells:
            for p in cell.get("wild_pokemons", []):
                expiration_time = (p["last_modified_timestamp_ms"] + p["time_till_hidden_ms"]) / 1000.0
                pokemon_id = p["pokemon_data"]["pokemon_id"]

                self._result.append(Pokemon({
                    "pokemonId": pokemon_id,
                    "latitude": p["latitude"],
                    "longitude": p["longitude"],
                    "expiration_time": expiration_time
                }))

    def search_thread (self):
        queue = self._queue
        threadname = threading.currentThread().getName()
        logging.info("Search thread {}: started and waiting".format(threadname))
        while True:
            if self._api is None:
                logging.info("Not ready to search yet")
                time.sleep(self._sleep_time)
                continue

            # Get the next item off the queue (this blocks till there is something)
            step, step_location, lock = queue.get()
            print("getting:", step, step_location)

            response_dict = {}
            failed_consecutive = 0
            while not response_dict:
                response_dict = self.send_map_request(step_location)
                if response_dict:
                    with lock:
                        try:
                            self.parse_map(response_dict, step, step_location)
                            self._changed = True
                        except KeyError:
                            logging.info('Search thread failed. Response dictionary key error')
                            logging.info('{}: step {} failed. Response dictionary\
                                key error.'.format(threadname, step))
                            failed_consecutive += 1
                            if (failed_consecutive >= self._max_tries):
                                logging.info('Niantic servers under heavy load. Waiting before trying again')
                                time.sleep(self._recovery_time)
                                failed_consecutive = 0
                            response_dict = {}
                else:
                    logging.info('Map download failed, waiting and retrying')
                    time.sleep(self._sleep_time)

            time.sleep(self._sleep_time)
            queue.task_done()

    def auth (self, lat, lon):
        auth_service = private_config["pgoapi"]["auth_service"]
        username = private_config["pgoapi"]["username"]
        password = private_config["pgoapi"]["password"]

        # for some reason, need to set position before we can login
        if None in self._api.get_position():
            self._api.set_position(lat, lon, 0.0)

        if not self._api.login(auth_service, username, password, app_simulation=True):
            raise ValueError("invalid or missing pgoapi config")

    def get_new_coords (self, init_loc, distance, bearing):
        """ Given an initial lat/lng, a distance(in kms), and a bearing (degrees),
        this will calculate the resulting lat/lng coordinates.
        """ 
        R = self._earth_radius
        bearing = math.radians(bearing)

        init_coords = [math.radians(init_loc[0]), math.radians(init_loc[1])] # convert lat/lng to radians

        new_lat = math.asin(math.sin(init_coords[0])*math.cos(distance/R) +
            math.cos(init_coords[0])*math.sin(distance/R)*math.cos(bearing))

        new_lon = init_coords[1] + math.atan2(math.sin(bearing)*math.sin(distance/R)*math.cos(init_coords[0]),
            math.cos(distance/R)-math.sin(init_coords[0])*math.sin(new_lat))

        return [math.degrees(new_lat), math.degrees(new_lon)]

    def generate_location_steps (self, initial_loc, step_count):
        # bearing (degrees)
        NORTH = 0
        EAST = 90
        SOUTH = 180
        WEST = 270

        pulse_radius = 0.1                  # km - radius of players heartbeat is 100m
        xdist = math.sqrt(3)*pulse_radius   # dist between column centers
        ydist = 3*(pulse_radius/2)          # dist between row centers

        yield (initial_loc[0], initial_loc[1], 0) # insert initial location

        ring = 1            
        loc = initial_loc
        while ring < step_count:
            # set loc to start at top left
            loc = self.get_new_coords(loc, ydist, NORTH)
            loc = self.get_new_coords(loc, xdist/2, WEST)
            for direction in range(6):
                for i in range(ring):
                    if direction == 0: # RIGHT
                        loc = self.get_new_coords(loc, xdist, EAST)
                    if direction == 1: # DOWN + RIGHT
                        loc = self.get_new_coords(loc, ydist, SOUTH)
                        loc = self.get_new_coords(loc, xdist/2, EAST)
                    if direction == 2: # DOWN + LEFT
                        loc = self.get_new_coords(loc, ydist, SOUTH)
                        loc = self.get_new_coords(loc, xdist/2, WEST)
                    if direction == 3: # LEFT
                        loc = self.get_new_coords(loc, xdist, WEST)
                    if direction == 4: # UP + LEFT
                        loc = self.get_new_coords(loc, ydist, NORTH)
                        loc = self.get_new_coords(loc, xdist/2, WEST)
                    if direction == 5: # UP + RIGHT
                        loc = self.get_new_coords(loc, ydist, NORTH)
                        loc = self.get_new_coords(loc, xdist/2, EAST)
                    yield (loc[0], loc[1], 0)
            ring += 1

    def get_nearby (self, lat, lon, num_steps):
        try:
            if self._api is None:
                self._api = pgoapi.PGoApi()
                self.auth(lat, lon)
                self.start_threads(10)
            elif self._api._auth_provider._ticket_expire:
                remaining_time = self._api._auth_provider._ticket_expire/1000 - time.time()

                if remaining_time > 60:
                    logging.info("Already logged in for another {:.2f} seconds".format(remaining_time))
                else:
                    self.auth(lat, lon)
        except Exception as e:
            logging.info("Got exception when trying to get nearby pokes: {}".format(e))

        if self._queue.empty():
            # finished previous load, time for more
            logging.info("Starting new search...")
            lock = Lock()
            locations = self.generate_location_steps([lat, lon], num_steps)

            for step, step_location in enumerate(locations, 1):
                print("putting:", step, step_location)
                search_args = (step, step_location, lock)
                self._queue.put(search_args)

        if self._changed:
            res = self._result
            self._result = []
            self._changed = False
            return res
        return []
