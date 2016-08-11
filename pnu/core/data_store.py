import redis
import time
import json

from pnu.config import pub_config
from pnu.models import Base

import logging
logging = logging.getLogger(__name__)


class RedisDataStore ():

    def __init__(self, host=None, port=None):
        if host is None or port is None:
            raise ValueError('Missing host or port')

        self._redis = redis.StrictRedis(host=host, port=port, db=0)
        self._last_update = time.time()

    def get(self, key):
        try:
            res = self._redis.get(key)
            res = res.decode("utf-8")
            res = json.loads(res)
        except Exception as e:
            logging.info('get failed, got exception: {}'.format(e))
            logging.info('tried to get {}'.format(key))
            res = {}
        return res

    # pass json document with ONLY the fields that need to be updated.
    # for example, suppose we have stored:
    # < "elemA": { "fieldA": 1, "fieldB": 2 } >
    # to update "fieldA" but keep "fieldB" intact, call:
    # update("elemA", { "fieldA": 2 })
    # if the key "elemA" doesn't exist, it will be set.
    def update(self, key, val):
        try:
            if (isinstance(val, Base)):
                val = val.get_json()

            curr = self.get(key)

            logging.info("prev: {}".format(curr))

            for k, v in val.items():
                if v is not None:
                    curr[k] = v
            self.set(key, curr)

            logging.info("now: {}".format(self.get(key)))
        except Exception as e:
            logging.info('update failed, got exception: {}'.format(e))
            logging.info('tried to update {} to {}'.format(key, val))

    def set(self, key, val):
        try:
            if (isinstance(val, Base)):
                val = val.get_json()

            self._redis.set(key, json.dumps(val))
            self._last_update = time.time()
        except Exception as e:
            logging.info('set failed, got exception: {}'.format(e))
            logging.info('tried to set {} to {}'.format(key, val))

    def list(self):
        res = []
        keys = self._redis.keys(pattern="*")
        for key in keys:
            try:
                res.append(self.get(key))
            except Exception as e:
                logging.info('list failed, got exception: {}'.format(e))
                logging.info('tried to load {}'.format(doc))
        return res

    def changed_since(self, time):
        return self._last_update > time

    def append(self, key, val):
        try:
            if (isinstance(val, Base)):
                val = val.get_json()

            self._redis.lpush(key, json.dumps(val))
        except Exception as e:
            logging.info('append failed, got exception: {}'.format(e))
            logging.info('tried to append {} to {}'.format(key, val))

    def pop(self, pop_key):
        try:
            _, raw_user = self._redis.blpop(pop_key)
            raw_user = raw_user.decode("utf-8")
            raw_user = json.loads(raw_user)
        except Exception as e:
            raw_user = {}
        return raw_user

    def delete_user(self, del_key):
        logging.info("Deleting user: {}".format(del_key))
        _ = self._redis.delete(del_key)


class UserDataStore(RedisDataStore):

    def __init__(self):
        super().__init__(
            host=pub_config["user_data_store"]["host"],
            port=pub_config["user_data_store"]["port"]
        )

    def update(self, key, val):
        try:
            if isinstance(val, Base):
                val = val.get_json()

            # reset last_notif if changing pokemon list
            if "pokemon_wanted" in val:
                val["last_notif"] = {}
            super().update(key, val)
        except Exception as e:
            logging.info('user update failed, got exception: {}'.format(e))
            logging.info('tried to update {} to {}'.format(key, val))

PnuUserDataStore = UserDataStore()
PnuPendingDataStore = RedisDataStore(
    host=pub_config["pending_data_store"]["host"],
    port=pub_config["pending_data_store"]["port"]
)
