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
        self._gen_url()

    def _gen_url(self):
        """ creates the long url to pnu.space based on the pokemon objects """
        url = self.BASE
        for pokemon in self.pokemon:
            url += "{id}={lat},{lon},{exp_time}&".format(
                    id=pokemon.get_id(),
                    lat=pokemon.get_lat(), lon=pokemon.get_lon(),
                    exp_time=pokemon.get_expiration_time())

        # remove the very last '&' from the long url
        self.link = url[:-1]
        self.short_link = PnuUrlShortener(self.link)

    def get_long_url(self):
        return self.link

    def get_phone_numbers(self):
        return self.phone_numbers

    def get_pokemon_names(self):
        return [pokemon.get_name().capitalize() for pokemon in self.pokemon]

    def get_short_link(self):
        return self.short_link

    def __str__ (self):
        return ("Link: {}\nNumbers: {}\n".format(
            self.get_short_link(), self.get_phone_numbers()
        ))
