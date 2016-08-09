import asyncio, aiohttp, time
from math import cos, sin, atan2, sqrt, radians, pi

from pnu.core.data_store import PnuUserDataStore
from pnu.apis.pgo_api import PgoAPI
from pnu.config import pub_config
from pnu.models.user import User
from pnu.models.pokemon import Pokemon
from pnu.models.alert import Alert

import logging
logging = logging.getLogger(__name__)

class PnuPokeApi ():
    def __init__ (self):
        self._pgo_api = PgoAPI()
        self._earth_radius = pub_config["poke_api"]["earth_radius_km"]
        self._group_member_dist = pub_config["poke_api"]["group_member_dist_km"]
        self._group_scan_dist = pub_config["poke_api"]["group_scan_dist_km"]
        self._step_size = pub_config["poke_api"]["step_size_km"]
        self._last_update = 0
        self._groups = []

        init_users = PnuUserDataStore.list()
        for user in init_users:
            user = User(user)
            if user.is_active():
                self.update_data(user, True)

    def pos_changed (self, user_a, user_b):
        if user_a is None or user_b is None:
            raise ValueError("invalid users")
        return (user_a.is_active() != user_b.is_active()) or (self.distance(user_a, user_b) > 0)

    def distance (self, user_a, user_b):
        lat1 = radians(float(user_a.get_lat()))
        lon1 = radians(float(user_a.get_lon()))
        lat2 = radians(float(user_b.get_lat()))
        lon2 = radians(float(user_b.get_lon()))

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return self._earth_radius * c

    def close_enough (self, user_a, user_b):
        return self.distance(user_a, user_b) < self._group_member_dist

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
                if not self.close_enough(user, member):
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
        self._last_update = time.time()

    def get_cover (self, group):
        x = 0
        y = 0
        z = 0

        for member in group:
            lat = radians(float(member.get_lat()))
            lon = radians(float(member.get_lon()))
            x += cos(lat) * cos(lon)
            y += cos(lat) * sin(lon)
            z += sin(lat)

        x = float(x / len(group))
        y = float(y / len(group))
        z = float(z / len(group))

        center_lat = 180 * atan2(z, sqrt(x * x + y * y)) / pi
        center_lon = 180 * atan2(y, x) / pi

        step_count = int(self._group_scan_dist / self._step_size)

        # TODO: increase radius based on number of members in group
        return center_lat, center_lon, step_count

    def get_pokemon_alerts (self):
        # for each such location, get the nearby pokes, and filter out the
        temp = {} # result to return
        fut_list = []
        logging.info("Have {} users...".format(len(PnuUserDataStore.list())))
        logging.info("Processing {} groups...".format(len(self._groups)))
        for group in self._groups:
            if len(group) < 1:
                logging.info("Something's wrong with the grouping code!")
                continue

            lat, lon, step_radius = self.get_cover(group)
            pokes_nearby = self._pgo_api.get_nearby(lat, lon, step_radius)

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
                    if poke_tuple in temp:
                        temp[poke_tuple].append(user)
                    else:
                        temp[poke_tuple] = [user]

        res = []
        if len(temp) > 0:
            logging.info("\n\n-------START--------\n\n")
            for poke_tuple, user_list in temp.items():
                logging.info("\n\nsending to users: {}".format(user_list))
                for t in poke_tuple:
                    logging.info("{} ".format(t))
                logging.info("\n\n")
                res.append(Alert(poke_tuple, user_list))
            logging.info("\n\n-------END--------\n\n")

        return res
