#! /usr/bin/env python3.5

import email
import imaplib
import json
import re
import sys

from pnu.models.user import User
from pnu.config import pub_config, private_config
from pnu.etc import constants

import logging
logging = logging.getLogger(__name__)

class PnuRequest:
    android_regex = re.compile("maps\.google\.com/maps\?f=q&q=\((?P<lat>.*)?,(?P<lon>.*)?\)")
    ios_regex = re.compile("maps\.apple\.com/\?ll=(?P<lat>.*)?\\\,(?P<lon>.*)?&")
    pokemon_regex = re.compile("pokemon\s*[a-z]*:\s*((([a-z]*-*[a-z]*),\s[a-z]*-*[a-z]*){0,4})", re.IGNORECASE)
    split_regex = re.compile(', |; | |,')
    stop_regex = re.compile('stop', re.IGNORECASE)
    pause_regex = re.compile('pause', re.IGNORECASE)
    resume_regex = re.compile('resume', re.IGNORECASE)

    STOP = "STOP"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    ACTIVE = "ACTIVE"
    ENROLL = "ENROLL"

    def __init__(self):
        self.mail = imaplib.IMAP4_SSL(pub_config['gmail']['imap'])
        try:
            u, data = self.mail.login(private_config['gmail']['username'],
                        private_config['gmail']['password'])
        except imaplib.IMAP4.error as e:
            logging.error("Login to retrieve emails failed!")
            logging.error(e)
            raise ConnectionError("Login to retrieve emails failed!")


    def __exit__(self):
        """ closes the open mailbox and logs out of the email account """
        self.mail.close()
        self.mail.logout()

    def get_inbox(self):
        """ returns the main 'INBOX' of the email account

        Args:
            None

        Results:
            returns the INBOX data associated with this email account

        """
        resp, data = self.mail.select(pub_config['gmail']['mailbox'])
        self.check_resp(resp)
        return data

    def check_resp(self, resp):
        """ checks the response from the server for each request """
        if resp != 'OK':
            logging.info("Response is: {}".format(resp))
            raise ConnectionError("Response from IMAP was not 'OK'")

    def get_unread_messages(self):
        """ retrieve all unread messages from the inbox """
        resp, msgs = self.mail.search(None, '(UNSEEN)')
        self.check_resp(resp)
        for msg_num in msgs[0].split():
            resp, msg = self.mail.fetch(msg_num, '(RFC822)')
            self.check_resp(resp)
            # contains the subject, body, and a bunch of other data
            msg_info = email.message_from_bytes(msg[0][1])
            yield msg_info

    def parse_msgs(self, msgs):
        """ yields Users with lat/lon, and phone number filled in
        Args:
            msgs    (byte string)
                Contains all of the message details
        Returns:
            User object
        """
        for msg in msgs:
            lat = lon = body = None
            pokemon_wanted = None
            status = None
            user = {
                'phone_number': msg['From'],
                'pokemon_wanted': pokemon_wanted,
                'location': {
                    'lat': lat,
                    'lon': lon
                },
                'status': status
            }

            body = msg.get_payload(decode=True)

            # check for PAUSE, RESUME, STOP
            status = self.check_for_command(body, msg)
            if status:
                user['status'] = status
                yield User(user)

            lat, lon = self.parse_lat_lon(msg)
            user['location']['lat'] = lat
            user['location']['lon'] = lon
            if body:
                pokemon_wanted = self.parse_pokemon_wanted(body)

            user['pokemon_wanted'] = pokemon_wanted

            # probably didn't find a location msg, instead is junk or
            # pokemon wanted msg
            if not (lat or lon or pokemon_wanted):
                # JUNK MESSAGEEEE
                continue

            logging.info("Returning user: " + str(user))

            yield User(user)

    def parse_lat_lon(self, msg):
        """ parses for the latitude and longitude from the email """
        # probably android msg either location or pokemon wanted
        lat = lon = None
        if msg['Subject']:
            logging.info("Possibly Android device")
            # message body
            body = msg.get_payload(decode=True)
            try:
                lat, lon = self.parse_android_lat_lon(body)
            except AttributeError:
                logging.info("Android location not found")
                pass

        else:
            logging.info("Possibly iOS device")
            try:
                lat, lon = self.parse_ios_lat_lon(msg)
            except AttributeError:
                logging.info("iOS location not found")
                pass

        return lat, lon

    def parse_pokemon_wanted(self, msg):
        """ parses input message and returns a list of pokemon wanted """
        results = re.search(self.pokemon_regex, msg.decode('UTF-8'))
        try:
            pokemon_wanted = re.split(self.split_regex, results.group(1))
        except AttributeError:
            logging.info("No pokemon found in message!")
            return None

        validated_pokemon_wanted =  filter_pokemon_wanted(pokemon_wanted)
        return validated_pokemon_wanted


    def filter_pokemon_wanted(pokemon_wanted):
        """ returns a list of pokemon ids the user wants
        Args:
            pokemon_wanted (list of strings of pokemon names)
        Returns:
            pokemon_validated (list of ints of pokemon ids)
        """
        valid_pokemon = []
        for pokemon in pokemon_wanted:
            try:
                valid_pokemon.append(constants.POKEMON_NAME_TO_ID[pokemon])

            except KeyError:
                logging.log("User submitted fake pokemon: " + str(pokemon))
                continue

        return valid_pokemon

    def get_attachment(self, msg):
        """ returns the text from the attachment of an iOS message """
        if msg.get_content_maintype() == 'multipart':
            for part in msg.walk():
                # find the vcard attachment part
                if part.get_content_type() != 'text/x-vcard':
                    continue
                filename = part.get_filename()
                return part.get_payload(decode=True)

    def parse_android_lat_lon(self, body):
        """ gets the latitude and longitude from an android message

        Args:
            body    byte string containing the address and google maps link
                    to their latitude and longitude

        Returns:
            a tuple containing the (lat, long) of the message
        """

        result = re.search(self.android_regex, body.decode('UTF-8'))
        logging.info('Android (lat, lon): ' + str(result.group('lat'))
                + ', ' + str(result.group('lon')))
        return (result.group('lat'), result.group('lon'),)

    def parse_ios_lat_lon(self, msg):
        """ gets the latitude and longitude from an iOS message attachment

        Args:
            msg     most of the email including the attachment, subject,
                    and body

        Returns:
            a tuple containing the (lat, long) of the message
        """
        attach_text = self.get_attachment(msg)
        result = re.search(self.ios_regex, attach_text.decode('UTF-8'))
        logging.info('iOS (lat, lon): ' + str(result.group('lat'))
                + ', ' + str(result.group('lon')))
        return (result.group('lat'), result.group('lon'),)

    def check_for_command(self, body, msg):
        status = None
        if self.find_stop_command(body):
            logging.info("STOP command received for: " + str(msg['From']))
            status = self.STOP

        elif self.find_pause_command(body):
            logging.info("PAUSE command received for: " + str(msg['From']))
            status = self.PAUSE

        elif self.find_resume_command(body):
            logging.info("RESUME command received for: " + str(msg['From']))
            status = self.RESUME

        return status

    def find_stop_command(self, body):
        return self.find_command(body, self.stop_regex)

    def find_resume_command(self, body):
        return self.find_command(body, self.resume_regex)

    def find_pause_command(self, body):
        return self.find_command(body, self.pause_regex)

    def find_command(self, body, regex):
        try:
            results = re.search(regex, body.decode('UTF-8'))
            results.group(0)
            return True
        except AttributeError as e:
            return False

    def run(self):
        """ yields new unread messages """
        self.get_inbox()
        msgs = self.get_unread_messages()
        return self.parse_msgs(msgs)

if __name__ == "__main__":
    import logging

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename='../etc/logs/requester.out',
            level=logging.DEBUG)

    logging.info("Beginning " + __file__)

    req = PnuRequest()
    req.get_inbox()
    msgs = req.get_unread_messages()
    users = req.parse_msgs(msgs)

    for user in users:
        print(user)
