#! /usr/bin/env python3.5

import email
import imaplib
import json
import re
import sys

from pnu.models.user import User
from pnu.config import pub_config, private_config

import logging
logger = logging.getLogger(__name__)

class PnuRequest:
    android_regex = re.compile("maps\.google\.com/maps\?f=q&q=\((?P<lat>.*)?,(?P<lon>.*)?\)")
    ios_regex = re.compile("maps\.apple\.com/\?ll=(?P<lat>.*)?\\\,(?P<lon>.*)?&")
    pokemon_regex = re.compile("pokemon\s*[a-z]*:\s*((([a-z]*-*[a-z]*),\s[a-z]*-*[a-z]*){0,4})", re.IGNORECASE)
    split_regex = re.compile(', |; | |,')

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
            logging.info("Response is: " + str(resp))
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

            lat, lon = self.parse_lat_lon(msg)

            # probably didn't find a location msg, instead is junk or
            # pokemon wanted msg
            if not (lat or lon):
                body = msg.get_payload(decode=True)

                try:
                    pokemon_wanted = self.parse_pokemon_wanted(body)

                    user = {
                            "phone_number": msg['From'],
                            "pokemon_wanted": pokemon_wanted
                    }

                    yield User(user)

                except AttributeError:
                    # both lat, lon, and pokemon_wanted are None
                    # probably junk message
                    logging.info("Latitude, Longitude, and pokemon_wanted, are "
                                 + "not found. Probably a junk message")
                    continue

            user = {
                "phone_number": msg['From'],
                "pokemon_wanted": pokemon_wanted,
                "location": {
                    "lat": lat,
                    "lon": lon
                }
            }
            logging.info("Creating user: " + str(user))

            yield User(user)

    def parse_lat_lon(self, msg):
        """ parses for the latitude and longitude from the email """
        # probably android msg either location or pokemon wanted
        lat = lon = None
        if msg['Subject']:
            logger.info("Possibly Android device")
            # message body
            body = msg.get_payload(decode=True)
            try:
                lat, lon = self.parse_android_lat_lon(body)
            except AttributeError:
                logger.info("Android location not found")
                pass

        else:
            logging.info("Possibly iOS device")
            try:
                lat, lon = self.parse_ios_lat_lon(msg)
            except AttributeError:
                logger.info("iOS location not found")
                pass

        return lat, lon

    def parse_pokemon_wanted(self, msg):
        """ parses input message and returns a list of pokemon wanted """
        results = re.search(self.pokemon_regex, msg.decode('UTF-8'))
        return re.split(self.split_regex, results.group(1))

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
                + str(result.group('lon')))
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
                + str(result.group('lon')))
        return (result.group('lat'), result.group('lon'),)

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
