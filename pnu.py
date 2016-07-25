import asyncio

from runnable import PnuRunnable
from poke_api import PnuPokeApi
from request_handler import PnuRequestHandler
from alert_dispatcher import PnuAlertDispatcher
from data_store import PnuDataStore
from config import pub_config

class Pnu (PnuRunnable):
    def __init__ (self):
        super().__init__(pub_config["pnu"]["update_interval"])

        # initialize event loop
        loop = asyncio.get_event_loop()

        # initialize api clients
        self._loop = loop

        with aiohttp.ClientSession(loop=loop) as session:
            self._poke_api = PnuPokeApi(session=session)
            self._handler = PnuRequestHandler(session=session, store=store)
            self._dispatcher = PnuAlertDispatcher(session=session)

    def run (self):
        super().run()
        self._handler.run()
        self._loop.run_forever()

    def update (self):
        alerts = self._poke_api.get_new_pokemon()

        # send alerts with dispatcher
        self._dispatcher.send(alerts)
