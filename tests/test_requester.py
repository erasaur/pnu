#!/usr/bin/env python3.5
import unittest
import re

from pnu.inbound.requester import PnuRequest


class LatLonRegexTests(unittest.TestCase):
    loc_regex = PnuRequest.location_regex
    pokemon_regex = PnuRequest.pokemon_regex
    split_regex = PnuRequest.split_regex
    stop_regex = PnuRequest.stop_regex
    pause_regex = PnuRequest.pause_regex
    resume_regex = PnuRequest.resume_regex
    req = PnuRequest()

    android_test_strings = [
        "202 South Division Street\n" +
        "Ann Arbor MI, 48104\n" +
        "USA\n" +
        "http://maps.google.com/maps?f=q&q=(42.280317,-83.744026)\n"
    ]

    generic_test_strings = [
        "Shared location https://maps.google.com/?t=m&q=38.79717," +
        "-77.30460+(Shared+location)&ll=38.79717,-77.30460&z=17",
    ]

    ios_test_strings = []
    with open('./test_files/Current Location.loc.vcf', 'r') as f:
        ios_test_strings.append(f.read())

    def test_android_lat_lon(self):
        for string in self.android_test_strings:
            result = re.search(self.loc_regex, string)
            self.assertTrue(result.group('lat'))
            self.assertTrue(result.group('lon'))

    def test_ios_lat_long(self):
        result = re.search(self.loc_regex, self.ios_test_strings[0])
        self.assertTrue(result.group('lat'))
        self.assertTrue(result.group('lon'))

    def test_generic_lat_lon(self):
        for string in self.generic_test_strings:
            result = re.search(self.loc_regex, string)
            self.assertTrue(result.group('lat'))
            self.assertTrue(result.group('lon'))

    def test_parse_for_location(self):
        msg = [self.android_test_strings[0], self.ios_test_strings[0],
               self.generic_test_strings[0]]
        for mess in msg:
            lat, lon = self.req.parse_for_location(mess.encode('UTF-8'))
            self.assertTrue(lat)
            self.assertTrue(lon)

    def test_pokemon_wanted_list_valid(self):
        pokemon_wanted = "Pokemon wanted: abra, alakazam, nidoran-f, " +\
                         "nidoran-m, pidgey, zebra"
        result = re.search(self.pokemon_regex, pokemon_wanted)
        result = re.split(self.split_regex, result.group(1))
        self.assertEqual(6, len(result))

    def test_pokemon_wanted_list_too_long(self):
        pokemon_wanted = "Pokemon wanted: abra, alakazam, nidoran-f, " +\
                         "nidoran-m, pidgey, zebra, pidgey, squirtle, " +\
                         "wartortle, rattata, alakazam, fearow"
        result = re.search(self.pokemon_regex, pokemon_wanted)
        result = re.split(self.split_regex, result.group(1))
        self.assertEqual(10, len(result))

    def test_pokemon_wanted_list_with_spaces(self):
        pokemon_wanted = "Pokemon wanted: abra  nidoran-f nidoran-m, " +\
                         "pidgey, pidgey wartortle, rattata alakazam, fearow"
        result = re.search(self.pokemon_regex, pokemon_wanted)
        result = re.split(self.split_regex, result.group(1))
        self.assertEqual(10, len(result))

    def test_pause_command(self):
        msg = ["pause", "Pause", "PAUSE", "pause ", " pAuSE "]
        for i, mess in enumerate(msg):
            result = self.req.find_pause_command(mess.encode('UTF-8'))
            self.assertTrue(result, i)

    def test_stop_command(self):
        msg = ["stop", "Stop", "STOP", "stop  ", " Stop  "]
        for i, mess in enumerate(msg):
            result = self.req.find_stop_command(mess.encode('UTF-8'))
            self.assertTrue(result, i)

    def test_resume_command(self):
        msg = ["resume", "Resume", "RESUME", "resume  ", " resume  "]
        for i, mess in enumerate(msg):
            result = self.req.find_resume_command(mess.encode('UTF-8'))
            self.assertTrue(result, i)

    def test_check_for_command_not_found(self):
        msgs = [msg for msg in self.android_test_strings]
        msgs += [msg for msg in self.ios_test_strings]
        msgs += [msg for msg in self.generic_test_strings]
        for mess in msgs:
            result = self.req.check_for_command(mess.encode('UTF-8'),
                                                {'From': 'tester'})
            self.assertFalse(result)

    def test_check_for_command(self):
        msgs = ["resume", "Resume", "RESUME", "resume  ", " resume  "]
        msgs += ["stop", "Stop", "STOP", "stop  ", " Stop  "]
        msgs += ["pause", "Pause", "PAUSE", "pause ", " pAuSE "]
        for mess in msgs:
            result = self.req.check_for_command(mess.encode('UTF-8'),
                                                {'From': 'tester'})
            self.assertTrue(result)

    def test_filter_pokemon_wanted_no_errors(self):
        pokemon_wanted = "Pokemon wanted: abra, alakazam, nidoran-f, " +\
                         "nidoran-m, pidgey, rattata"
        result, errors = self.req.parse_pokemon_wanted(
                pokemon_wanted.encode('utf-8'))
        self.assertTrue(result)
        self.assertEqual(6, len(result))
        self.assertFalse(errors)

        pokemon_wanted = "Pokemon wanted: abra, abra, alakazam, nidoran-f, " +\
                         "nidoran-m, pidgey, rattata"
        result, errors = self.req.parse_pokemon_wanted(
                pokemon_wanted.encode('utf-8'))
        self.assertTrue(result)
        self.assertEqual(6, len(result))
        self.assertFalse(errors)

    def test_filter_pokemon_wanted_with_errors(self):
        pokemon_wanted = "Pokemon wanted: abra, alakazam, nidoranf, " +\
                         "nidoran-m, pidgey, rattata"
        result, errors = self.req.parse_pokemon_wanted(
                pokemon_wanted.encode('utf-8'))
        self.assertTrue(result)
        self.assertEqual(5, len(result))
        self.assertTrue(errors)
        self.assertEqual(1, len(errors))

        pokemon_wanted = "Pokemon wanted: abra, abra, z, , alakazam, " +\
                         "nidoran-f, nidoranm, pidgey, rattata"
        result, errors = self.req.parse_pokemon_wanted(
                pokemon_wanted.encode('utf-8'))
        self.assertTrue(result)
        self.assertEqual(5, len(result))
        self.assertTrue(errors)
        self.assertEqual(3, len(errors))

if __name__ == "__main__":
    unittest.main()
