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
                    + pokemon.get_lon() + ',' + pokemon.get_time_to_exp() + '&')

        # remove the very last '&' from the long url
        self.link = url[:-1]

    def get_long_url(self):
        return self.link
