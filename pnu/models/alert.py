from pnu.apis.google_url_api import PnuUrlShortener

class Alert:

    BASE = 'https://pnu.space/map/?'

    def __init__(self, pokemon_tuple, phone_numbers):
        """ takes in a pokemon tuple and list of phone numbers to notify
        Args:
            pokemon_tuple  (Tuple of pokemon objects)
            phone_numbers (List of phone numbers to send the alert to)
        """
        self.pokemon = list(pokemon_tuple)
        self.phone_numbers = phone_numbers
        self._gen_long_url()

    def _gen_long_url(self):
        """ generates the long url to pnu.space based on the pokemon objects """
        url = BASE
        for pokemon in self.pokemon:
            url += (pokemon.get_id() + '=' + pokemon.get_lat() + ','
                    + pokemon.get_lon() + ',' + pokemon.get_expiration_time() + '&')

        # remove the very last '&' from the long url
        self.link = url[:-1]

    def get_long_url(self):
        return self.link

    def get_phone_numbers(self):
        return self.phone_numbers

    def get_pokemon_names(self):
        return [pokemon.get_name() for pokemon in self.pokemon]

    def get_short_link(self):
        self.short_link = PnuUrlShortener(self.link)
        return self.short_link