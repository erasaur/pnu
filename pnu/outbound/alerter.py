#! /usr/bin/env python3.5

from smtplib import SMTP
from pnu.config import pub_config, private_config
from pnu.outbound.response import Response
from pnu.models.user import User

import logging
logging = logging.getLogger(__name__)


class PnuAlertDispatcher:


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

    def send_message(self, user, link = None):
        """ sends a text message alert to the specified user
        Args:
            info (dictionary)
        """
        msg, phone_number = Response(user, link).build_message()
        logging.info("MESSAGE IS: " + msg)
        logging.info("Sending to: " + phone_number)
        self.smtp.sendmail(private_config['gmail']['username'],
                phone_number, msg)

smtp = PnuAlertDispatcher()

if __name__ == "__main__":
    import logging

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename='../etc/logs/alerter.out',
            level=logging.DEBUG)

    logging.info("Beginning " + __file__)
    link = "https://pnu.space"

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": ['abra', 'snorlax', 'ekans'],
            "status": "ACTIVE",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }

    smtp.send_message(User(info), link)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "PAUSE",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info), link)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "RESUME",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info), link)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": ['abra', 'snorlax'],
            "status": "STOP",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info), link)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "ENROLL",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info), link)
