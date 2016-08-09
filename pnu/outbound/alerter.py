#! /usr/bin/env python3.5

import time
from smtplib import (SMTP, SMTPHeloError, SMTPAuthenticationError,
                     SMTPNotSupportedError, SMTPException, SMTPSenderRefused)

from pnu.config import pub_config, private_config
from pnu.etc import constants
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
        auth_attempts = 0

        while auth_attempts < 5:
            auth_attempts += 1
            try:
                self.smtp = SMTP(pub_config['smtp']['host'],
                                 pub_config['smtp']['port'])
                self.smtp.starttls()
                self.smtp.ehlo()
                self.smtp.login(private_config['gmail']['username'],
                                private_config['gmail']['password'])
                break
            except SMTPHeloError as e:
                logging.error("Error the email server didn't properly reply " +
                              "to the ehlo/helo request:\n{}".format(e))

            except SMTPAuthenticationError as e:
                logging.error("The username or password was not accepted by " +
                              "the email server:\n{}".format(e))

            except SMTPNotSupportedError as e:
                logging.error("The AUTH command is not supported by the " +
                              "email server:\n{}".format(e))

            except SMTPException as e:
                logging.error("Could not connect with the email " +
                              "server:\n{}".format(e))

            except Exception as e:
                logging.error("An error occurred while initializing " +
                              "SMTP:\n{}".format(e))

            time.sleep(constants.SMTP_RECONNECT_SLEEP_TIME)

        if auth_attempts >= 5:
            raise SMTPException("Failed connecting with the SMTP server. :(")

    def __exit__(self):
        self.smtp.quit()

    def send_message(self, user):
        """ sends a text message alert to the specified user
        Args:
            info (dictionary)
        """
        msg, phone_number = BuildResponse(user).build_message()
        logging.info("MESSAGE IS: {}\nSending to: {}".format(
                     msg, phone_number))

        send_attempts = 0
        while send_attempts < 10:
            try:
                send_attempts += 1
                self.smtp.sendmail(private_config['gmail']['username'],
                                   phone_number, msg)
                send_attempts = 10
            except SMTPSenderRefused as e:
                time.sleep(constants.SMTP_RECONNECT_SLEEP_TIME)
                logging.error("Sender refused error. Phone #: {}"
                              .format(phone_number))
                logging.error("Sender refused address is: {}".format(sender))
                logging.error("Error is: {}".format(e))
                logging.error("Message: {}".format(msg))

            except:
                time.sleep(constants.SMTP_RECONNECT_SLEEP_TIME)
                logging.error("An error occurred while sending a message!!")
                logging.error("Phone number: {}\nMessage: {}"
                              .format(phone_number, msg))
                logging.error("Error is: {}".format(e))


smtp = PnuAlertDispatcher()

if __name__ == "__main__":
    import logging

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename='../etc/logs/alerter.out',
                        level=logging.DEBUG)

    logging.info("Beginning " + __file__)
    link = "https://pnu.space"

    # test sending ALERTS
    poke_json = {
        "pokemonId": 16,
        "latitude": 42.27883786872156,
        "longitude": -83.74502208351473,
        "expiration_time": 123456789
    }
    user_json = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "PAUSE",
            "location": {
                    "lat": 12,
                    "lon": 10
            }
    }

    poke_tuple = Pokemon(poke_json)
    user1 = User(user_json)
    user2 = User(user_json)
    phone_numbers = [user1, user2]
    alert = Alert((poke_tuple,), phone_numbers)
    smtp.send_message(alert)

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": ['abra', 'snorlax', 'ekans'],
            "status": "STOP",
            "location": {
                    "lat": 12,
                    "lon": 10
            }
    }

    smtp.send_message(User(info))

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "PAUSE",
            "location": {
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info))

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "RESUME",
            "location": {
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info))

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": ['abra', 'snorlax'],
            "status": "STOP",
            "location": {
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info))

    info = {
            "phone_number": "2694913303@vtext.com",
            "pokemon_wanted": [],
            "status": "ENROLL",
            "location": {
                    "lat": 12,
                    "lon": 10
            }
    }
    smtp.send_message(User(info))
