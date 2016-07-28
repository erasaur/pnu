from pnu.core.runnable import PnuRunnable
from pnu.core.data_store import PnuPendingDataStore
from pnu.etc import constants
from pnu.outbound.alerter import smtp
from pnu.models.user import User

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
            log_msg = "Dispatching message for {} to {}".format(
                alert.get_pokemon_names(),
                alert.get_phone_numbers())
            logging.info(log_msg)

            smtp.send_message(alert)

            # update users' last notified times so we don't
            # keep alerting them about the same pokemon
            for user in alert.get_users():
                for poke in alert.get_pokemon():
                    user.set_last_notif_for_poke(poke)

                PnuUserDataStore.update(user.get_phone_number(), user)

    def prompt_alerts(self):
        while True:
            raw_user = PnuPendingDataStore.pop(constants.ENROLL)
            logging.info("Got pending user: {}".format(raw_user))
            smtp.send_message(User(raw_user))
