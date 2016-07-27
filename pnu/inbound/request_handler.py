import threading

from pnu.config import pub_config
from pnu.etc.constants import RESPONSE_STATUS_LIST
from pnu.core.runnable import PnuRunnable
from pnu.core.data_store import PnuPendingDataStore
from pnu.core.data_store import PnuUserDataStore
from pnu.inbound.requester import PnuRequest

import logging
logging = logging.getLogger(__name__)

# TODO
# handler should be responsible for parsing incoming requests and updating the
# data store appropriately

# behind the scenes, the handler class might rely on the gmail api, some form of
# sms api, etc. but should expose an interface that is agnostic to the method by
# which we are obtaining data (gmail, sms, and so on)


class PnuRequestHandler (PnuRunnable):

    def __init__ (self):
        super().__init__(update_interval=pub_config["request_handler"]["update_interval"])

        self._requester = PnuRequest()

    def update (self):
        # query using PnuRequest api, write changes to store
        for inbound_user in self._requester.run():
            if inbound_user.empty():
                continue

            # check for status update on the inbound_user
            if inbound_user.get_status() in RESPONSE_STATUS_LIST:
                # sends correct status message based on status field
                if inbound_user.get_status() == constants.STOP:
                    PnuUserDataStore.delete_user(inbound_user.get_phone_number())
                # resume or pause status
                else:
                    PnuUserDataStore.update(inbound_user.get_phone_number(),
                            inbound_user)
                PnuPendingDataStore.set(inbound_user.get_phone_number(),
                        inbound_user)
                continue

            # we don't have BOTH the location and pokemon wanted, so they still
            # need to fully enroll
            PnuUserDataStore.update(inbound_user.get_phone_number(), inbound_user)
            json_user = PnuUserDataStore.get(inbound_user.get_phone_number())
            user = User(json_user)
            # user still needs to fully enroll
            if (user.get_location_is_set() != user.get_pokemon_wanted()):
                PnuPendingDataStore.set(inbound_user.get_phone_number(), inbound_user)
