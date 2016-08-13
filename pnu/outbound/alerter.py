#! /usr/bin/env python3.5

import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from os.path import basename
from smtplib import (SMTP, SMTPHeloError, SMTPAuthenticationError,
                     SMTPNotSupportedError, SMTPException, SMTPSenderRefused)

from pnu.config import pub_config, private_config
from pnu.etc import constants
from pnu.outbound.response import BuildResponse
from pnu.models import User
from pnu.models import Alert
from pnu.models import Pokemon


import logging
logging = logging.getLogger(__name__)


class PnuAlertDispatcher:

    def __init__(self):
        """ perform preliminary actions for sending email via SMTP """

        logging.info("Starting up Alert")
        self.reconnect()

    def __exit__(self):
        self.smtp.quit()

    def reconnect(self):
        auth_attempts = 0

        while auth_attempts <= constants.MAX_RECONNECT_RETRIES:
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

        if auth_attempts > constants.MAX_RECONNECT_RETRIES:
            logging.critical("Could not connect to SMTP handler")
            self.send_error("Could not connect to SMTP handler")

    def send_error(self, message):
        """ create an email with the most recent log file attached and send it

        Args:
            message: string of text to be sent in the body of the message
        """
        try:
            recipients = [email for email in private_config['notify']['email']]
        except KeyError:
            logging.critical("No one to be notified for fatal problems :( " +
                             "Slowly dying instead...")
            return

        # get the currently logged to file
        logFilename = logging.root.handlers[0].baseFilename

        msg = MIMEMultipart()

        msg['To'] = COMMASPACE.join(recipients)
        msg['From'] = private_config['gmail']['username']
        msg['Subject'] = constants.ERROR_SUBJECT

        msg.attach(MIMEText(message))

        with open(logFilename, 'rb') as attach:
            part = MIMEApplication(
                    attach.read(),
                    Name=basename(logFilename)
            )
            part['Content-Disposition'] = ('attachment; filename="{}"'
                                           .format(basename(logFilename)))
            msg.attach(part)

        try:
            self.smtp.sendmail(private_config['gmail']['username'],
                               private_config['notify']['email'],
                               msg.as_string())
        except:
            logging.critical("COULD NOT SEND ERROR EMAIL :(" +
                             "THINGS WILL NOW PROCEED TO BURN DOWN")

    def send_message(self, user):
        """ sends a text message alert to the specified user
        Args:
            info (dictionary)
        """
        msg, phone_number = BuildResponse(user).build_message()
        logging.info("\nMESSAGE IS: {}\nSending to: {}".format(
                     msg, phone_number))

        send_attempts = 0
        while send_attempts < 10:
            send_attempts += 1
            try:
                self.smtp.sendmail(private_config['gmail']['username'],
                                   phone_number, msg)
                logging.info("Successfully sent message after {} tries"
                             .format(send_attempts))
                send_attempts = 200
            except SMTPSenderRefused as e:
                time.sleep(constants.SMTP_RECONNECT_SLEEP_TIME)
                logging.error("Sender refused error. Phone #: {}"
                              .format(phone_number))
                logging.error("Error is: {}".format(e))
                logging.error("Message: {}".format(msg))
                # try reconnecting anyway :shrug:
                self.reconnect()

            except Exception as e:
                time.sleep(constants.SMTP_RECONNECT_SLEEP_TIME)
                logging.error("An error occurred while sending a message!!")
                logging.error("Phone number: {}".format(phone_number))
                logging.error("Message: {}".format(msg))
                logging.error("Error is: {}".format(e))
                self.reconnect()

        if send_attempts != 200:
            # OH SHOOT, SOMETHING'S ON FIRE
            # although this is funny since we're trying to send a message
            # about not being able to send a message xD
            message = ("Attempted to send a message more than 10 times, a " +
                       "connection issue or refusal to send is likely the " +
                       "case.\nAttached are the most recent logs to help.")
            self.send_error(message)


smtp = PnuAlertDispatcher()

if __name__ == "__main__":
    import logging

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename='../etc/logs/alerter.out',
                        level=logging.DEBUG)

    logging.info("Beginning " + __file__)
