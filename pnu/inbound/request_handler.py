import threading

from pnu.config import pub_config
from pnu.etc import constants
from pnu.core.runnable import PnuRunnable
from pnu.core.data_store import PnuPendingDataStore
from pnu.core.data_store import PnuUserDataStore
from pnu.models.user import User
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

    def __init__ (self, poke_api=None):
        if poke_api is None:
            raise ValueError("missing poke api")

        super().__init__(update_interval=pub_config["request_handler"]["update_interval"])

        self._poke_api = poke_api
        self._requester = PnuRequest()

    def update (self):
        # query using PnuRequest api, write changes to store
        inbound_users = self._requester.run()
        for inbound_user in inbound_users:
            if inbound_user.empty():
                continue

            status = inbound_user.get_status()
            phone_number = inbound_user.get_phone_number()

            # check for status update on the inbound_user
            if status in constants.RESPONSE_STATUS_LIST:
                logging.info("Status update!")
                # sends correct status message based on status field
                if status == constants.STOP:
                    PnuUserDataStore.delete_user(phone_number)
                # resume or pause status
                else:
                    PnuUserDataStore.update(phone_number, inbound_user)

                logging.info("Setting user to be notified")
                PnuPendingDataStore.append(constants.ENROLL, inbound_user)
                continue

            # check if current user is already active
            old_user = User(PnuUserDataStore.get(phone_number))
            already_active = (old_user is not None and old_user.is_active())

            # we don't have BOTH the location and pokemon wanted, so they still
            # need to fully enroll
            PnuUserDataStore.update(phone_number, inbound_user)
            json_user = PnuUserDataStore.get(phone_number)
            json_user['status'] = constants.ENROLL
            user = User(json_user)

            # user still needs to fully enroll
            if not user.is_active():
                logging.info("User needs to send us more data")
                PnuPendingDataStore.append(constants.ENROLL, user)

            # user is fully enrolled. depending on whether they just enrolled,
            # or were already enrolled and simply updating their info, we want
            # to update the minimal location set differently (if they just
            # enrolled, we want to add a new entry; if not, we want to update an
            # existing entry)
            elif self._poke_api.pos_changed(old_user, user):
                self._poke_api.update_data(user, already_active)
