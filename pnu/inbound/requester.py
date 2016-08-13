#! /usr/bin/env python3.5

import email
import imaplib
import json
import re
import sys
import time

from pnu.models import User
from pnu.config import pub_config, private_config
from pnu.etc import constants

import logging
logging = logging.getLogger(__name__)


class PnuRequest:
    location_regex = re.compile(r"""(?P<lat>[\d\.-]+) # matches 23.3 or -23.13
                                \\*, # backslashes sometimes included in msgs
                                (?P<lon>[\d\.-]+)""",
                                re.IGNORECASE | re.VERBOSE)
    pokemon_regex = re.compile("""pokemon\s*[a-z]*:?\s* # match pokemon wanted:
                               (([a-z-]* # match any char or dash
                               [,| ]* # match space or comma separation
                               [a-z-]*) # match same as above
                               {0,9}) # match up to 10 times""",
                               re.IGNORECASE | re.VERBOSE)

    split_regex = re.compile(', |; | |,')
    stop_regex = re.compile('stop', re.IGNORECASE)
    pause_regex = re.compile('pause', re.IGNORECASE)
    resume_regex = re.compile('resume', re.IGNORECASE)

    def __init__(self):
        self.reconnect()

    def __exit__(self):
        """ closes the open mailbox and logs out of the email account """
        self.mail.close()
        self.mail.logout()

    def reconnect(self):
        auth_attempts = 0

        while auth_attempts <= constants.MAX_RECONNECT_RETRIES:
            auth_attempts += 1

            try:
                self.mail = imaplib.IMAP4_SSL(pub_config['gmail']['imap'])
                u, data = self.mail.login(private_config['gmail']['username'],
                                          private_config['gmail']['password'])
                return
            except imaplib.IMAP4.error as e:
                logging.error("Login to retrieve emails failed!")
                logging.error(e)

            except Exception as e:
                logging.error("Error from IMAP! Trying to reconnect...")
                logging.error(e)

            time.sleep(constants.SMTP_RECONNECT_SLEEP_TIME)

        if auth_attempts > constants.MAX_RECONNECT_RETRIES:
            from pnu.outbound.alerter import smtp
            logging.critical("Could not connect to IMAP handler")
            smtp.send_error("Could not connect to IMAP handler")

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
            logging.info("Parsing message from: {}".format(msg['From']))
            lat = lon = body = None
            pokemon_wanted = None
            status = None
            user = {
                'phone_number': self.get_from_address(msg['From']),
                'pokemon_wanted': pokemon_wanted,
                'location': None,
                'status': status,
                'error_data': [],
            }

            # need to check if multipart message, walk or don't walk
            # based on that

            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    body = part.get_payload(decode=True)

            if not body:
                body = msg.get_payload(decode=True)

            # check for PAUSE, RESUME, STOP
            status = self.check_for_command(body, msg)
            if status:
                user['status'] = status
                yield User(user)

            lat, lon = self.parse_lat_lon(msg)
            if (lat or lon):
                user['location'] = {
                    "lat": lat,
                    "lon": lon
                }

            errors = []
            if body:
                pokemon_wanted, errors = self.parse_pokemon_wanted(body)

            user['pokemon_wanted'] = pokemon_wanted
            user['error_data'] = errors

            # probably didn't find a location msg, instead is junk or
            # pokemon wanted msg
            if not (lat or lon or pokemon_wanted or errors):
                # JUNK MESSAGEEEE
                logging.info("Didn't find lat/lon or any pokemon")
                continue

            logging.info("Parsed message to find: {}".format(user))

            yield User(user)

    def parse_lat_lon(self, msg):
        """ parses for the latitude and longitude from the email """
        lat = lon = None
        # get the payload if it is an android since the message body contains
        # the location and it's not in an attachment
        body = msg.get_payload(decode=True)
        lat, lon = self.parse_android_lat_lon(body)

        # check for an attachment that may have come from an ios device
        if not (lat and lon):
            lat, lon = self.parse_ios_lat_lon(msg)

        return lat, lon

    def parse_pokemon_wanted(self, msg):
        """ parses input message and returns a list of pokemon wanted """
        results = re.search(self.pokemon_regex, msg.decode('UTF-8'))
        try:
            logging.info("Looking for pokemon wanted in body of message")
            pokemon_wanted = re.split(self.split_regex, results.group(1))
        except AttributeError:
            logging.info("No pokemon found in message!")
            return None, None

        validated_pokemon_wanted, errors = self.filter_pokemon_wanted(
                pokemon_wanted)
        return validated_pokemon_wanted, errors

    def filter_pokemon_wanted(self, pokemon_wanted):
        """ returns a list of pokemon ids the user wants
        Args:
            pokemon_wanted (list of strings of pokemon names)
        Returns:
            pokemon_validated (list of ints of pokemon ids)
        """
        logging.info("Filtering pokemon...")
        valid_pokemon = set()
        errors = []
        for pokemon in pokemon_wanted:
            try:
                valid_pokemon.add(
                        constants.POKEMON_NAME_TO_ID[pokemon.strip().lower()])

            except KeyError:
                logging.info("User submitted fake pokemon: {}".format(pokemon))
                errors.append(pokemon)
                continue

        return list(valid_pokemon), errors

    def get_attachment(self, msg):
        """ returns the text from the attachment of an iOS message """
        if msg.get_content_maintype() == 'multipart':
            for part in msg.walk():
                # find the vcard attachment part
                if part.get_content_type() != 'text/x-vcard':
                    continue
                filename = part.get_filename()
                if filename == "Current Location.loc.vcf":
                    return part.get_payload(decode=True)

    def get_from_address(self, from_addr):
        logging.info("parsing from_addr: {}".format(from_addr))
        from_addr_email = re.search('<(.*?)>', from_addr)

        if not from_addr_email:
            return from_addr

        try:
            return from_addr_email.group(1)
        except AttributeError:
            logging.error("Unsure what platform the user messaged with")
            return None

    def parse_android_lat_lon(self, body):
        """ gets the latitude and longitude from an android message
        Args:
            body    byte string containing the address and google maps link
                    to their latitude and longitude
        Returns:
            a tuple containing the (lat, long) of the message
        """

        lat, lon = self.parse_for_location(body)
        logging.info('Android (lat, lon): {}, {}'.format(lat, lon))
        return (lat, lon,)

    def parse_ios_lat_lon(self, msg):
        """ gets the latitude and longitude from an iOS message attachment
        Args:
            msg     most of the email including the attachment, subject,
                    and body
        Returns:
            a tuple containing the (lat, long) of the message
        """
        attach_text = self.get_attachment(msg)
        lat, lon = self.parse_for_location(attach_text)
        logging.info('iOS (lat, lon): {}, {}'.format(lat, lon))
        return (lat, lon,)

    def parse_for_location(self, body):
        try:
            # if body is None, then it will also throw an AttributeError
            result = re.search(self.location_regex, body.decode('UTF-8'))
            lat = result.group('lat')
            lon = result.group('lon')

        except AttributeError:
            return None, None

        return lat, lon

    def check_for_command(self, body, msg):
        status = None
        logging.info("Checking body: {} for status commands".format(body))
        if self.find_stop_command(body):
            logging.info("STOP command received for: {}".format(msg['From']))
            status = constants.STOP

        elif self.find_pause_command(body):
            logging.info("PAUSE command received for: {}".format(msg['From']))
            status = constants.PAUSE

        elif self.find_resume_command(body):
            logging.info("RESUME command received for: {}".format(msg['From']))
            status = constants.RESUME

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
        get_inbox_attempts = 0
        while get_inbox_attempts <= constants.MAX_RECONNECT_RETRIES:
            get_inbox_attempts += 1
            try:
                self.get_inbox()
                msgs = self.get_unread_messages()
                users_from_msgs = self.parse_msgs(msgs)
                logging.info("Successfully connected to IMAP inbox and " +
                             "parsed messages after {} tries."
                             .format(get_inbox_attempts))
                return users_from_msgs

            except Exception as e:
                logging.error("Error while trying to get inbox messages")
                logging.error(e)
                self.reconnect()

        # should only get here in the case of too many reconnects/failures
        message = ("Attempted to retrieve the inbox messages more than 10 " +
                   "times and a successful connection could not be made. " +
                   "Attached are the most recent logs to help.")
        self.send_error(message)

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
