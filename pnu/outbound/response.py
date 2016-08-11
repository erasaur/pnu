from email.mime.text import MIMEText
from pnu.config import private_config
from pnu.etc import constants
from pnu.models import Alert

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
            logging.info("Sending an alert to {}".format(user))
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
            logging.info("Sending a message to user {}".format(user))
            self.status = user.get_status()
            self.errors = user.get_errors()
            self.to = user.get_phone_number()
            self.pokemon_wanted = user.get_pokemon_wanted()
            self.location = (user.get_lat() or user.get_lon())

        self._title_case_pokemon_wanted()

    def _make_enroll_msg(self):
        logging.info("Sending WELCOME message")
        msg = MIMEText("\nTo activate your user, respond in the form of \"" +
               "Pokemon wanted: poke1, poke2, poke3...\" with up to five " +
               "Pokemon. A list of commands are:\nPAUSE - temporarily " +
               "suspend alerts\nRESUME - resume previous alerts\nSTOP - " +
               "quit receiving alerts")
        self.to = self._check_len_of_msg(msg.get_payload())

        msg['To'] = self.to[0]
        msg['From'] = private_config['gmail']['username']
        msg['Subject'] = self.SUBJECT

        return msg.as_string()

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

    def _make_error_msg(self):
        logging.info("Error message being sent")
        incorrect_pokemon = (', ').join(self.errors)
        msg = ("We didn't recognize these pokemon: {}."
               .format(incorrect_pokemon) + "Double check the spelling and " +
               "try again.")

        return msg

    def _make_received_msg(self):
        msg = ("We are currently tracking these Pokémon for you: {}"
               .format(self.poke_list_to_str()))
        return msg

    def _check_len_of_msg(self, msg):
        """ checks if the message length is longer than 159 chars """
        if (len(msg) > constants.MAX_SMS_MESSAGE_LEN):
            logging.info("Message too long: {}. Sending MMS".format(len(msg)))
            return self._sms_to_mms()

        return self.to

    def _sms_to_mms(self):
        """ converts the sms carrier gateway to mms carrier gateway """
        updated_to = []
        # since self.to is a list of phone_numbers, we iterate through it
        for number in [self.to]:
            num, ext = number.split('@')

            # check if the carrier is listed in our sms to mms availability
            for i, carrier in enumerate(self.SMS_CARRIERS):
                if ext == carrier:
                    ext = self.MMS_CARRIERS[i]

            updated_to.append(num + "@" + ext)

        # check if sending to multiple users
        if len(updated_to) > 1:
            return updated_to

        # if not multiple users, we only need the 1 'to' address
        return updated_to[0]

    def poke_list_to_str(self):
        """ creates a string from the list of pokemon wanted
        Args:
            pokemon_wanted (list)
        Returns:
            string A string of pokemon such as "poke1, poke2, and poke3"
        """
        str_of_poke = self.pokemon_wanted[0].title()
        logging.info("List of pokemon_wanted is: {}".format(
                self.pokemon_wanted))

        if len(self.pokemon_wanted) > 1:
            str_of_poke = (", ".join(self.pokemon_wanted[:-1]) +
                           ", and {}".format(self.pokemon_wanted[-1]))
            logging.info("List of pokemon from string is: {}"
                         .format(str_of_poke))

        return str_of_poke

    def _title_case_pokemon_wanted(self):
        """ rattata == Rattata, pidgey == Pidgey """
        self.pokemon_wanted = [poke.title() for poke in self.pokemon_wanted]

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
            if self.errors:
                return self._make_error_msg(), self.to
            elif self.pokemon_wanted:
                return self._make_received_msg(), self.to

            return self._make_enroll_msg(), self.to

        elif self.status == constants.RESUME:
            if not self.location:
                return self._make_no_location_msg(), self.to
            elif not self.pokemon_wanted:
                return self._make_no_pokemon_listed_msg(), self.to
            else:
                return self._make_resume_msg(), self.to

        elif self.status == constants.PAUSE:
            return self._make_pause_msg(), self.to

        elif self.status == constants.STOP:
            return self._make_stop_msg(), self.to

        logging.error("Type of message is undetermined. Here's some data to " +
                      "help")
        logging.error("Pokemon wanted: {}".format(self.pokemon_wanted))
        logging.error("Status of user: {}".format(self.status))
        return self._make_reenroll_msg(), self.to
