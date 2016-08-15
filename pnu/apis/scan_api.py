from pnu.apis.poke_helpers import close_enough, get_coor_in_dir
from pnu.config import pub_config

class PnuScanApi ():

    def __init__ (self, queue=None):
        if queue is None:
            raise ValueError("missing scan queue")
        self._queue = queue

        # locations we know that have spawns
        self._spawn_locations = {}

        # minimal count to be considered for regular spawn
        self._spawn_count_threshold = pub_config["poke_api"]["spawn_count_threshold"]

        # how far to scan per group
        self._group_scan_radius = pub_config["poke_api"]["group_scan_radius_km"]

        # on startup, load known scan locations into memory
        self.update_locations_from_file(pub_config["poke_api"]["scan_locations_file"])

    def update_locations_from_file (self, file_name):
        with open(file_name, "w") as f:
            self._spawn_locations = json.load(f) 

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

    def get_locations (self, group, steps=None):
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

    def scan (self, groups, full_scan=False):
        now = time.time()
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
                        self._queue.add((loc, group))

                # always scan the new locations immediately
                else:
                    self._spawn_locations[loc] = {
                        "last_scan": now,
                        "spawn_count": self._spawn_count_threshold
                    }
                    self._queue.add((loc, group))
