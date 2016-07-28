#! /usr/bin/env python3.5

from smtplib import SMTP
from pnu.config import pub_config, private_config
from pnu.outbound.response import BuildResponse
from pnu.models.user import User
from pnu.models.alert import Alert
from pnu.models.pokemon import Pokemon

import logging
logging = logging.getLogger(__name__)


class PnuAlertDispatcher:


    def __init__(self):
        """ perform preliminary actions for sending email via SMTP """

        logging.info("Starting up Alert")
        try:
            self.smtp = SMTP(pub_config['smtp']['host'], pub_config['smtp']['port'])
            self.smtp.ehlo()
            self.smtp.starttls()
            self.smtp.login(private_config['gmail']['username'],
                    private_config['gmail']['password'])
        except SMTPHeloError:
            logging.error("Error the email server didn't properly reply "
                    + "to the ehlo/helo request")

        except SMTPAuthenticationError:
            logging.error("The username or password was not accepted by the "
                    + "email server")

        except SMTPNotSupportedError:
            logging.error("The AUTH command is not supported by the email "
                    + "server")

        except SMTPException:
            logging.error("Could not connect with the email server!!")

    def __exit__(self):
        self.smtp.quit()

    def send_message(self, user):
        """ sends a text message alert to the specified user
        Args:
            info (dictionary)
        """
        msg, phone_number = BuildResponse(user).build_message()
        logging.info("MESSAGE IS: {}\nSending to: {}".format(msg, phone_number))
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

    ### test sending ALERTS
    info = {
        "pokemonId": 16,
        "latitude": 12,
        "longitude": 10,
        "expiration_time": 123456789
    }
    poke_tuple = Pokemon(info)
    phone_numbers = ["2694913303@vtext.com","2694913303@vtext.com"]
    alert = Alert((poke_tuple,), phone_numbers)
    smtp.send_message(alert)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": ['abra', 'snorlax', 'ekans'],
            "status": "STOP",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }

    smtp.send_message(User(info))

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "PAUSE",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info))

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "RESUME",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info))

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": ['abra', 'snorlax'],
            "status": "STOP",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info))

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "ENROLL",
            "location":{
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info))
