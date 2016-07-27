import redis, time, json
import logging
logging = logging.getLogger(__name__)

from pnu.config import pub_config
from pnu.models.base import Base

class RedisDataStore ():
    def __init__ (self, host=None, port=None):
        if host is None or port is None:
            raise ValueError('Missing host or port')

        self._redis = redis.StrictRedis(host=host, port=port, db=0)
        self._last_update = time.time()

    def get (self, key):
        try:
            res = json.loads(self._redis.get(key))
        except Exception:
            res = {}
        return res

    # pass json document with ONLY the fields that need to be updated.
    # for example, suppose we have stored:
    # < "elemA": { "fieldA": 1, "fieldB": 2 } >
    # to update "fieldA" but keep "fieldB" intact, call:
    # update("elemA", { "fieldA": 2 })
    # if the key "elemA" doesn't exist, it will be set.
    def update (self, key, val):
        try:
            if (isinstance(val, Base)):
                val = val.get_json()

            curr = self.get(key)
            for k, v in val.items():
                if v is not None:
                    curr[k] = v
            self.set(key, curr)
        except Exception as e:
            logging.info('update failed, got exception: {}'.format(e))
            logging.info('tried to update {} to {}'.format(key, val))

    def set (self, key, val):
        try:
            if (isinstance(val, Base)):
                val = val.get_json()

            self._redis.set(key, json.dumps(val))
            self._last_update = time.time()
        except Exception as e:
            logging.info('set failed, got exception: {}'.format(e))
            logging.info('tried to set {} to {}'.format(key, val))

    def list (self):
        res = []
        keys = self._redis.keys(pattern="*")
        for key in keys:
            try:
                res.append(self.get(key))
            except Exception:
                logging.info('list failed, got exception: {}'.format(e))
                logging.info('tried to load {}'.format(doc))
        return res

    def changed_since (self, time):
        return self._last_update > time

    def append (self, key, val):
        logging.log("Appending: " + str(key) + ' ' + str(val))
        self._redis.lpush(key, val)

    def pop(self, pop_key):
        _, raw_user = self._redis.blpop(pop_key)
        return raw_user

    def delete_user(self, del_key):
        logging.info("Deleting user: " + str(del_key))
        _ = self._redis.delete(del_key)


PnuUserDataStore = RedisDataStore(
    host=pub_config["user_data_store"]["host"],
    port=pub_config["user_data_store"]["port"]
)

PnuPendingDataStore = RedisDataStore(
    host=pub_config["pending_data_store"]["host"],
    port=pub_config["pending_data_store"]["port"]
)
