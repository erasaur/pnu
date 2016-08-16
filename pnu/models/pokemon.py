from pnu.models import Base
from pnu.etc.constants import POKEMON_ID_TO_NAME

class Pokemon (Base):
    def load_args (self, pokemonId, lat, lon, expiration_time):
        self.load_json({
            "pokemonId": pokemonId,
            "latitude": lat,
            "longitude": lon,
            "expiration_time": expiration_time
        })

    def load_json(self, data):
        super().load_json(data)

        try:
            self.pokemon_name = POKEMON_ID_TO_NAME[self.pokemonId]
        except:
            self.pokemon_name = None

    def get_json(self):
        return {
            "pokemonId": self.pokemonId,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "expiration_time": self.expiration_time
        }

    # load_tuple equivalent to load_args(*tuple)
    def get_tuple(self):
        return (
            self.pokemonId,
            self.latitude,
            self.longitude,
            self.expiration_time
        )

    def get_name(self):
        return self.pokemon_name

    def get_id(self):
        return self.pokemonId

    def get_lat(self):
        return self.latitude

    def get_lon(self):
        return self.longitude

    def get_expiration_time(self):
        return self.expiration_time

    def __str__ (self):
        return "Id: {}\nName: {}\nLat: {}\nLon: {}\nExpiration: {}".format(
            self.get_id(), self.get_name(), self.get_lat(),
            self.get_lon(), self.get_expiration_time())
