from pnu.apis.google_url_api import PnuUrlShortener


class Alert:

    BASE = 'https://pnu.space/map/?'

    def __init__(self, pokemon, users):
        """ takes in a pokemon list/tuple and user list/tuple to notify
        Args:
            pokemon  (List or tuple of pokemon objects)
            user (List or tuple of user objects)
        """
        # the pokemon_tuple are used as keys prior, that's why it's a tuple
        if isinstance(pokemon, tuple):
            self.pokemon = list(pokemon)

        # if the users are not a tuple, but a list, then we won't error out
        if isinstance(users, tuple):
            self.users = list(users)
        else:
            self.users = users

        self.pokemon = pokemon
        self.phone_numbers = [
            user.get_phone_number() for user in self.users
        ]
        self.pokemon_names = [
            pokemon.get_name().capitalize().strip() for pokemon in self.pokemon
        ]
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

    def get_users(self):
        return self.users

    def get_pokemon(self):
        return self.pokemon

    def get_phone_numbers(self):
        return self.phone_numbers

    def get_pokemon_names(self):
        return self.pokemon_names

    def get_short_link(self):
        return self.short_link

    def __str__(self):
        return ("Link: {}\nNumbers: {}\nPokemon: {}".format(
            self.get_short_link(), self.get_phone_numbers(), self.pokemon_names
        ))
