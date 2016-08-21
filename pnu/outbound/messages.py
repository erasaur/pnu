import random
import itertools
from email.mime.text import MIMEText

from pnu.config import private_config
from pnu.etc import constants

import logging
logging = logging.getLogger(__name__)

class Message:

    SMS_CARRIERS = ["message.alltel.com", "txt.att.net", "myboostmobile.com",
                    "messaging.sprintpcs.com", "tmomail.net",
                    "email.uscc.net", "vtext.com", "vmobl.com"]
    MMS_CARRIERS = ["mms.alltelwireless.com", "mms.att.net",
                    "myboostmobile.com", "pm.sprint.com", "tmomail.net",
                    "mms.uscc.net", "vzwpix.com", "vmpix.com"]

    def __init__(self, to, subject=None):
        if isinstance(to, list):
            self.to = ', '.join(to)
        else:
            self.to = to

        if subject:
            self.subject = subject

    def make_msg(self, **kwargs):
        self.message = self._get_rand_msg(**kwargs)

        final_msg = MIMEText(self.message)
        final_msg['From'] = private_config['gmail']['username']
        final_msg['Subject'] = self.subject
        self._sms_to_mms(final_msg)
        final_msg['To'] = self.to

        logging.info("Sending {} message.".format(self.subject))
        return final_msg.as_string()

    def _get_rand_msg(self, **kwargs):
        msg = ""
        # build message based on randomly selecting from each of the
        # message parts
        for i, msg_list in enumerate(self.MESSAGES):
            pick = random.randrange(0, len(msg_list))
            msg += msg_list[pick].format(**kwargs)
        return msg

    def _sms_to_mms(self, msg):
        if len(msg.get_payload()) <= constants.MAX_SMS_MESSAGE_LEN:
            return

        logging.info("Message too long: {}. Sending MMS".format(len(msg)))
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
            self.to = updated_to

        # if not multiple users, we only need the 1 'to' address
        self.to = updated_to[0]


class EnrollMessage(Message):

    subject = ""
    MESSAGES = [
        ("To activate ", "To enroll ", "To enable ", "To begin using ",),
        ("your account ", "this service ",),
        ("respond ","reply ","text back ",),
        ("with ","in the form of ","to us with ",),
        ("\"Pokemon wanted: ",),
        ("poke1, poke2, poke3...\" ","poke1, poke2...\" ",),
        ("", "with ",),
        ("up to ","up to a maximum of ",),
        ("10 Pokemon. ",),
        ("Commands available ","A list of commands ","Possible commands ",),
        ("are:\n",)
    ]

    COMMANDS = [
        "PAUSE - suspend alerts\n",
        "RESUME - resume alerts\n",
        "STOP - quit receiving alerts\n"
    ]

    MSG_COMMANDS = [
        "PAUSE - suspend messages\n",
        "RESUME - resume messages\n",
        "STOP - quit receiving messages\n"
    ]

    def __init__(self, to):
        super().__init__(to)
        commands = itertools.permutations(self.COMMANDS)
        msg_commands = itertools.permutations(self.MSG_COMMANDS)
        com_list = []
        for command in commands:
            com_list.append(command)
        msg_com_list = []
        for msg_command in msg_commands:
            msg_com_list.append(msg_command)

        which_perm = random.randrange(0, max(len(com_list), len(msg_com_list)))
        which_cmd = random.randrange(0, 2)
        final_com_list = com_list if which_cmd else msg_com_list
        to_append = ""
        for cmd in final_com_list[which_perm]:
            to_append += cmd

        self.MESSAGES.append(cmd)


class ResumeMessage(Message):

    subject = "Resuming"
    MESSAGES = [
        ("Alerts ","Notifications ","Messages ","Texts ","SMS's ",),
        ("are now ","will be ","will now be ",),
        ("turned on ",),
        ("for Pokemon ",),
        ("around ","near ","close to ","near by ",),
        ("your location.","your location!","you!","you.",),
    ]


