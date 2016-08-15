from google.protobuf.internal import encoder
from pgoapi import PGoApi, exceptions
from pgoapi import utilities as util
from s2sphere import Cell, CellId, LatLng

from pnu.apis import PnuPokeHelpers
from pnu.config import pub_config, private_config
from pnu.models import Pokemon

import math, random, sys, time, threading
from threading import Thread, Lock
from queue import Queue

import logging
logging = logging.getLogger(__name__)


class PgoAPI ():

    def __init__ (self):
        self._changed = False
        self._queue = Queue()
        self._user_queue = Queue()
        self._result = []

        self._signature_lib_path = ""
        if sys.platform.startswith("linux"):
            self._signature_lib_path = "pnu/etc/pgoapi/libencrypt.so"
        elif sys.platform.startswith("darwin"):
            self._signature_lib_path = "pnu/etc/pgoapi/libencrypt-osx-64.so"
        elif sys.platform.startswith("win"):
            self._signature_lib_path = "pnu/etc/pgoapi/encrypt.dll"
        else:
            raise ValueError("un-supported system")

        self._min_sec_before_reauth = pub_config["poke_api"]["min_sec_before_reauth"]
        self._min_queue_size_before_rescan = pub_config["poke_api"]["min_queue_size_before_rescan"]
        self._scan_throttle_sec = pub_config["poke_api"]["scan_throttle_sec"]
        self._max_tries = pub_config["poke_api"]["max_tries_per_request"]
        self._recovery_time = pub_config["poke_api"]["sleep_after_max_tries"]
        self._sleep_time = pub_config["poke_api"]["sleep_per_request"]
        self._threads = []
        self._users = private_config["poke_api"]["accounts"]

        for index, user_data in enumerate(self._users):
            user = PGoApi()
            user._last_call = 0
            user._data = user_data
            self.auth(user)
            self._users[index] = user
            self._user_queue.put(user)

        self.start_threads(10)

    def encode (self, cellid):
        output = []
        encoder._VarintEncoder()(output.append, cellid)
        return ''.join(output)

    def start_threads (self, num):
        for i in range(num):
            t = Thread(target=self.search_thread, name='search_thread-{}'
                       .format(i))
            t.daemon = True
            t.start()
            self._threads.append(t)

    def send_map_request (self, user, position):
        try:
            cell_ids = util.get_cell_ids(position[0], position[1])
            user._last_call = time.time()
            timestamps = [0,] * len(cell_ids)
            return user.get_map_objects(
                latitude=util.f2i(position[0]),
                longitude=util.f2i(position[1]),
                since_timestamp_ms=timestamps,
                cell_id=cell_ids
            )
        except Exception as e:
            logging.info("Uncaught exception when downloading map: {}"
                         .format(e))
            return False

    def parse_map (self, map_dict, step, step_location):
        if map_dict["responses"]["GET_MAP_OBJECTS"]["status"] != 1:
            return

        cells = map_dict["responses"]["GET_MAP_OBJECTS"]["map_cells"]
        for cell in cells:
            for p in cell.get("wild_pokemons", []):
                expiration_time = (p["last_modified_timestamp_ms"] +
                                   p["time_till_hidden_ms"]) / 1000.0
                pokemon_id = p["pokemon_data"]["pokemon_id"]

                self._result.append(Pokemon({
                    "pokemonId": pokemon_id,
                    "latitude": p["latitude"],
                    "longitude": p["longitude"],
                    "expiration_time": expiration_time
                }))

    def search_thread (self):
        queue = self._queue
        user_queue = self._user_queue
        threadname = threading.currentThread().getName()
        logging.info("Search thread {}: started and waiting".format(threadname))
        while True:
            # get next available user (this blocks till there is one)
            user = user_queue.get()
            now = time.time()

            if user._auth_provider._ticket_expire:
                remaining_time = user._auth_provider._ticket_expire/1000.0-now
                if remaining_time < (self._min_sec_before_reauth * 1000):
                    self.auth(user)

            if now - user._last_call < (self._scan_throttle_sec * 1000):
                logging.info("Not ready to search yet")
                user_queue.put(user)
                time.sleep(self._sleep_time)
                continue

            # get next task (this blocks till there is one)
            step, step_location, lock = queue.get()

            response_dict = {}
            failed_consecutive = 0
            user.set_position(*step_location)

            while not response_dict:
                user.activate_signature(self._signature_lib_path)
                response_dict = self.send_map_request(user, step_location)

                if response_dict:
                    with lock:
                        try:
                            self.parse_map(response_dict, step, step_location)
                            self._changed = True
                        except KeyError:
                            logging.info("Search thread failed. " +
                                         "Response dictionary key error")
                            logging.info("{}: step {} failed. "
                                         .format(threadname, step) +
                                         "Response dictionary key error."
                                         .format(threadname, step))
                            failed_consecutive += 1
                            if (failed_consecutive >= self._max_tries):
                                logging.info("Niantic servers under heavy " +
                                             "load. Waiting before trying " +
                                             "again")
                                time.sleep(self._recovery_time)
                                failed_consecutive = 0
                            response_dict = {}
                else:
                    logging.info('Map download failed, waiting and retrying')
                    time.sleep(self._sleep_time)

            time.sleep(self._sleep_time)
            queue.task_done()
            user_queue.put(user)

    def auth (self, user):
        user_data = user._data
        auth_service = user_data["auth_service"]
        username = user_data["username"]
        password = user_data["password"]

        # for some reason, need to set position before we can login
        if None in user.get_position():
            lat = float(user_data["latitude"])
            lon = float(user_data["longitude"])
            user.set_position(lat, lon, 8)

        user.set_authentication(provider=auth_service, username=username,
                                password=password)

    def generate_location_steps (self, initial_loc, step_count):
        #Bearing (degrees)
        NORTH = 0
        EAST = 90
        SOUTH = 180
        WEST = 270

        pulse_radius = 0.07  # km - radius of players heartbeat is 70m
        xdist = math.sqrt(3)*pulse_radius  # dist between column centers
        ydist = 3*(pulse_radius/2)  # dist between row centers

        yield (initial_loc[0], initial_loc[1], 0)  # insert initial location

        ring = 1
        loc = initial_loc
        while ring < step_count:
            #Set loc to start at top left
            loc = get_coor_in_dir(loc, ydist, NORTH)
            loc = get_coor_in_dir(loc, xdist/2, WEST)
            for direction in range(6):
                for i in range(ring):
                    if direction == 0: # RIGHT
                        loc = get_coor_in_dir(loc, xdist, EAST)
                    if direction == 1: # DOWN + RIGHT
                        loc = get_coor_in_dir(loc, ydist, SOUTH)
                        loc = get_coor_in_dir(loc, xdist/2, EAST)
                    if direction == 2: # DOWN + LEFT
                        loc = get_coor_in_dir(loc, ydist, SOUTH)
                        loc = get_coor_in_dir(loc, xdist/2, WEST)
                    if direction == 3: # LEFT
                        loc = get_coor_in_dir(loc, xdist, WEST)
                    if direction == 4: # UP + LEFT
                        loc = get_coor_in_dir(loc, ydist, NORTH)
                        loc = get_coor_in_dir(loc, xdist/2, WEST)
                    if direction == 5: # UP + RIGHT
                        loc = get_coor_in_dir(loc, ydist, NORTH)
                        loc = get_coor_in_dir(loc, xdist/2, EAST)
                    yield (loc[0], loc[1], 0)
            ring += 1

    def get_nearby (self, lat, lon, num_steps):
        queue_size = self._queue.qsize()
        user_queue_size = self._user_queue.qsize()
        logging.info("Task queue size: {}".format(queue_size) +
                     " User queue size: {}".format(user_queue_size))
        if queue_size <= self._min_queue_size_before_rescan:
            # finished previous load, time for more
            logging.info("Starting new search...")
            lock = Lock()
            locations = self.generate_location_steps([lat, lon], num_steps)

            for step, step_location in enumerate(locations, 1):
                search_args = (step, step_location, lock)
                self._queue.put(search_args)

        if self._changed:
            # flush the result buffer
            res = self._result
            self._result = []
            self._changed = False
            return res
        return []
