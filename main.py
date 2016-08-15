#! /usr/bin/env python3.5

import asyncio, threading

from pnu.core.runnable import PnuRunnable
from pnu.config import pub_config
from pnu.apis import PnuPokeApi
from pnu.inbound.request_handler import PnuRequestHandler
from pnu.outbound.alert_dispatcher import PnuAlertDispatcher
from pnu.etc.logging import ConfigureLogging

import logging
logging = logging.getLogger(__name__)

class Pnu (PnuRunnable):
    def __init__ (self):
        # handler alerts poke api, which then alerts dispatcher
        self._dispatcher = PnuAlertDispatcher()
        self._poke_api = PnuPokeApi(dispatcher=self._dispatcher)
        self._handler = PnuRequestHandler(poke_api=self._poke_api)

        super().__init__(update_interval=10)

    def run (self):
        super().run()
        self._handler.run() # begin handling inbound requests
        self._dispatcher.run() # begin dispatching text responses
        self._poke_api.run() # begin scanning for pokemon
        asyncio.get_event_loop().run_forever() # start update loops

    def update (self):
        logging.info("Running a total of {} threads".format(threading.active_count()))

if __name__ == "__main__":
    ConfigureLogging()
    Pnu().run()
