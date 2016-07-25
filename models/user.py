from base import Base

class User (Base):
    def load_args (self, phone_number, pokemon_wanted, latitude, longitude):
        self.load_json(
            "phone_number"=phone_number,
            "pokemon_wanted"=pokemon_wanted,
            "latitude"=latitude,
            "longitude"=longitude
        )

    def load_json (self, *args, **kwargs):
        try:
            self["phone_number"] = kwargs["phone_number"]
            self["pokemon_wanted"] = kwargs["pokemon_wanted"]

            if "location" in kwargs:
                loc = kwargs["location"]
                self["latitude"] = loc["lat"]
                self["longitude"] = loc["lon"]
            else:
                self["latitude"] = kwargs["latitude"]
                self["longitude"] = kwargs["longitude"]
        except:
            raise Exception('trying to load invalid data')

    def get_json(self):
        return {
            "phone_number": self["phone_number"],
            "pokemon_wanted": self["pokemon_wanted"],
            "location": {
                "lat": self["latitude"],
                "lon": self["longitude"]
            }
        }

    def get_lat (self):
        return self.lat

    def get_lon (self):
        return self.lon

    def get_pokemon_wanted (self):
        return self.pokemon_wanted

    def get_phone_number (self):
        return self.phone_number

    def __str__ (self):
        return ("Phone #: " + self.phone_number + "\n" +
               "Pokemon wanted: " + self.pokemon_wanted + "\n" +
               "Latitude: " + self.lat + "\n" +
               "Longitude: " + self.lon + "\n")
