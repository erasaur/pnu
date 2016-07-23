import threading

from runnable import PnuRunnable

# TODO
# handler should be responsible for parsing incoming requests and updating the
# data store appropriately

# behind the scenes, the handler class might rely on the gmail api, some form of
# sms api, etc. but should expose an interface that is agnostic to the method by
# which we are obtaining data (gmail, sms, and so on)

# how often to check for new requests
UPDATE_INTERVAL = 5.0 # seconds

class PnuRequestHandler (PnuRunnable):
    def __init__ (self, loop=None, store=None):
        if loop is None or store is None:
            raise ValueError('missing loop or store')

        super().__init__(UPDATE_INTERVAL)

        # TODO initialize Gmail api

        self._loop = loop
        self._store = store

    def update (self):
        # query using Gmail api, write changes to store
        pass
