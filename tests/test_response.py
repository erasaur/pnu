#! /usr/bin/env python3.5
import unittest

from pnu.models import Alert
from pnu.models import User
from pnu.models import Pokemon
from pnu.outbound import BuildResponse
from pnu.etc import constants


class PnuResponseTest(unittest.TestCase):

    def setUp(self):
        self.to = "test@gmail.com"
        user_info = {
            "phone_number": self.to,
            "pokemon_wanted": [],
            "status": "",
            "location": {
                "lat": 12,
                "lon": 10
            },
            "errors": []
        }

        self.user_info = user_info

    def test_make_enroll_msg(self):
        self.user_info['status'] = constants.ENROLL
        user_enroll = User(self.user_info)
        msg, to = BuildResponse(user_enroll).build_message()
        self.assertIn("RESUME", msg)
        self.assertIn("STOP", msg)
        self.assertIn("PAUSE", msg)
        self.assertIn("To activate", msg)
        self.assertEqual(to, self.to)

    def test_make_pause_msg(self):
        self.user_info['status'] = constants.PAUSE
        user_pause = User(self.user_info)
        msg, to = BuildResponse(user_pause).build_message()
        self.assertIn("RESUME", msg)
        self.assertEqual(to, self.to)

    def test_make_pause_msg_with_no_loc_or_pokemon(self):
        self.user_info['status'] = constants.PAUSE
        self.user_info['location'] = {}
        self.user_info['pokemon_wanted'] = []
        user_pause = User(self.user_info)
        msg, to = BuildResponse(user_pause).build_message()
        self.assertIn("RESUME", msg)
        self.assertEqual(to, self.to)

    def test_make_stop_msg(self):
        self.user_info['status'] = constants.STOP
        user_stop = User(self.user_info)
        msg, to = BuildResponse(user_stop).build_message()
        self.assertIn("Sorry to", msg)

    def test_make_resume_msg_no_pokemon(self):
        self.user_info['status'] = constants.RESUME
        user_resume = User(self.user_info)
        msg, to = BuildResponse(user_resume).build_message()
        # pokemon_wanted is empty right now
        self.assertIn("There are no pokemon", msg)

    def test_make_resume_msg_no_location(self):
        self.user_info['location'] = {}
        self.user_info['status'] = constants.RESUME
        user_resume = User(self.user_info)
        # location is missing, as well as pokemon wanted
        msg, to = BuildResponse(user_resume).build_message()
        self.assertIn("It does not look like we have", msg)

    def test_make_resume_msg_valid(self):
        self.user_info['status'] = constants.RESUME
        self.user_info['pokemon_wanted'] = ['pidgey', 'rattata', 'ekans']
        user_resume = User(self.user_info)
        # location is missing, as well as pokemon wanted
        msg, to = BuildResponse(user_resume).build_message()
        self.assertIn("Alerts will now be sent", msg)

    def test_make_active_msg_user_valid(self):
        self.user_info['status'] = constants.ACTIVE
        self.user_info['pokemon_wanted'] = ['pidgey', 'rattata', 'ekans']
        user_active = User(self.user_info)
        msg, to = BuildResponse(user_active).build_message()
        self.assertIn("There\'s a wild", msg)
        self.assertIn("Pidgey", msg)
        self.assertIn("Rattata", msg)
        self.assertIn("Ekans", msg)

    def test_make_active_msg_alert_valid(self):
        self.user_info['status'] = constants.ACTIVE
        self.user_info['pokemon_wanted'] = ['pidgey']
        poke = {
            "pokemonId": 16,
            "latitude": 42.01,
            "longitude": -83.69,
            "expiration_time": 14789029
        }
        poke = Pokemon(poke)
        user_active = Alert([poke], [User(self.user_info)])
        msg, to = BuildResponse(user_active).build_message()
        self.assertIn("There\'s a wild", msg)
        self.assertIn("Pidgey", msg)
        self.assertIn("goo.gl", msg)

    # continue with invalid active messages (no poke, no loc)
    # then test all above cases with errors

if __name__ == "__main__":
    unittest.main()
