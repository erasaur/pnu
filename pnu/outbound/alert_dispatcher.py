from pnu.outbound.alerter import smtp
import logging
logging = logging.getLogger(__name__)

class PnuAlertDispatcher ():
    def dispatch (self, alerts):
        smtp.send_message(alerts)
