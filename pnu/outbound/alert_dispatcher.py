from pnu.core.runnable import PnuRunnable
from pnu.core.data_store import PnuUserDataStore, PnuPendingDataStore
from pnu.etc import constants
from pnu.models import User
from pnu.outbound.alerter import smtp

import json
import logging
logging = logging.getLogger(__name__)


class PnuAlertDispatcher(PnuRunnable):
    def run(self):
        self.run_once(self.prompt_alerts)

    def dispatch(self, alerts):
        # pokemon object tuples will be returned
        # followed by a list of users who need to be notified
        # for the said pokemon
        for alert in alerts:
            log_msg = "Dispatching message for {} to {}\n".format(
                alert.get_pokemon_names(),
                alert.get_phone_numbers())
            logging.info(log_msg)

            smtp.send_message(alert)

            # update users' last notified times so we don't
            # keep alerting them about the same pokemon
            for user in alert.get_users():
                logging.info("Updating users' last notified time: {}"
                             .format(user.get_json()))
                PnuUserDataStore.update(
                    user.get_phone_number(),
                    # only modify last_notif
                    { "last_notif": user.get_last_notif() }
                )

    def prompt_alerts(self):
        while True:
            raw_user = PnuPendingDataStore.pop(constants.ENROLL)
            logging.info("Got user to send msg to: {}".format(raw_user))
            if len(raw_user) > 0:
                smtp.send_message(User(raw_user))
