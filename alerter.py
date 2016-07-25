#! /usr/bin/env python3.5

from smtplib import SMTP
from config import pub_config, private_config
from email.mime.text import MIMEText

import logging
logger = logging.getLogger(__name__)


class Alert:

    SUBJECT = "Pokemon Alert!"
    SMS_CARRIERS = ["message.alltel.com", "txt.att.net", "myboostmobile.com",
                    "messaging.sprintpcs.com", "tmomail.net", "email.uscc.net",
                    "vtext.com", "vmobl.com"]
    MMS_CARRIERS = ["mms.alltelwireless.com", "mms.att.net", "myboostmobile.com",
                    "pm.sprint.com", "tmomail.net", "mms.uscc.net", "vzwpix.com",
                    "vmpix.com"]

    def __init__(self):
        """ perform preliminary actions for sending email via SMTP """

        logging.info("Starting up Alert")
        self.smtp = SMTP(pub_config['smtp']['host'], pub_config['smtp']['port'])
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.login(private_config['gmail']['username'],
                private_config['gmail']['password'])

    def __exit__(self):
        self.smtp.quit()

    def build_message(self, info):
        """ returns the text message to be sent to the receiver
        Args:
            info    (dictionary)
                with keys: link (string), pokemon_wanted (list),
                and phone_number (string)

        Returns:
            msg     MIMEText formatted message
        """
        pokemon_wanted = self.poke_list_to_str(info['pokemon_wanted'])
        a_an = self.format_plural_a_an(info['pokemon_wanted'])

        msg = MIMEText("There's {a_an} {pokemon} near you! Go catch 'em!\n{link}\n"
                .format(a_an=a_an, pokemon=pokemon_wanted, link=info['link']))

        # if the message to send is over 160 characters, send it via the mms
        # gateway instead of sms. The minus 2 is for parenthesis that get added
        # to the subject part of the message being sent.
        if (len(msg.get_payload()) > (159 - 2)):
            logging.info("Message too long " + str(len(msg.get_payload()))
                    + " sending MMS.")
            info['phone_number'] = self.sms_to_mms(info['phone_number'])

        msg['To'] = info['phone_number']
        msg['From'] = private_config['gmail']['username']
        msg['Subject'] = self.SUBJECT

        return msg.as_string()

    def format_plural_a_an(self, pokemon_wanted):
        """ returns either a or an depending on the 1st letter """
        if pokemon_wanted[0][0].lower() in ['a', 'e', 'i', 'o', 'u']:
            return 'an'

        return 'a'

    def poke_list_to_str(self, pokemon_wanted):
        """ creates a string from the list of pokemon wanted 
        Args:
            pokemon_wanted (list)
        Returns:
            string A string of pokemon such as "poke1, poke2, and poke3"
        """
        str_of_poke = pokemon_wanted[0]
        logging.info("List of pokemon_wanted is: " + str(pokemon_wanted))

        if len(pokemon_wanted) > 1:
            str_of_poke = ', '.join(pokemon_wanted[:-1]) + ", and " + pokemon_wanted[-1]
            logging.info("List of pokemon from string is: " + str(str_of_poke))

        return str_of_poke

    def sms_to_mms(self, phone_number):
        """ converts the sms carrier gateway to mms carrier gateway """
        num, ext = phone_number.split('@')

        for i, carrier in enumerate(self.SMS_CARRIERS):
            if ext == carrier:
                ext = self.MMS_CARRIERS[i]

        return num + "@" + ext

    def send_message(self, info):
        """ sends a text message alert to the specified user
        Args:
            info (dictionary)
        """

        msg = self.build_message(info)
        logging.info("Sending message: " + msg)
        self.smtp.sendmail(private_config['gmail']['username'],
                [info['phone_number']], msg)

smtp = Alert()

if __name__ == "__main__":
    import logging.config
    logging.config.fileConfig(pub_config['logging']['location'],
            disable_existing_loggers=False)
    logging.info("Beginning Alerter")

    info = {
        "phone_number": "2694913303@vtext.com",
        "pokemon_wanted": ['abra', 'snorlax', 'ekans'],
        "link": "https://exmaple.com"
    }
    smtp.send_message(info)

