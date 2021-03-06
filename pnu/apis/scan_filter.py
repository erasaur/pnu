import time, json

from math import sqrt, cos, radians
from ast import literal_eval
from pnu.core.runnable import PnuRunnable
from pnu.apis.geo import close_enough, get_coor_in_dir, get_center_of_group
from pnu.config import pub_config

import logging
logging = logging.getLogger(__name__)

class PnuScanFilter (PnuRunnable):

    def __init__ (self, scan_queue=None):
        if scan_queue is None:
            raise ValueError("missing scan queue")
        self._scan_queue = scan_queue
        self._sync_file = pub_config["scan_filter"]["sync_file"]
        self._update_interval = pub_config["scan_filter"]["update_interval_sec"]

        # locations we know that have spawns
        self._spawn_locations = {}

        # minimal count to be considered for regular spawn
        self._spawn_count_threshold = pub_config["scan_filter"]["spawn_count_threshold"]

        # delay between scans for the same location
        self._spawn_interval = pub_config["poke_api"]["scan_interval_sec"]

        # how far to scan per group
        self._group_scan_radius = pub_config["scan_filter"]["group_scan_radius_km"]

        # on startup, load known scan locations into memory
        self.sync_from_file()

        # how often to sync data to file
        self._sync_to_file_interval = pub_config["scan_filter"]["sync_to_file_interval_sec"]
        self._last_sync = time.time()

        super().__init__(update_interval=self._update_interval)
        self.run()

    def update (self):
        logging.info("Updating scan filter")
        now = time.time()
        if now - self._last_sync >= self._sync_to_file_interval:
            self.sync_to_file()

    def sync_from_file (self):
        logging.info("Syncing locations from file...")
        logging.info("Previously had {} locations".format(len(self._spawn_locations)))

        with open(self._sync_file, "r") as f:
            self._spawn_locations = {}
            try:
                json_data = json.load(f)
                # spawn_locations maps locations (tuples) to dictionaries.
                # because json doesn't support tuples as keys, when serializing
                # the spawn_locations, the keys (tuples) are converted to their
                # string representations. so, when reading from the json dump, 
                # we have to convert the keys back to tuples using literal_eval.
                for spawn_loc, spawn_data in json_data.items():
                    loc = literal_eval(spawn_loc)
                    self._spawn_locations[loc] = spawn_data
            except Exception as e:
                logging.info("Error reading spawn locations from file: {}".format(e))

        logging.info("Now have {} locations".format(len(self._spawn_locations)))
        logging.info("Done syncing locations")

    def sync_to_file (self):
        logging.info("Syncing locations to file...")

        with open(self._sync_file, "w") as f:
            try:
                json_data = {}
                for spawn_loc, spawn_data in self._spawn_locations.items():
                    json_data[str(spawn_loc)] = spawn_data
                json.dump(json_data, f)
            except Exception as e:
                logging.info("Error writing spawn locations to file: {}".format(e))

        self._last_sync = time.time()
        logging.info("Done syncing locations")

    def update_data (self, loc, pokes):
        if not self.seen_before(loc):
            logging.info("trying to update filter data with invalid data")
            return
        spawn_loc, spawn_data = self.get_spawn_location(loc)
        if len(pokes) > 0:
            spawn_data["spawn_count"] = max(spawn_data["spawn_count"] + 1, self._spawn_count_threshold)
        else:
            spawn_data["spawn_count"] -= 1

    def get_corners (self, group):
        NORTH = 0
        EAST = 90
        SOUTH = 180
        WEST = 270

        loc = get_center_of_group(group)
        radius = self._group_scan_radius
        xdist = ydist = sqrt(2)/2 * (radius/2)

        bot_left = get_coor_in_dir(loc, ydist, SOUTH)
        bot_left = get_coor_in_dir(bot_left, xdist, WEST)

        top_right = get_coor_in_dir(loc, ydist, NORTH)
        top_right = get_coor_in_dir(top_right, xdist, EAST)
        
        return (bot_left[0], bot_left[1], top_right[0], top_right[1])

    def get_locations (self, group):
        locations = []
        rect = self.get_corners(group)
        dlat = 0.00089
        dlng = dlat / cos(radians((rect[0]+rect[2])*0.5))
        startLat = min(rect[0], rect[2])+(0.624*dlat)
        startLng = min(rect[1], rect[3])+(0.624*dlng)
        latSteps = int((((max(rect[0], rect[2])-min(rect[0], rect[2])))/dlat)+0.75199999)
        if latSteps<1:
            latSteps=1
        lngSteps = int((((max(rect[1], rect[3])-min(rect[1], rect[3])))/dlng)+0.75199999)
        if lngSteps<1:
            lngSteps=1
        for i in range(latSteps):
            for j in range(lngSteps):
                locations.append((startLat+(dlat*i), startLng+(dlng*j)))
        return locations

    def seen_before (self, loc):
        return self.get_spawn_location(loc) is not None

    def get_spawn_location (self, loc):
        for spawn_loc, spawn_data in self._spawn_locations.items():
            if close_enough(loc, spawn_loc):
                return spawn_loc, spawn_data
        return None

    def queue_locations (self, groups, full_scan=False):
        logging.info("Queueing locations to scan...")
        logging.info("Is full scan? {}".format(full_scan))

        now = time.time()
        total_queued = 0

        for group in groups:
            locations = self.get_locations(group)
            for loc in locations:
                # if we've seen this location before, and we've waited enough:
                # if doing a full scan, scan regardless of spawn count
                # otherwise, scan again only if spawn count is high enough
                if self.seen_before(loc):
                    spawn_loc, spawn_data = self.get_spawn_location(loc)
                    if (now - spawn_data["last_scan"]) < self._spawn_interval:
                        # haven't waited long enough yet
                        continue

                    if full_scan or (spawn_data["spawn_count"] >= self._spawn_count_threshold):
                        spawn_data["last_scan"] = now
                        self._scan_queue.put((loc, group))
                        total_queued += 1

                # always scan the new locations immediately
                else:
                    self._spawn_locations[loc] = {
                        "last_scan": now,
                        "spawn_count": self._spawn_count_threshold
                    }
                    self._scan_queue.put((loc, group))
                    total_queued += 1

        logging.info("Done queueing {} locations".format(total_queued))
