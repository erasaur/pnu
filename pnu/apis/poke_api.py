import asyncio, aiohttp, time
from math import cos, sin, atan2, sqrt, radians

from pnu.core.data_store import PnuUserDataStore
# from pnu.apis.pokevision_api import PokevisionAPI
from pnu.apis.pgo_api import PgoAPI
from pnu.config import pub_config
from pnu.models.user import User
from pnu.models.pokemon import Pokemon
from pnu.models.alert import Alert

import logging
logging = logging.getLogger(__name__)

class PnuPokeApi ():
    def __init__ (self, session=None):
        self._pgo_api = PgoAPI()
        # self._pokevision_api = PokevisionAPI(session=session)
        self._earth_radius = pub_config["poke_api"]["earth_radius"]
        self._group_step_count = pub_config["poke_api"]["group_scan_step_count"]
        self._last_update = 0
        self._groups = []

    def pos_changed (self, user_a, user_b):
        return self.distance(user_a, user_b) > 0

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

    def close_enough (self, user, group):
        for member in group:
            if distance(user, member) >= self._group_member_dist:
                return False
        return True

    def remove_user (self, user):
        for group in self._groups:
            for index, member in enumerate(group):
                if (member.get_phone_number() == user.get_phone_number()):
                    del group[index]
                    return

    def update_data (self, user, already_active):
        group_index = 0
        added_new = False
        deleted_old = not already_active # if not active, no old to delete

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
                if found_self: # update with our new position
                    group[old_index] = user
                else: # add our new position
                    group.append(user)
                added_new = True
            else:
                if found_self: # delete old copy of self
                    del group[old_index]
                    deleted_old = True

                    if len(group) < 1:
                        del self._groups[group_index]
                # else: keep on looking

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
            lat = radians(member.get_lat())
            lon = radians(member.get_lon())
            x += cos(lat) * cos(lon)
            y += cos(lat) * sin(lon)
            z += sin(lat)

        x = float(x / len(group))
        y = float(y / len(group))
        z = float(z / len(group))

        center_lat = atan2(z, sqrt(x * x + y * y))
        center_lon = atan2(y, x)

        # TODO: increase radius based on number of members in group
        return center_lat, center_lon, self._group_step_count

    def get_pokemon_alerts (self):
        pokes_nearby = self._pgo_api.get_nearby(42.277556681, -83.740878574,
                self._group_step_count)
        print(pokes_nearby)

        # for each such location, get the nearby pokes, and filter out the
        temp = {} # result to return
        fut_list = []
        print("Processing {} users...".format(len(self._groups)))
        logging.info("Processing {} users...".format(len(self._groups)))
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
