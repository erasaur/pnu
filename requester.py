#! /usr/bin/env python3.5

import email
import imaplib
import json
import re
import sys
from config import Config, PrivateConfig

class PnuRequest:

    android_regex = re.compile("maps\.google\.com/maps\?f=q&q=\((?P<lat>.*)?,(?P<lon>.*)?\)")
    ios_regex = re.compile("maps\.apple\.com/\?ll=(?P<lat>.*)?\\\,(?P<lon>.*)?&")

    def __init__(self):
        self.config = Config().load_config()
        self.private_config = PrivateConfig().load_config()

        self.mail = imaplib.IMAP4_SSL(self.config['gmail']['imap'])
        try:
            u, data = self.mail.login(self.private_config['gmail']['username'],
                        self.private_config['gmail']['password'])
        except imaplib.IMAP4.error:
            print("Login Failed")
            sys.exit(1)


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
        resp, data = self.mail.select(self.config['gmail']['mailbox'])
        self.check_resp(resp)
        return data

    def check_resp(self, resp):
        """ checks the response from the server for each request """
        if resp != 'OK':
            print("response is: ", resp)
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
            msgs    byte string containing all of the message details

        Returns:
            User object
        """
        for msg in msgs:
            # probably android location msg
            if msg['Subject']:
                # message body
                body = msg.get_payload(decode=True)
                lat, lon = self.parse_android_lat_lon(body)
                user = {
                    "phone_number": msg['From'],
                    "pokemon_wanted": ['INSERT_POKEMON_WANTED'],
                    "location": {
                        "lat": lat,
                        "lon": lon
                    }
                }
                yield user
            else:
                lat, lon = self.parse_iphone_lat_lon(msg)
                user = {
                    "phone_number": msg['From'],
                    "pokemon_wanted": ['INSERT_POKEMON_WANTED'],
                    "location": {
                        "lat": lat,
                        "lon": lon
                    }
                }
                yield user


    def get_attachment(self, msg):
        """ returns the text from the attachment of an iphone message """
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
#        print('Android (lat, lon): ', (result.group('lat'), result.group('lon'),))
        return (result.group('lat'), result.group('lon'),)

    def parse_iphone_lat_lon(self, msg):
        """ gets the latitude and longitude from an iphone message attachment

        Args:
            msg     most of the email including the attachment, subject,
                    and body

        Returns:
            a tuple containing the (lat, long) of the message
        """
        attach_text = self.get_attachment(msg)
        result = re.search(self.ios_regex, attach_text.decode('UTF-8'))
#        print('iPhone (lat, lon): ', (result.group('lat'), result.group('lon'),))
        return (result.group('lat'), result.group('lon'),)

    def run(self):
        """ yields new unread messages """
        self.get_inbox()
        msgs = self.get_unread_messages()
        return self.parse_msgs(msgs)


if __name__ == "__main__":
    req = PnuRequest()
    req.get_inbox()
    msgs = req.get_unread_messages()
    users = req.parse_msgs(msgs)
    for user in users:
        print(user)
