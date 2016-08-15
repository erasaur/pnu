from google.protobuf.internal import encoder
from pgoapi import PGoApi, exceptions
from pgoapi import utilities as util
from s2sphere import Cell, CellId, LatLng

from pnu.config import pub_config, private_config
from pnu.models import Pokemon

import math, random, sys, time, threading
from threading import Thread, Lock
from queue import Queue

import logging
logging = logging.getLogger(__name__)


class PnuScanner ():

    def __init__ (self, scan_queue=None, dispatch_queue=None):
        if scan_queue is None or dispatch_queue is None:
            raise ValueError("missing scan/dispatch queues")

        self._scan_queue = scan_queue
        self._dispatch_queue = dispatch_queue
        self._user_queue = Queue()

        self._lock = Lock()
        self._threads = []
        self._users = []

        self._signature_lib_path = ""
        if sys.platform.startswith("linux"):
            self._signature_lib_path = pub_config["pgo_api"]["linux_signature_lib_file"]
        elif sys.platform.startswith("darwin"):
            self._signature_lib_path = pub_config["pgo_api"]["darwin_signature_lib_file"]
        elif sys.platform.startswith("win"):
            self._signature_lib_path = pub_config["pgo_api"]["win_signature_lib_file"]
        else:
            raise ValueError("un-supported system")

        self._min_ms_before_reauth = pub_config["scanner"]["min_sec_before_reauth"] * 1000
        self._max_tries = pub_config["scanner"]["max_tries_per_request"]
        self._sleep_ms = pub_config["scanner"]["sleep_per_try_sec"] * 1000
        self._scan_throttle_ms = pub_config["scanner"]["scan_throttle_sec"] * 1000
        self._delay_between_login_sec = pub_config["scanner"]["delay_between_login_sec"]
        users = private_config["poke_api"]["accounts"]

        logging.info("Logging in users...")
        for user_data in users:
            user = PGoApi()
            user._last_call = 0
            user._data = user_data
            self.auth(user)
            self._users.append(user)
            self._user_queue.put(user)

            # stagger logins
            time.sleep(random.random() * self._delay_between_login_sec)

        logging.info("Spinning up threads...")
        self.start_threads(10)

    def encode (self, cellid):
        output = []
        encoder._VarintEncoder()(output.append, cellid)
        return ''.join(output)

    def start_threads (self, num):
        for i in range(num):
            t = Thread(target=self.search_thread, name='search_thread-{}'.format(i))
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
            logging.info("Uncaught exception when downloading map: {}".format(e))
            return False

    def parse_map (self, map_dict):
        res = []
        if map_dict["responses"]["GET_MAP_OBJECTS"]["status"] != 1:
            return res

        cells = map_dict["responses"]["GET_MAP_OBJECTS"]["map_cells"]
        for cell in cells:
            for p in cell.get("wild_pokemons", []):
                # handle expiration time overflow
                if (0 < p['time_till_hidden_ms'] < (60 * 60 * 1000)):
                    # we're within the hour range
                    expiration_time = p['last_modified_timestamp_ms'] + p['time_till_hidden_ms']
                else:
                    # assume 15 minutes since it's clearly larger than that
                    expiration_time = p['last_modified_timestamp_ms'] + (15 * 60 * 1000)

                pokemon_id = p["pokemon_data"]["pokemon_id"]
                res.append(Pokemon({
                    "pokemonId": pokemon_id,
                    "latitude": p["latitude"],
                    "longitude": p["longitude"],
                    "expiration_time": expiration_time
                }))
        return res

    def remaining_time (self, start_ms, interval_ms):
        return max(time.time() * 1000 - (start_ms + interval_ms), 0)

    def search_thread (self):
        queue = self._scan_queue
        user_queue = self._user_queue
        threadname = threading.currentThread().getName()
        logging.info("Search thread {}: started and waiting".format(threadname))

        while True:
            # get next available user (this blocks till there is one)
            user = user_queue.get()
            start = time.time() * 1000

            if user._auth_provider._ticket_expire:
                remaining_time = user._auth_provider._ticket_expire - start
                if remaining_time < self._min_ms_before_reauth:
                    self.auth(user)

            if start - user._last_call < self._scan_throttle_ms:
                logging.info("Not ready to search yet")
                user_queue.put(user)
                time.sleep(self.remaining_time(start, self._sleep_ms))
                continue

            # get next task (this blocks till there is one)
            loc, group = self._scan_queue.get()
            user.set_position(*loc)
            failed_consecutive = 0

            while True:
                if failed_consecutive >= self._max_tries:
                    logging.info("tried too many times to parse map, giving up")
                    queue.task_done()
                    break

                user.activate_signature(self._signature_lib_path)
                response_dict = self.send_map_request(user, loc)

                if not response_dict:
                    logging.info("got no results when querying, retrying soon")
                    time.sleep(self.remaining_time(start, self._sleep_ms))
                    failed_consecutive = 0
                    continue

                am_tired = False
                with self._lock:
                    try:
                        pokes_nearby = self.parse_map(response_dict)
                        self._dispatch_queue.put((loc, group, pokes_nearby))
                        queue.task_done()
                        break
                    except Exception as e:
                        logging.info("failed parsing map on thread {} with error: {}".format(threadname, e))
                        failed_consecutive += 1
                        am_tired = True
                        # don't sleep here while holding onto the lock!

                if am_tired:
                    time.sleep(self.remaining_time(start, self._sleep_ms))

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
