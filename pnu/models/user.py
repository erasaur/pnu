from pnu.models.base import Base
import logging
logging = logging.getLogger(__name__)

class User (Base):
    def load_args (self, phone_number, pokemon_wanted, lat, lon, status):
        self.load_json(
            phone_number=phone_number,
            pokemon_wanted=pokemon_wanted,
            latitude=lat,
            longitude=lon,
            status=status,
        )

    def load_json (self, data):
        try:
            self.phone_number = data.get("phone_number")
            self.status = data.get("status")

            # returns None if key doesn't exist
            self.pokemon_wanted = data.get("pokemon_wanted")

            loc = data.get("location")
            if loc is not None:
                self.lat = loc.get("lat")
                self.lon = loc.get("lon")
            elif "latitude" in data and "longitude" in data:
                self.lat = data.get("latitude")
                self.lon = data.get("longitude")
            else:
                self.lat = self.lon = None
        except KeyError as e:
            logging.info("Error loading user model: {}".format(e))
            self.phone_number = None
            self.status = None
            self.pokemon_wanted = None
            self.lat = self.lon = None

    def get_json (self):
        location = None
        if self.lat and self.lon:
            location = {
                "lat": self.lat,
                "lon": self.lon
            }

        return {
            "phone_number": self.phone_number,
            "pokemon_wanted": self.pokemon_wanted,
            "location": location,
            "status": self.status
        }

    def get_lat (self):
        return self.lat

    def get_lon (self):
        return self.lon

    def get_pokemon_wanted (self):
        return self.pokemon_wanted

    def get_phone_number (self):
        return self.phone_number

    def get_status (self):
        return self.status

    def is_location_set(self):
        return self.get_lat() is not None and self.get_lon() is not None

    def is_pokemon_wanted_set (self):
        pw = self.get_pokemon_wanted()
        return isinstance(pw, list) and len(pw) > 0

    def is_active (self):
        return self.is_location_set() and self.is_pokemon_wanted_set()

    def empty (self):
        status = self.get_status()
        number = self.get_phone_number()
        is_active = self.is_active()
        return not (status or number or is_active)

    def __str__ (self):
        return ("Phone #: {}\nPokemon wanted: {}\nLatitude: {}\nLongitude: {}\n"
                "Status: {}".format(self.phone_number, self.pokemon_wanted,
                                    self.lat, self.lon, self.status))
