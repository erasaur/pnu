from pnu.models.base import Base
import logging
logger = logging.getLogger(__name__)

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
            self.phone_number = data["phone_number"]
            self.status = data["status"]

            # returns None if key doesn't exist
            self.pokemon_wanted = data.get('pokemon_wanted')

            if "location" in data:
                loc = data["location"]
                self.lat = loc["lat"]
                self.lon = loc["lon"]
            elif "latitude" in data and "longitude" in data:
                self.lat = data["latitude"]
                self.lon = data["longitude"]
            else:
                self.lat = self.lon = None
        except KeyError as e:
            logging.error("Invalid user data")
            logging.error(e)
            raise e

    def get_json (self):
        return {
            "phone_number": self.phone_number,
            "pokemon_wanted": self.pokemon_wanted,
            "location": {
                "lat": self.lat,
                "lon": self.lon
            },
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


    def __str__ (self):
        return ("Phone #: " + str(self.phone_number) + "\n" +
               "Pokemon wanted: " + str(self.pokemon_wanted) + "\n" +
               "Latitude: " + str(self.lat) + "\n" +
               "Longitude: " + str(self.lon) + "\n" +
               "Status: " + str(self.status) + "\n")
