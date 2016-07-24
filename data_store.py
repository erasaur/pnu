import redis, time
from config import pub_config

class RedisDataStore ():
    def __init__ (self, host=None, port=None):
        if host is None or port is None:
            raise ValueError('Missing host or port')

        self._redis = redis.StrictRedis(host=host, port=port, db=0)
        self._last_update = time.time()

    def get (key):
        try:
            res = json.loads(self._redis.get(key))
        except Exception:
            res = {}
        return res

    def update (key, val):
        try:
            curr = self.get(key)
            for k, v in val.iteritems():
                curr[k] = v
            self.set(key, curr)
        except Exception:
            print('invalid json value')

    def set (key, val):
        try:
            self._redis.set(key, json.dumps(val))
            self._last_update = time.time()
        except Exception:
            print('invalid json value') # TODO logging

    def list ():
        res = []
        for doc in self._redis.lrange(0, -1):
            try:
                res.append(json.loads(doc))
            except Exception:
                print('unable to load doc') # TODO logging
        return res

    def changed_since (time):
        return self._last_update > time

PnuDataStore = RedisDataStore(
    host=pub_config["data_store"]["host"],
    port=pub_config["data_store"]["port"]
)
