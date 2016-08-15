import time

from queue import Queue
from pnu.core.data_store import PnuUserDataStore
from pnu.config import pub_config
from pnu.models import User, Pokemon, Alert
from pnu.apis import PgoApi, PnuScanApi
from pnu.apis.poke_helpers import close_enough, get_center_of_group

import logging
logging = logging.getLogger(__name__)

class PnuPokeApi (PnuRunnable):

    def __init__ (self, dispatcher):
        self._queue = Queue()
        self._dispatcher = dispatcher
        self._pgo_api = PgoApi()
        self._scanner = PnuScanApi(self._queue)

        self._update_interval = pub_config["poke_api"]["update_interval_sec"]

        # only regularly scan locations with spawn count above a certain threshold
        self._last_scan = 0
        self._scan_interval = pub_config["poke_api"]["scan_interval_sec"]

        # perform a full scan every once in a while to catch missing spawn locations
        self._last_full_scan = 0
        self._full_scan_interval = pub_config["poke_api"]["full_scan_interval_sec"]

        # occasionally resync group data from data store
        self._last_sync = 0
        self._sync_group_data_interval = pub_config["poke_api"]["sync_group_data_interval_sec"]

        # users grouped by location
        self._groups = []

        # on startup, load existing users into memory
        self.sync_data_from_store()

    def run (self):
        super().run(self._update_interval)
        self.run_once(self.process_queue)

    def sync_data_from_store (self):
        # reset groups
        self._groups = []
        init_users = PnuUserDataStore.list()

        # re-add all active users
        for user in init_users:
            user = User(user)
            if user.is_active():
                self.update_data(user, True)

    def delete_user (self, phone_number):
        for group_index, group in enumerate(self._groups):
            for index, member in enumerate(group):
                if (member.get_phone_number() == phone_number):
                    del group[index]
                    if len(group) < 1:
                        del self._groups[group_index]
                    return

    def update_data (self, user, already_active):
        group_index = 0

        # tracks whether or not we updated with our new value yet
        added_new = False 

        # tracks whether or not we removed old value yet. if the user wasn't 
        # active before this function, no old one to delete, so default to true
        deleted_old = not already_active 

        for group in self._groups:
            index = 0
            old_index = -1
            for member in group:
                if member.get_phone_number() == user.get_phone_number():
                    old_index = index
                if not close_enough(user, member):
                    break
                index += 1

            close_enough_to_group = (index >= len(group))
            found_self = (old_index != -1)

            if close_enough_to_group:
                if found_self: # update with our new data
                    group[old_index] = user
                    deleted_old = True
                else: # add our new user
                    group.append(user)
                added_new = True
            else:
                if found_self: # delete old copy of self
                    del group[old_index]
                    deleted_old = True

                    if len(group) < 1:
                        del self._groups[group_index]
                # else: keep on looking for our old self if need be

            if added_new and deleted_old:
                break
            group_index += 1

        # create a new group just for this isolated user
        if group_index >= len(self._groups):
            self._groups.append([user])

    def send_alerts (self, group, pokes_nearby):
        res = {} # mapping of lists of pokemon to lists of users

        # if multiple users are going to be alerted of the same set of pokemon,
        # group those users together so we can notify them all at once
        logging.info("Found {} pokemon nearby".format(len(pokes_nearby)))
        if len(pokes_nearby) < 1:
            continue

        # sort so we get expiration times in ascending order, hence
        # check all copies of the newly appeared pokes
        pokes_nearby = sorted(
            pokes_nearby, 
            key=lambda poke: poke.get_expiration_time()
        )

        for user in group:
            curr = set() # don't want duplicates
            for poke in pokes_nearby:
                if user.should_be_alerted(poke):
                    curr.add(( # tuple order matters here
                        poke.get_id(), 
                        poke.get_lat(), 
                        poke.get_lon(),
                        poke.get_expiration_time()
                    ))
                    # TODO only need to set this once per unique poke, ie if
                    # have 100 same poke, only need to set to the last poke's
                    # time because we've sorted the list
                    user.set_last_notif_for_poke(poke)

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
                if poke_tuple in res:
                    res[poke_tuple].append(user)
                else:
                    res[poke_tuple] = [user]

        alerts = []
        if len(res) > 0:
            for poke_tuple, user_list in res.items():
                logging.info("\n\nsending to users: {}".format(user_list))
                for t in poke_tuple:
                    logging.info("{} ".format(t))
                logging.info("\n\n")
                alerts.append(Alert(poke_tuple, user_list))

        self._dispatcher.dispatch(alerts)

    def process_queue (self):
        while True:
            # blocks until there is something
            (loc, group) = self._queue.get()
            pokes_nearby = self._pgo_api.get_nearby(loc)

            if not self.seen_before(loc):
                logging.info("shouldn't enqueue unseen locations!")
                continue

            if len(pokes_nearby) > 0 :
                self._spawn_locations[loc]["spawn_count"] += 1
            else:
                self._spawn_locations[loc]["spawn_count"] -= 1

            self.send_alerts(group, pokes_nearby)

    def update (self):
        now = time.time()
        if (now - self._last_sync >= self._sync_group_data_interval):
            self.sync_data_from_store()
            self._last_sync = now

        if (now - self._last_full_scan >= self._full_scan_interval):
            full_scan = True
            self._full_scan_interval = now
        elif (now - self._last_scan >= self._scan_interval):
            full_scan = False
            self._scan_interval = now

        self._scanner.scan(self._groups, full_scan)
