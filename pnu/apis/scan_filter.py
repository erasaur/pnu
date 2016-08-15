import time, json

from pnu.core.runnable import PnuRunnable
from pnu.apis.geo import close_enough, get_coor_in_dir
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

        # how far to scan per group
        self._group_scan_radius = pub_config["scan_filter"]["group_scan_radius_km"]

        # on startup, load known scan locations into memory
        self.sync_from_file()

        # how often to sync data to file
        self._sync_to_file_interval = pub_config["scan_filter"]["sync_to_file_interval_sec"]

        super().__init__(update_interval=self._update_interval)

    def update (self):
        now = time.time()
        if now - self._last_sync >= self._sync_to_file_interval:
            self.sync_to_file()

    def sync_from_file (self):
        logging.info("Syncing locations from file...")
        logging.info("Previously had {} locations".format(len(self._spawn_locations)))

        with open(self._sync_file, "r") as f:
            try:
                self._spawn_locations = json.load(f) 
            except:
                logging.info("Error reading spawn locations from file")
                self._spawn_locations = {}

        logging.info("Now have {} locations".format(len(self._spawn_locations)))
        logging.info("Done syncing locations")

    def sync_to_file (self):
        logging.info("Syncing locations to file...")

        with open(self._sync_file, "w") as f:
            json.dump(self._spawn_locations, f)
        self._last_sync = time.time()

        logging.info("Done syncing locations")

    def update_data (self, loc, pokes):
        if loc not in self._spawn_locations:
            logging.info("trying to update filter data with invalid data")
            return
        if len(pokes) > 0:
            self._spawn_locations[loc] += 1
        else:
            self._spawn_locations[loc] -= 1

    def get_corners (self, group):
        NORTH = 0
        EAST = 90
        SOUTH = 180
        WEST = 270
        
        radius = self._group_scan_radius
        xdist = ydist = sqrt(2)/2 * radius

        bot_left = get_coor_in_dir(loc, ydist, SOUTH)
        bot_left = get_coor_in_dir(bot_left, xdist, WEST)

        top_right = get_coor_in_dir(loc, ydist, NORTH)
        top_right = get_coor_in_dir(top_right, xdist, EAST)
        
        return (bot_left[0], bot_left[1], top_right[0], top_right[1])

    def get_locations (self, group):
        locations = []
        bot_left, top_right = self.get_corners(group)
        dlat = 0.00089
        dlng = dlat / math.cos(math.radians((bot_left[0]+top_right[2])*0.5))
        startLat = min(bot_left[0], top_right[2])+(0.624*dlat)
        startLng = min(bot_left[1], top_right[3])+(0.624*dlng)
        latSteps = int((((max(bot_left[0], top_right[2])-min(bot_left[0], top_right[2])))/dlat)+0.75199999)
        if latSteps<1:
            latSteps=1
        lngSteps = int((((max(bot_left[1], top_right[3])-min(bot_left[1], top_right[3])))/dlng)+0.75199999)
        if lngSteps<1:
            lngSteps=1
        for i in range(latSteps):
            for j in range(lngSteps):
                locations.append((startLat+(dlat*i), startLng+(dlng*j)))
        return locations

    def seen_before (self, loc, spawn_locations):
        for spawn_loc in spawn_locations:
            if not close_enough(loc, spawn_loc):
                return False
        return True

    def queue_locations (self, groups, full_scan=False):
        logging.info("Queueing locations to scan...")

        now = time.time()
        total_queued = 0

        for group in groups:
            locations = self.get_locations(group)
            for loc in locations:
                # if we've seen this location before, and we've waited enough:
                # if doing a full scan, scan regardless of spawn count
                # otherwise, scan again only if spawn count is high enough
                if self.seen_before(loc, self._spawn_locations):
                    loc_data = self._spawn_locations[loc]
                    if (now - loc_data["last_scan"]) < self._spawn_interval:
                        # haven't waited long enough yet
                        continue

                    if full_scan or (loc_data["spawn_count"] >= self._spawn_count_threshold):
                        loc_data["last_scan"] = now
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
