import threading

from pnu.core.runnable import PnuRunnable
from pnu.config import pub_config
from pnu.inbound.requester import PnuRequest

# TODO
# handler should be responsible for parsing incoming requests and updating the
# data store appropriately

# behind the scenes, the handler class might rely on the gmail api, some form of
# sms api, etc. but should expose an interface that is agnostic to the method by
# which we are obtaining data (gmail, sms, and so on)

class PnuRequestHandler (PnuRunnable):
    def __init__ (self, store=None):
        if store is None:
            raise ValueError("missing store")

        super().__init__(pub_config["request_handler"]["update_interval"])

        self._requester = PnuRequest()
        self._store = store

    async def update (self):
        # query using PnuRequest api, write changes to store
        for new_msg in self._requester.run():
            # each new message represents a new user
            user = User(new_msg)
            self._store.update(user.get_phone_number(), user.get_json())

