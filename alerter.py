#! /usr/bin/env python3.5

from smtplib import SMTP
from config import JSONConfig

class Alert:

    SUBJECT = "Pokemon Alert!"

    def __init__(self):
        """ perform preliminary actions for sending email via SMTP """
        self.smtp = SMTP(JSONConfig['smtp']['host'], JSONConfig['smtp']['port'])
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.login(JSONConfig['gmail']['username'], JSONConfig['gmail']['password'])

    def __exit__(self):
        self.smtp.quit()

    def build_message(self):
        """ returns the text message to be sent to the receiver """
        a_an = self.format_plural_a_an()

        msg = ("Subject: {subject}\n\n".format(subject=self.SUBJECT) +
               "There's {a_an} {pokemon} near you! Go catch 'em!\n{link}"
               .format(a_an=a_an, pokemon=self.pokemon_wanted, link=self.link))
        return msg

    def format_plural_a_an(self):
        """ returns either a or an depending on the 1st letter """
        if self.pokemon_wanted[0][0].lower() in ['a', 'e', 'i', 'o', 'u']:
            return 'an'

        return 'a'

    def list_to_str(self, pokemon_wanted):
        """ creates a string from the list of pokemon wanted 
        Args:
            pokemon_wanted (list)
        Returns:
            string A string of pokemon such as "poke1, poke2, and poke3"
        """
        str_of_poke = pokemon_wanted[0]

        if len(pokemon_wanted) > 1:
            str_of_poke = ','.join(pokemon_wanted) + ", and " + pokemon_wanted[-1]

        return str_of_poke

    def send_message(self, info):
        """ sends a text message alert to the specified user
        Args:
            info (dictionary)
        """
        self.phone_number = info['phone_number']
        self.pokemon_wanted = self.list_to_str(info['pokemon_wanted'])
        self.link = info['link']

        self.smtp.sendmail(JSONConfig['gmail']['username'], [self.phone_number],
                self.build_message())

smtp = Alert()
