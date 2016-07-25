import threading

from requester import PnuRequest
from runnable import PnuRunnable
from config import pub_config

# TODO
# handler should be responsible for parsing incoming requests and updating the
# data store appropriately

# behind the scenes, the handler class might rely on the gmail api, some form of
# sms api, etc. but should expose an interface that is agnostic to the method by
# which we are obtaining data (gmail, sms, and so on)

class PnuRequestHandler (PnuRunnable):
    def __init__ (self, loop=None, store=None):
        if loop is None or store is None:
            raise ValueError('missing loop or store')

        super().__init__(pub_config['request_handler']['update_interval'])

        self._requester = PnuRequest()

        self._loop = loop
        self._store = store

    async def update (self):
        # query using PnuRequest api, write changes to store
        for new_msg in self._requester.run():
            # the value is a tuple right now so that we can contain the location
            # and pokemon_wanted all in one collection
            self._store.set(new_msg['phone_number'], {new_msg['location'],
                    new_msg['pokemon_wanted']})

