#! /usr/bin/env python3.5

import unittest

from pnu.outbound.alerter import PnuAlertDispatcher
from pnu.models import Alert
from pnu.models import User
from pnu.models import Pokemon
from pnu.etc import constants


class PnuAlerterTests(unittest.TestCase):

    smtp = PnuAlertDispatcher()

    link = "https://pnu.space"

    def test_alert(self):

        # test sending ALERTS
        poke_json = {
            "pokemonId": 16,
            "latitude": 42.27883786872156,
            "longitude": -83.74502208351473,
            "expiration_time": 123456789
        }
        user_json = {
                "phone_number": "test@gmail.com",
                "pokemon_wanted": [],
                "status": constants.PAUSE,
                "location": {
                    "lat": 12,
                    "lon": 10
                },
                "errors": []
        }

        poke_tuple = Pokemon(poke_json)
        user1 = User(user_json)
        user2 = User(user_json)
        phone_numbers = [user1, user2]
        alert = Alert((poke_tuple,), phone_numbers)
        self.smtp.send_message(alert)

    def test_stop_message(self):
        info = {
                "phone_number": "test@gmail.com",
                "pokemon_wanted": ['abra', 'snorlax', 'ekans'],
                "status": constants.STOP,
                "location": {
                        "lat": 12,
                        "lon": 10
                },
                "errors": []
        }
        self.smtp.send_message(User(info))

    def test_pause_message(self):
        info = {
                "phone_number": "test@gmail.com",
                "pokemon_wanted": [],
                "status": constants.PAUSE,
                "location": {
                        "lat": 12,
                        "lon": 10
                },
                "errors": []
        }
        self.smtp.send_message(User(info))

    def test_resume_message(self):
        info = {
                "phone_number": "test@gmail.com",
                "pokemon_wanted": [],
                "status": constants.RESUME,
                "location": {
                        "lat": 12,
                        "lon": 10
                },
                "errors": []
        }
        self.smtp.send_message(User(info))

    def test_enroll_message(self):
        info = {
                "phone_number": "test@gmail.com",
                "pokemon_wanted": [],
                "status": constants.ENROLL,
                "location": {
                        "lat": 12,
                        "lon": 10
                },
                "errors": []
        }
        self.smtp.send_message(User(info))


if __name__ == "__main__":
    unittest.main()
