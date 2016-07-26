from pnu.outbound.alerter import smtp
import logging
logging = logging.getLogger(__name__)

class PnuAlertDispatcher ():
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
                "link": link,
                "status": 'ACTIVE'
            })
