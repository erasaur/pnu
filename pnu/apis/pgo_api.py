from pgoapi import PGoApi
from pgoapi import pgoapi
from pgoapi import exceptions
from pgoapi import utilities as util
from pgoapi.utilities import f2i, get_cellid

from pnu.config import private_config
from pnu.models.pokemon import Pokemon
from s2sphere import Cell, CellId, LatLng
import time, random

import threading
from threading import Thread, Lock
from queue import Queue

class PgoAPI ():
    def __init__ (self):
        self._api = None
        self._changed = False
        self._last_changed = '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'
        self._queue = Queue()
        self._result = []

        self._max_tries = pub_config["pgo_api"]["max_tries"]
        self._recovery_time = pub_config["pgo_api"]["recovery_time"]
        self._sleep_time = pub_config["pgo_api"]["sleep_time"]
        self._accounts = []
        self.start_threads(10)

    def start_threads (self, num):
        for i in range(num): t = Thread(target=self.search_thread, name='search_thread-{}'.format(i))
            t.daemon = True
            t.start()
            search_threads.append(t)

    def send_map_request (self, position):
        try:
            api_copy = self._api.copy()
            api_copy.set_position(*position)
            api_copy.get_map_objects(
                latitude=f2i(position[0]),
                longitude=f2i(position[1]),
                since_timestamp_ms=self._last_changed,
                cell_id=get_cellid(position[0], position[1])
            )
            return api_copy.call()
        except Exception as e:
            logging.info("Uncaught exception when downloading map: {}".format(e))
            return False

    def parse_map (self, map_dict, iteration_num, step, step_location):
        cells = map_dict["responses"]["GET_MAP_OBJECTS"]["map_cells"]

        for cell in cells:
            if config["parse_pokemon"]:
                for p in cell.get("wild_pokemons", []):
                    expiration_time = (p["last_modified_timestamp_ms"] +
                         p["time_till_hidden_ms"]) / 1000.0)
                    pokemon_id = p["pokemon_data"]["pokemon_id"]

                    self._result.append(Pokemon({
                        "pokemonId": pokemon_id,
                        "latitude": p["latitude"],
                        "longitude": p["longitude"],
                        "expiration_time": expiration_time
                    })

    def search_thread (self):
        queue = self._queue
        threadname = threading.currentThread().getName()
        logging.info("Search thread {}: started and waiting".format(threadname))
        while True:
            # Get the next item off the queue (this blocks till there is something)
            i, step_location, step, lock = queue.get()

            response_dict = {}
            failed_consecutive = 0
            while not response_dict:
                response_dict = self.send_map_request(step_location)
                if response_dict:
                    with lock:
                        try:
                            self.parse_map(response_dict, i, step, step_location)
                            self._changed = True
                        except KeyError:
                            logging.info('Search thread failed. Response dictionary key error')
                            logging.info('{}: iteration {} step {} failed. Response dictionary\
                                key error.'.format(threadname, i, step))
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

    def get_nearby (self, lat, lon, offset):
        try:
            if self._api is None:
                self._api = pgoapi.PGoApi()
                self.auth(lat, lon)
            elif self._api._auth_provider._ticket_expire:
                remaining_time = self._api._auth_provider._ticket_expire/1000 - time.time()

                if remaining_time > 60:
                    logging.info("Already logged in for another {:.2f} seconds".format(remaining_time))
                else:
                    self.auth(lat, lon)
        except Exception as e:
            logging.info("Got exception when trying to get nearby pokes: {}".format(e))

        if self._changed:
            res = self._result
            self._result = []
            self._changed = False
            return res
        return []
