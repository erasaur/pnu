#! /usr/bin/env python3.5

import asyncio, aiohttp
from contextlib import suppress

from pnu.core.runnable import PnuRunnable
from pnu.config import pub_config
from pnu.apis.poke_api import PnuPokeApi
from pnu.inbound.request_handler import PnuRequestHandler
from pnu.outbound.alert_dispatcher import PnuAlertDispatcher
from pnu.etc.logging import ConfigureLogging


class Pnu (PnuRunnable):
    def __init__(self):
        # initialize event loop
        loop = asyncio.get_event_loop()

        super().__init__(update_interval=pub_config["pnu"]["update_interval"])

        # initialize api clients
        self._loop = loop

        # session = aiohttp.ClientSession(loop=loop)
        # self._session = session

        self._poke_api = PnuPokeApi()
        self._handler = PnuRequestHandler(poke_api=self._poke_api)
        self._dispatcher = PnuAlertDispatcher()

    # def __exit__ (self):
    #     self._session.close()
    #     self._loop.close()

    def run(self):
        super().run()
        self._handler.run()
        self._dispatcher.run()
        self._loop.run_forever()

    def send_alerts(self):
        alerts = self._poke_api.get_pokemon_alerts()
        # send alerts with dispatcher
        self._dispatcher.dispatch(alerts)

    # def clear_tasks (self):
    #     # TODO only clear tasks for aiohttp loop used for poke api requests
    #     # currently, aiohttp is only used for that purpose so this is fine
    #     tasks = asyncio.Task.all_tasks(loop=self._loop)
    #     for task in tasks:
    #         task.cancel()
    #         with suppress(asyncio.CancelledError):
    #             self._loop.run_until_complete(task)

    def update(self):
        super().update()

        # cancel all tasks that are still pending
        # self.clear_tasks()

        # start new batch of tasks
        self.send_alerts()
        # asyncio.ensure_future(self.send_alerts(), loop=self._loop)


def main():
    Pnu().run()

if __name__ == "__main__":
    ConfigureLogging()
    main()
