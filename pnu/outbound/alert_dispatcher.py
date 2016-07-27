from pnu.core.runnable import PnuRunnable
from pnu.outbound.alerter import smtp
from pnu.core.data_store import PnuPendingDataStore
from pnu.etc import constants

import logging
logging = logging.getLogger(__name__)

class PnuAlertDispatcher (PnuRunnable):
    def run (self):
        self.run_once(self.prompt_alerts)

    def dispatch (self, alerts):
        # pokemon object tuples will be returned
        # followed by a list of users who need to be notified
        # for the said pokemon
        for alert in alerts:
            logging.info("Dispatching message for "
                    + str(alert.get_pokemon_names()) + " to "
                    + str(alert.get_phone_numbers()))
            smtp.send_message({
                "phone_number": alert.get_phone_numbers(),
                "pokemon_wanted": alert.get_pokemon_names(),
                "link": alert.get_short_link(),
                "status": 'ACTIVE'
            })

    def prompt_alerts(self):
        while True:
            raw_user = PnuPendingDataStore.pop(constants.ENROLL)
            logging.info("Got pending user:", raw_user)
            smtp.send_message(json.loads(raw_user))
