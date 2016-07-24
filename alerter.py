#! /usr/bin/env python3.5

from smtplib import SMTP
from config import pub_config, private_config
from email.mime.text import MIMEText

class Alert:

    SUBJECT = "Pokemon Alert!"

    def __init__(self):
        """ perform preliminary actions for sending email via SMTP """

        self.smtp = SMTP(pub_config['smtp']['host'], pub_config['smtp']['port'])
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.login(private_config['gmail']['username'],
                private_config['gmail']['password'])

    def __exit__(self):
        self.smtp.quit()

    def build_message(self, info):
        """ returns the text message to be sent to the receiver """
        pokemon_wanted = self.list_to_str(info['pokemon_wanted'])
        a_an = self.format_plural_a_an(info['pokemon_wanted'])

        msg = MIMEText("There's {a_an} {pokemon} near you! Go catch 'em!\n{link}"
                .format(a_an=a_an, pokemon=pokemon_wanted, link=info['link']))
        msg['To'] = info['phone_number']
        msg['From'] = private_config['gmail']['username']
        msg['Subject'] = "Pokemon Alert!"

        return msg.as_string()

    def format_plural_a_an(self, pokemon_wanted):
        """ returns either a or an depending on the 1st letter """
        if pokemon_wanted[0][0].lower() in ['a', 'e', 'i', 'o', 'u']:
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

        self.smtp.sendmail(private_config['gmail']['username'],
                [info['phone_number']], self.build_message(info))

smtp = Alert()
