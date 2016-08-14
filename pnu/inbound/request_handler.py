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

class PnuRequestHandler (PnuRunnable):

    def __init__ (self, poke_api=None):
        if poke_api is None:
            raise ValueError("missing poke api")

        super().__init__(update_interval=pub_config["request_handler"]["update_interval"])

        self._poke_api = poke_api
        self._requester = PnuRequest()

    def update(self):
        # query using PnuRequest api, write changes to store
        inbound_users = self._requester.run()
        for inbound_user in inbound_users:
            if inbound_user.empty():
                logging.info("Empty user: {}".format(inbound_user.get_json()))
                continue

            status = inbound_user.get_status()
            phone_number = inbound_user.get_phone_number()

            # check if current user is already active
            old_user = User(PnuUserDataStore.get(phone_number))
            old_user_exists = not old_user.empty()
            old_user_active = old_user_exists and old_user.is_active()

            # check for status update on the inbound_user
            if status in constants.RESPONSE_STATUS_LIST:
                # makes no sense to update status of non-existent user
                if not old_user_exists:
                    continue

                logging.info("Status update!")
                user_to_notify = old_user

                # sends correct status message based on status field
                if status == constants.STOP:
                    user_to_notify = inbound_user
                    self._poke_api.delete_user(phone_number)
                    PnuUserDataStore.delete(phone_number)
                # resume or pause status
                else:
                    # only save the update and save the status if pause is sent
                    if inbound_user.get_status() == constants.PAUSE:
                        PnuUserDataStore.update(phone_number, inbound_user)
                        user_to_notify = PnuUserDataStore.get(phone_number)
                        logging.info("Pausing user based on PAUSE message")

                    # so we don't actually save the 'RESUME' status
                    if inbound_user.get_status() == constants.RESUME:
                        # clear the previous status of 'PAUSE' for the user
                        # and update it in the store
                        inbound_user.set_status('')
                        PnuUserDataStore.update(phone_number, inbound_user)
                        user_to_notify = PnuUserDataStore.get(phone_number)
                        user_to_notify['status'] = constants.RESUME
                        logging.info("Bringing user into normal alert cycle " +
                                     "base on RESUME message")

                logging.info("Setting user to be notified: {}"
                             .format(user_to_notify))
                PnuPendingDataStore.append(constants.ENROLL, user_to_notify)
                # don't need to send any more messages so continue to the
                # next person to be messaged
                continue

            # at this point, we know the user is either updating their location
            # or their list of pokemon wanted (potentially for the first time)
            logging.info("Updating inbound_user to see if their account is " +
                         "complete")
            PnuUserDataStore.update(phone_number, inbound_user)
            json_user = PnuUserDataStore.get(phone_number)
            json_user['status'] = constants.ENROLL
            user = User(json_user)
            logging.info("The full inbound_user account is: {}"
                         .format(user.get_json()))

            # user still needs to fully enroll
            if not user.is_active():
                logging.info("User needs to send us more data")
                PnuPendingDataStore.append(constants.ENROLL, user)

            # user is fully enrolled. depending on whether they just enrolled,
            # or were already enrolled and simply updating their info, we want
            # to update our data set differently (if they just enrolled, we want 
            # to add a new entry; if not, we want to update an existing entry),
            # hence we pass in the `old_user_active` flag.
            else:
                logging.info("User is fully enrolled")
                PnuPendingDataStore.append(constants.ENROLL, user)
                self._poke_api.update_data(user, old_user_active)
