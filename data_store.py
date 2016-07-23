import redis

class PnuDataStore ():
    def __init__ (self, host=None, port=None):
        if host is None or port is None:
            raise ValueError('Missing host or port')

        self._redis = redis.StrictRedis(host=host, port=port, db=0)

    def get (key):
        return self._redis.get(key)

    def set (key, val):
        return self._redis.set(key, val)
