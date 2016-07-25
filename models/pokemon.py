from base import Base

class Pokemon (Base):
    def get_json (self):
        return {
            "pokemonId": self["pokemonId"],
            "latitude": self["latitude"],
            "longitude": self["longitude"]
        }

    def get_lat (self):
        return self["latitude"]

    def get_lon (self):
        return self["longitude"]
