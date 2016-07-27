import threading

from pnu.config import pub_config
from pnu.etc import constants
from pnu.core.runnable import PnuRunnable
from pnu.core.data_store import PnuEnrollDataStore
from pnu.inbound.requester import PnuRequest

import logging
logger = logging.getLogger(__name__)

# TODO
# handler should be responsible for parsing incoming requests and updating the
# data store appropriately

# behind the scenes, the handler class might rely on the gmail api, some form of
# sms api, etc. but should expose an interface that is agnostic to the method by
# which we are obtaining data (gmail, sms, and so on)

from pnu.core.data_store import PnuUserDataStore

class PnuRequestHandler (PnuRunnable):
    def __init__ (self):
        super().__init__(update_interval=pub_config["request_handler"]["update_interval"])

        self._requester = PnuRequest()

    def update (self):
        # query using PnuRequest api, write changes to store
        for new_msg in self._requester.run():
            # if the user is not active, then we'll be sending them
            # an immediate message
            if user.get_status() != constants.ACTIVE:
                PnuEnrollDataStore.set(user.get_phone_number(), user)
            # user is active so we add them to the alert queue
            else:
                PnuUserDataStore.update(user.get_phone_number(), user.get_json())
