from pnu.models.base import Base
import logging
logger = logging.getLogger(__name__)

class User (Base):

    def __init__ (self, *args):
        self.load_json(args)

    def load_args (self, phone_number, pokemon_wanted, latitude, longitude,
            status):
        self.load_json(
            phone_number=phone_number,
            pokemon_wanted=pokemon_wanted,
            latitude=latitude,
            longitude=longitude,
            status=status,
        )

    def load_json (self, *args):
        # access the 1st element of the tuple
        args = args[0][0]
        try:
            self.phone_number = args["phone_number"]
            self.status = args["status"]

            # returns None if key doesn't exist
            self.pokemon_wanted = args.get('pokemon_wanted')

            if args.get("location"):
                loc = args["location"]
                self.lat = loc["lat"]
                self.lon = loc["lon"]
            else:
                self.lat = None
                self.lon = None
        except KeyError as e:
            logging.error("Invalid user data")
            logging.error(e)
            raise e

    def get_json(self):
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

    def get_phone_number (self):
        return self.status

    def __str__ (self):
        return ("Phone #: " + str(self.phone_number) + "\n" +
               "Pokemon wanted: " + str(self.pokemon_wanted) + "\n" +
               "Latitude: " + str(self.lat) + "\n" +
               "Longitude: " + str(self.lon) + "\n" +
               "Status: " + str(self.status) + "\n")
