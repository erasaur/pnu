#! /usr/bin/env python3.5

import asyncio, aiohttp
from contextlib import suppress

from pnu.core.runnable import PnuRunnable
from pnu.config import pub_config
from pnu.apis.poke_api import PnuPokeApi
from pnu.inbound.request_handler import PnuRequestHandler
from pnu.outbound.alert_dispatcher import PnuAlertDispatcher

class Pnu (PnuRunnable):
    def __init__ (self):
        # initialize event loop
        loop = asyncio.get_event_loop()

        super().__init__(update_interval=pub_config["pnu"]["update_interval"])

        # initialize api clients
        self._loop = loop
        self._curr_task = None

        with aiohttp.ClientSession(loop=loop) as session:
            self._poke_api = PnuPokeApi(session=session)
            self._handler = PnuRequestHandler()
            self._dispatcher = PnuAlertDispatcher()

    def run (self):
        super().run()
        self._handler.run()
        self._loop.run_forever()

    async def fetch_new_pokemon (self):
        alerts = await self._poke_api.get_new_pokemon()
        print(alerts)
        # send alerts with dispatcher
        self._dispatcher.dispatch(alerts)

    def clear_tasks (self):
        # TODO only clear tasks for aiohttp loop used for poke api requests
        # currently, aiohttp is only used for that purpose so this is fine
        tasks = asyncio.Task.all_tasks(loop=self._loop)
        for task in tasks:
            task.cancel()
            with suppress(asyncio.CancelledError):
                self._loop.run_until_complete(task)

    def update (self):
        super().update()

        # cancel all tasks that are still pending
        self.clear_tasks()

        # start new batch of tasks
        asyncio.ensure_future(self.fetch_new_pokemon(), loop=self._loop)

def main ():
    Pnu().run()

if __name__ == "__main__":
    import logging.config
    logging.config.fileConfig(pub_config["logging"]["location"],
            disable_existing_loggers=False)
    main()
