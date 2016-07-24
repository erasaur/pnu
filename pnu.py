import asyncio

from runnable import PnuRunnable
from poke_api import PnuPokeApi
from request_handler import PnuRequestHandler
from alert_dispatcher import PnuAlertDispatcher
from data_store import PnuDataStore
<<<<<<< HEAD
from config import Config


class Pnu (PnuRunnable):
    def __init__ (self):
        super().__init__(UPDATE_INTERVAL)
        self.config = Config().load_config()
=======
from config import JSONConfig

class Pnu (PnuRunnable):
    def __init__ (self):
        super().__init__(JSONConfig["pnu"]["update_interval"])

        # initialize data store
        data_store = PnuDataStore(
            host=JSONConfig["pnu"]["store_host"], 
            port=JSONConfig["pnu"]["store_port"])
>>>>>>> 23d7508da74a06ec284d46507df705663b6b2bcb

        # initialize event loop
        loop = asyncio.get_event_loop()

<<<<<<< HEAD
        # initialize data store
        # data_store = PnuDataStore(host=self.config['pnu']['store_host'],
        #    port=self.config['pnu']['cache_port'])

=======
>>>>>>> 23d7508da74a06ec284d46507df705663b6b2bcb
        # initialize api clients
        self._loop = loop
        self._store = data_store

        with aiohttp.ClientSession(loop=loop) as session:
            self._poke_api = PnuPokeApi(session=session)
            self._handler = PnuRequestHandler(session=session, store=store)
            self._dispatcher = PnuAlertDispatcher(session=session)

    def run (self):
        super().run()
        self._handler.run()
        self._loop.run_forever()

    def update (self):
        # query poke api and store new (just appeared) pokemon in a list
        curr_pokes = self._poke_api.get_pokemon()

        # run through each "hotspot" location and check if any new pokes are in
        # a user's whitelist
        users = self._data_store.list() # list of all users
        alerts = [] # list of alerts to send out

        for user in users:
            pokemon = [] # pokemon that user might be interested in
            for poke in curr_pokes:
                if self._poke_api.is_nearby(poke["location"], user["location"]):
                    pokemon.append(poke)

            if len(pokemon) > 0:
                alerts.append({
                    "phone": user["phone"],
                    "pokemon": pokemon
                })

        # send alerts with dispatcher
        self._dispatcher.send(alerts)
