import asyncio

from runnable import PnuRunnable
from poke_api import PnuPokeApi
from request_handler import PnuRequestHandler
from alert_dispatcher import PnuAlertDispatcher
from data_store import PnuDataStore

# how often to dispatch alerts
UPDATE_INTERVAL = 5.0 # seconds
STORE_HOST = 'localhost'
STORE_PORT = 1337

class Pnu (PnuRunnable):
    def __init__ (self):
        super().__init__(UPDATE_INTERVAL)

        # initialize event loop
        loop = asyncio.get_event_loop()

        # initialize data store
        # data_store = PnuDataStore(host=CACHE_HOST, port=CACHE_PORT)

        # initialize api clients
        self._loop = loop
        # self._store = data_store
        # self._poke_api = PnuPokeApi(loop=loop)
        # self._handler = PnuRequestHandler(loop=loop, store=store)

    def run (self):
        super().run()
        self._handler.run()
        self._loop.run_forever()

    def update (self):
        # query poke api and store new (just appeared) pokemon in a list

        # run through each "hotspot" location and check if any new pokes are in
        # a user's whitelist

        # send alerts with dispatcher
        pass

