from email.mime.text import MIMEText
from pnu.config import private_config
from pnu.etc import constants
from pnu.models import Alert
from pnu.outbound.messages import (EnrollMessage, ResumeMessage, PauseMessage,
                                   StopMessage, NoPokemonMessage,
                                   NoLocationMessage, ReEnrollMessage,
                                   AlertMessage, ReceivedMessage, PNEError,
                                   OORError)

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
            self.link = alert.get_short_link().split('/')[3]
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

        # may be empty if only an error is being sent
        if self.pokemon_wanted:
            self._title_case_pokemon_wanted()

    def _make_active_msg(self):
        self.pokemon_wanted = self.poke_list_to_str()
        msg = AlertMessage(self.to).make_msg(
                link = "https://pnu.space/{}".format(self.link),
                pokemon = self.pokemon_wanted,
        )

        return msg

    def _make_received_msg(self):
        self.pokemon_wanted = self.poke_list_to_str()
        msg = ReceivedMessage(self.to).make_msg(pokemon=self.pokemon_wanted)
        return msg

    def _make_enroll_msg(self):
        msg = EnrollMessage(self.to).make_msg()
        return msg

    def _make_no_location_msg(self):
        msg = NoLocationMessage(self.to).make_msg()
        return msg

    def _make_no_pokemon_listed_msg(self):
        msg = NoPokemonMessage(self.to).make_msg()
        return msg

    def _make_resume_msg(self):
        msg = ResumeMessage(self.to).make_msg()
        return msg

    def _make_pause_msg(self):
        msg = PauseMessage(self.to).make_msg()
        return msg

    def _make_stop_msg(self):
        msg = StopMessage(self.to).make_msg()
        return msg

    def _choose_error_msg(self):
        err = None
        if self.errors['code'] == 'PNE':
            incorrect_pokemon = (', ').join(self.errors['data'])
            err = PNEError(self.to).make_msg(incorrect_pokemon=incorrect_pokemon)
        elif self.errors['code'] == 'OOR':
            err = OORError(self.to).make_msg()

        return err

    def _make_reenroll_msg(self):
        msg = ReEnrollMessage(self.to).make_msg()
        return msg

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
        try:
            # test if we have pokeID's or pokemon names
            if isinstance(self.pokemon_wanted[0], int):
                self.pokemon_wanted = [constants.POKEMON_ID_TO_NAME[p]
                                       for p in self.pokemon_wanted]

            self.pokemon_wanted = [p.title() for p in self.pokemon_wanted]
        except TypeError:
            logging.info("No pokemon listed to titlecase")

    def build_message(self):
        """ returns the text message to be sent to the receiver
        Args:
            self.status, self.pokemon_wanted, self.location
        Returns:
            One of four messages. Either the STOP message, PAUSE message,
            RESUME message, or ACTIVE
        """
        logging.info("Sending message with status of {}".format(self.status))
        # new user, no pokemon listed
        if self.status == constants.ACTIVE:
            return self._make_active_msg()

        elif self.status == constants.ENROLL:
            if self.errors:
                return self._choose_error_msg()
            # if they send us pokemon wanted before sending location
            elif self.pokemon_wanted and not self.location:
                return self._make_no_location_msg()
            elif self.pokemon_wanted:
                return self._make_received_msg()

            return self._make_enroll_msg()

        elif self.status == constants.RESUME:
            if not self.location:
                return self._make_no_location_msg()
            elif not self.pokemon_wanted:
                return self._make_no_pokemon_listed_msg()
            else:
                return self._make_resume_msg()

        elif self.status == constants.PAUSE:
            return self._make_pause_msg()

        elif self.status == constants.STOP:
            return self._make_stop_msg()

        logging.error("Type of message is undetermined. Here's some data to " +
                      "help")
        logging.error("Pokemon wanted: {}".format(self. pokemon_wanted))
        logging.error("Status of user: {}".format(self.status))
        return self._make_reenroll_msg()
