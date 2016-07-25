#! /usr/bin/env python3.5

import asyncio, aiohttp

from pnu.core.runnable import PnuRunnable
from pnu.core.data_store import PnuDataStore

from pnu.config import pub_config
from pnu.apis.poke_api import PnuPokeApi
from pnu.inbound.request_handler import PnuRequestHandler
from pnu.outbound.alert_dispatcher import PnuAlertDispatcher

class Pnu (PnuRunnable):
    def __init__ (self):
        super().__init__(pub_config["pnu"]["update_interval"])

        # initialize event loop
        loop = asyncio.get_event_loop()

        # initialize api clients
        self._loop = loop

        with aiohttp.ClientSession(loop=loop) as session:
            self._poke_api = PnuPokeApi(session=session)
            self._handler = PnuRequestHandler(store=store)
            self._dispatcher = PnuAlertDispatcher()

    def run (self):
        super().run()
        self._handler.run()
        self._loop.run_forever()

    async def update (self):
        alerts = await self._poke_api.get_new_pokemon()

        # send alerts with dispatcher
        self._dispatcher.send(alerts)

def main ():
    Pnu().run()

if __name__ == "__main__":
    import logging.config
    logging.config.fileConfig(pub_config["logging"]["location"],
            disable_existing_loggers=False)
    main()
