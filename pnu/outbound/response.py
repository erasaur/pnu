from email.mime.text import MIMEText
from pnu.config import private_config
from pnu.etc import constants
from pnu.models.alert import Alert

import logging
logging = logging.getLogger(__name__)


class BuildResponse:

    SUBJECT = "Pokemon Alert!"
    SMS_CARRIERS = ["message.alltel.com", "txt.att.net", "myboostmobile.com",
                    "messaging.sprintpcs.com", "tmomail.net",
                    "email.uscc.net", "vtext.com", "vmobl.com"]
    MMS_CARRIERS = ["mms.alltelwireless.com", "mms.att.net",
                    "myboostmobile.com", "pm.sprint.com", "tmomail.net",
                    "mms.uscc.net", "vzwpix.com", "vmpix.com"]

    def __init__(self, user):
        self.link = None
        if isinstance(user, Alert):
            alert = user
            self.status = constants.ACTIVE
            # user in this case is a list of users' phone numbers
            self.to = alert.get_phone_numbers()
            self.pokemon_wanted = alert.get_pokemon_names()
            self.link = alert.get_short_link()
            # spoofed since we have a list of users we presume to be
            # already valid
            self.location = True
        else:
            self.status = user.get_status()
            self.to = user.get_phone_number()
            self.pokemon_wanted = user.get_pokemon_wanted()
            self.location = (user.get_lat() or user.get_lon())

    def _make_enroll_msg(self):
        logging.info("Sending WELCOME message")
        msg = ("To activate your user, respond in the form of \"Pokemon " +
               "wanted: poke1, poke2, poke3...\" with up to five Pokemon" +
               "A list of commands are:\nPAUSE - temporarily suspend alerts" +
               "\nRESUME - resume previous alerts\nSTOP - quit receiving " +
               "alerts")
        self.to = self._check_len_of_msg(msg)
        return msg

    def _make_stop_msg(self):
        logging.info("Sending STOP message")
        return "Sorry to see you go! Best of luck catchin' 'em all!"

    def _make_pause_msg(self):
        logging.info("Sending PAUSE message")
        return "Respond with RESUME to begin alerts"

    def _make_resume_msg(self):
        logging.info("Sending RESUME message")
        return "Alerts will now be sent for new pokemon near you!"

    def _make_no_pokemon_listed_msg(self):
        logging.info("Sending no pokemon message")
        return "There are no pokemon listed for your user."

    def _make_no_location_msg(self):
        logging.info("Sending no location message")
        return ("It does not look like we have your location. Please send " +
                "us your location and try your request again.")

    def _make_reenroll_msg(self):
        logging.info("Sending no re-enroll message")
        return ("There seems to be a miscommunication. Please try " +
                "re-enrolling by sending us your location first.")

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
        msg = MIMEText("There's a wild {pokemon} near you! Go catch 'em!\n"
                       .format(pokemon=self.pokemon_wanted) +
                       "{link}\n".format(link=self.link))

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
            logging.info("Message too long: {}. Sending MMS".format(len(msg)))
            return self._sms_to_mms()

        return self.to

    def _sms_to_mms(self):
        """ converts the sms carrier gateway to mms carrier gateway """
        updated_to = []
        # since self.to is a list of phone_numbers, we iterate through it
        for num in self.to:
            num, ext = self.to.split('@')

            # check if the carrier is listed in our sms to mms availability
            for i, carrier in enumerate(self.SMS_CARRIERS):
                if ext == carrier:
                    ext = self.MMS_CARRIERS[i]

            updated_to.append(num + "@" + ext)

        return updated_to

    def poke_list_to_str(self):
        """ creates a string from the list of pokemon wanted
        Args:
            pokemon_wanted (list)
        Returns:
            string A string of pokemon such as "poke1, poke2, and poke3"
        """
        str_of_poke = self.pokemon_wanted[0]
        logging.info("List of pokemon_wanted is: {}".format(
                self.pokemon_wanted))

        if len(self.pokemon_wanted) > 1:
            str_of_poke = (", ".join(self.pokemon_wanted[:-1]) +
                           ", and {}".format(self.pokemon_wanted[-1]))
            logging.info("List of pokemon from string is: {}"
                         .format(str_of_poke))

        return str_of_poke

    def build_message(self):
        """ returns the text message to be sent to the receiver
        Args:
            self.status, self.pokemon_wanted, self.location
        Returns:
            One of four messages. Either the STOP message, PAUSE message,
            RESUME message, or ACTIVE
        """
        # new user, no pokemon listed
        if self.status == constants.ACTIVE:
            return self._make_active_msg(), self.to

        elif self.status == constants.ENROLL:
            return self._make_enroll_msg(), self.to

        elif self.status == constants.RESUME:
            if not self.location:
                return self._make_no_location_msg(), self.to
            elif not self.pokemon_wanted:
                return self._make_no_pokemon_listed_msg(), self.to
            else:
                return self._make_resume_msg(), self.to

        elif self.status == constants.PAUSE:
            if not self.location:
                return self._make_no_location_msg(), self.to
            elif not self.pokemon_wanted:
                return self._make_no_pokemon_listed_msg(), self.to
            else:
                return self._make_pause_msg(), self.to

        elif self.status == constants.STOP:
            return self._make_stop_msg(), self.to

        logging.error("Type of message is undetermined. Here's some data to " +
                      "help")
        logging.error("Pokemon wanted: {}".format(self.pokemon_wanted))
        logging.error("Status of user: {}".format(self.status))
        return self._make_reenroll_msg(), self.to
