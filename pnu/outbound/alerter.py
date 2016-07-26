#! /usr/bin/env python3.5

from smtplib import SMTP
from pnu.config import pub_config, private_config
from pnu.outbound.response import Response

import logging
logging = logging.getLogger(__name__)


class PnuAlert:


    def __init__(self):
        """ perform preliminary actions for sending email via SMTP """

        logging.info("Starting up Alert")
        self.smtp = SMTP(pub_config['smtp']['host'], pub_config['smtp']['port'])
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.login(private_config['gmail']['username'],
                private_config['gmail']['password'])

    def __exit__(self):
        self.smtp.quit()

    def send_message(self, info):
        """ sends a text message alert to the specified user
        Args:
            info (dictionary)
        """
        msg, phone_number = Response(info).build_message()
        logging.info("MESSAGE IS: " + msg)
        logging.info("Sending to: " + phone_number)
        self.smtp.sendmail(private_config['gmail']['username'],
                phone_number, msg)

smtp = PnuAlert()

if __name__ == "__main__":
    import logging

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename='../etc/logs/alerter.out',
            level=logging.DEBUG)

    logging.info("Beginning " + __file__)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": ['abra', 'snorlax', 'ekans'],
            "link": "https://pnu.space",
            "status": "ACTIVE"
    }

    smtp.send_message(info)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "link": "https://pnu.space",
            "status": "PAUSE"
    }
    smtp.send_message(info)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "link": "https://pnu.space",
            "status": "RESUME"
    }
    smtp.send_message(info)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": ['abra', 'snorlax'],
            "link": "https://pnu.space",
            "status": "STOP"
    }
    smtp.send_message(info)
