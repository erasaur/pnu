from email.mime.text import MIMEText
from pnu.config import private_config

import logging
logging = logging.getLogger(__name__)


class Response:

    SUBJECT = "Pokemon Alert!"
    SMS_CARRIERS = ["message.alltel.com", "txt.att.net", "myboostmobile.com",
            "messaging.sprintpcs.com", "tmomail.net", "email.uscc.net",
            "vtext.com", "vmobl.com"]
    MMS_CARRIERS = ["mms.alltelwireless.com", "mms.att.net", "myboostmobile.com",
            "pm.sprint.com", "tmomail.net", "mms.uscc.net", "vzwpix.com",
            "vmpix.com"]

    def __init__(self, info):
        self.status = info['status']
        self.to = info['phone_number']
        self.pokemon_wanted = info['pokemon_wanted']
        self.link = info['link']

    def _make_welcome_msg(self):
        logging.info("Sending WELCOME message")
        msg = ("PAUSE - temporarily suspend alerts\nRESUME "
                + "- resume previous alerts\nSTOP - quit receiving alerts"
                + "\nTo activate your user, respond in the form of 'Pokemon wanted: "
                + "poke1, poke2, poke3' up to five pokemon")
        self.to = self._check_len_of_msg(msg)
        return msg

    def _make_stop_msg(self):
        logging.info("Sending STOP message")
        return "Sorry to see you go! Best of luck catchin' 'em all!"

    def _make_pause_msg(self):
        logging.info("Sending PAUSE message")
        return "Respond with RESUME to begin alerts"

    def _make_active_msg(self):
        """ returns the text message to be sent to the receiver
        Args:
            info    (dictionary)
                with keys: link (string), pokemon_wanted (list),
                and phone_number (string)
        Returns:
            msg     MIMEText formatted message
        """
        logging.info("Sending ACTIVE message")
        self.pokemon_wanted = self.poke_list_to_str()
        a_an = self.format_plural_a_an()
        msg = MIMEText("There's {a_an} {pokemon} near you! Go catch 'em!\n{link}\n"
                .format(a_an=a_an, pokemon=self.pokemon_wanted,
                        link=self.link))

        # if the message to send is over 160 characters, send it via the mms
        # gateway instead of sms. The minus 2 is for parenthesis that get added
        # to the subject part of the message being sent.
        self.to = self._check_len_of_msg(msg.get_payload())

        if isinstance(self.to, list):
            msg['To'] = ', '.join(self.to)
        else:
            msg['To'] = self.to

        msg['From'] = private_config['gmail']['username']
        msg['Subject'] = self.SUBJECT

        return msg.as_string()

    def _check_len_of_msg(self, msg):
        """ checks if the message length is longer than 159 chars """
        if (len(msg) > (159)):
            logging.info("Message too long: " + str(len(msg))
                    + " Sending MMS.")
            return self._sms_to_mms()

        return self.to

    def _sms_to_mms(self):
        """ converts the sms carrier gateway to mms carrier gateway """
        num, ext = self.to.split('@')

        for i, carrier in enumerate(self.SMS_CARRIERS):
            if ext == carrier:
                ext = self.MMS_CARRIERS[i]

        return num + "@" + ext

    def format_plural_a_an(self):
        """ returns either a or an depending on the 1st letter """
        if self.pokemon_wanted[0][0].lower() in ['a', 'e', 'i', 'o', 'u']:
            return 'an'

        return 'a'

    def poke_list_to_str(self):
        """ creates a string from the list of pokemon wanted 
        Args:
            pokemon_wanted (list)
        Returns:
            string A string of pokemon such as "poke1, poke2, and poke3"
        """
        str_of_poke = self.pokemon_wanted[0]
        logging.info("List of pokemon_wanted is: " + str(self.pokemon_wanted))

        if len(self.pokemon_wanted) > 1:
            str_of_poke = (', '.join(self.pokemon_wanted[:-1]) + ", and "
                    + self.pokemon_wanted[-1])
            logging.info("List of pokemon from string is: " + str(str_of_poke))

        return str_of_poke

    def build_message(self):
        """ returns the text message to be sent to the receiver
        Args:
            None
        Returns:
            One of four messages. Either the STOP message, PAUSE message,
            RESUME message, or ACTIVE
        """
        logging.info("Deciding which message to send.")

        if self.status == 'RESUME':
            return self._make_welcome_msg(), self.to

        elif self.status == 'PAUSE':
            return self._make_pause_msg(), self.to

        elif self.status == 'STOP':
            return self._make_stop_msg(), self.to

        elif self.pokemon_wanted and self.status == 'ACTIVE':
            return self._make_active_msg(), self.to

        logging.error("Type of message is undetermined. Here's some data to help")
        logging.error("Pokemon wanted: " + str(self.pokemon_wanted))
        logging.error("Status of user: " + str(self.status))
        raise AttributeError("Type of message to be sent could not be determined")
