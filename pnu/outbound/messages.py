import random


class Message:

    SMS_CARRIERS = ["message.alltel.com", "txt.att.net", "myboostmobile.com",
                    "messaging.sprintpcs.com", "tmomail.net",
                    "email.uscc.net", "vtext.com", "vmobl.com"]
    MMS_CARRIERS = ["mms.alltelwireless.com", "mms.att.net",
                    "myboostmobile.com", "pm.sprint.com", "tmomail.net",
                    "mms.uscc.net", "vzwpix.com", "vmpix.com"]

    def __init__(self, to, subject):
        self.to = to
        self.subject = subject

    def make_msg(self, **kwargs):
        self.message = self._get_rand_msg(**kwargs)

        final_msg = MIMEText(self.message)
        final_msg['From'] = private_config['gmail']['username']
        final_msg['Subject'] = self.subject
        self._sms_to_mms(final_msg)
        final_msg['To'] = self.to
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
        "STOP - quit receiving messages\n"
    ]

    def __init__(self, to, subject):
        super().__init__(to, subject)
        commands = self._permute_commands(0, "", self.COMMANDS.copy()))
        self.MESSAGES.append(tuple(commands))

    def _permute_commands (depth, curr, commands):
        result = []
        if depth >= len(commands):
            if curr != "":
                result.append(curr)
            return result

        for index, command in enumerate(commands)
            if command != "":
                commands[index] = ""
                rest = self._permute_commands(depth+1, curr + command, commands)
                result += rest
                commands[index] = command
        return result

class ResumeMessage(Message):
    MESSAGES = [
        ("Alerts ","Notifications ","Messages ","Texts ","SMS's ",),
        ("are now ","will be ","will now be ",),
        ("turned on ",),
        ("for Pokemon",),
        ("around ","near ","close to ","near by",),
        ("your location.","your location!","you!","you.",),
    ]


class PauseMessage(Message):
    MESSAGES = [
        ("Respond ","Reply ","Text back ","Send a message ",),
        ("with RESUME ","including RESUME in it ",),
        ("to ",),
        ("begin ","activate ","start ",),
        ("receiving ","getting ","allowing ","experiencing ",),
        ("alerts ","notifications ","texts ","sms's ",),
    ]


class StopMessage(Message):
    MESSAGES = [
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
    ]


class NoPokemonMessage(Message):
    MESSAGES = [
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
    ]


class NoLocationMessage(Message):
    MESSAGES = [
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
    ]


class ReEnrollMessage(Message):
    MESSAGES = [
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
    ]


class AlertMessage(Message):
    MESSAGES = [
        ("Go catch a wild ","There's a ","A ","Go catch a ",""),
        ("{pokemon}","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
    ]


class ErrorMessage(Message):
    MESSAGES = [
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
    ]

    def make_msg(self, **kwargs):
        logging.info("Error message being sent")
        em = ErrorMsg()
        err = None

        if self.errors['code'] == 'PNE':
            logging.info("Pokemon Not Existent error")
            incorrect_pokemon = (', ').join(self.errors['data'])
            err = em.pne(incorrect_pokemon)
        elif self.errors['code'] == 'OOR':
            logging.info("User Out Of Range error")
            err = em.oor(self.errors['data'][0], self.errors['data'][1])

        return self._enc_string(err.msg, err.subj)


class ReceivedMessaged(Message):
    MESSAGES = [
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
        ("","","","",),
    ]