class PauseMessage(Message):

    subject = "Pausing"
    MESSAGES = [
        ("Respond ","Reply ","Text back ","Send a message ",),
        ("with RESUME ","including RESUME in it ",),
        ("to ",),
        ("begin ","activate ","start ",),
        ("receiving ","getting ","allowing ","experiencing ",),
        ("alerts ","notifications ","texts ","sms's ","messages "),
    ]


class StopMessage(Message):

    subject = "Goodbye"
    MESSAGES = [
        ("Sorry to see you go! ",
         "You will now be removed from alerts. ",
         "Alerts will no longer be sent. ",
         "You have been removed from any future alerts. ",),
        ("Best of luck ","Have fun ","Enjoy ","Have a good time ",),
        ("catchin' ","finding ", "capturing ",),
        ("all of 'em!","'em all!","all of them!","Pokemon!",),
    ]


class NoPokemonMessage(Message):

    subject = "Incomplete Pokemon Wanted"
    MESSAGES = [
        ("There are no Pokemon ","No Pokemon are ","Pokemon are not ",),
        ("associated ","listed ","paired ","assigned ",),
        ("with your ",),
        ("account. ","user. ","person. ","trainer. "),
        ("Reply ","Respond ","Text back ","Message us ",),
        ("in the form of ","with "),
        ("\"Pokemon wanted: ",),
        ("poke1, poke2, poke3...\" ","poke1, poke2...\" ",),
        ("with ",),
        ("up to ","as many as ", "",),
        ("10 Pokemon.",),
    ]


class NoLocationMessage(Message):

    subject = "No Location Listed"
    MESSAGES = [
        ("It does not look like there is a ","There is no ","No ",),
        ("location ",),
        ("associated ","listed ","paired ",),
        ("with ","to ",),
        ("your ",),
        ("user. ","trainer. ","person. ","account. ",),
        ("Please send ","Send ","Text ","Message ","Please give ", "Give ",),
        ("us your ",),
        ("location","current location",),
    ]


class ReEnrollMessage(Message):

    subject = "Oops!"
    MESSAGES = [
        ("An error occurred. ",
         "Something went wrong. ",
         "We messed up. ",
         "Our bad! ",),
        ("Please try ","Try ",),
        ("re-sending ","re-enrolling by sending ","messaging ","texting ",),
        ("us your location ",),
        ("again.","once more.","at this time.","now.",),
    ]


class AlertMessage(Message):

    subject = "Pokemon Alert!"
    MESSAGES = [
        ("Go catch a wild ",
         "There's a ",
         "A ",
         "Go catch a ",
         "Catch the ",
         "Catch ",
         "",),
        ("{pokemon} ",),
        ("near you. ",
         "in the area. ",
         "close by. ",
         "in the vicinity. ",
         "by you. ",
         "around you. ",
         "around. ",),
        ("{link}",),
    ]


class ReceivedMessage(Message):

    subject = "Pokemon Tracked"
    MESSAGES = [
        ("We are currently tracking these Pokemon ",
         "We are watching these Pokemon ",
         "These Pokemon are being tracked ",
         "These Pokemon are being watched ",
         "The following Pokemon are in our database ",
         "We've stored these Pokemon ",
         "Tracking these Pokemon ",
         "Following these Pokemon ",),
        ("for you: {pokemon}",),
    ]


class PNEError(Message):
    """
        error message for when a user submits a pokemon that is
        non-existent
    """
    subject = "Non-Existent Pokemon"
    MESSAGES = [
        ("We didn't recognize the following Pokemon: {incorrect_pokemon}. " +
         "Double check the spelling and try again.",),
    ]


class OORError(Message):
    """
        error message for when a user enrolls and is not within the
        location designated by their host
    """

    subject = "Out of Range"
    link = "https://github.com/erasaur/pnu/wiki/Location-Restrictions"
    MESSAGES = [
        ("We're sorry, it looks like you are outside this region's " +
         "designated tracking area. More information can be found " +
         "here {link}".format(link=link)),
    ]
