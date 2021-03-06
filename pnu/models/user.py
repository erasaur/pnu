from pnu.etc import constants
from pnu.models import Base
import logging
logging = logging.getLogger(__name__)


class User (Base):

    def load_args(self, phone_number, pokemon_wanted, lat, lon, status,
                  error_data=None):
        self.load_json({
            "phone_number": phone_number,
            "pokemon_wanted": pokemon_wanted,
            "latitude": lat,
            "longitude": lon,
            "status": status,
            "last_notif": last_notif,
            "error_data": error_data
        })

    def load_json(self, data):
        try:
            self.phone_number = data.get("phone_number")
            self.status = data.get("status")
            self.error_data = data.get("error_data")

            # returns None if key doesn't exist
            self.pokemon_wanted = data.get("pokemon_wanted")
            self.last_notif = data.get("last_notif")

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
            self.last_notif = None
            self.error_data = None

    def get_json(self):
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
            "status": self.status,
            "last_notif": self.last_notif,
            "error_data": self.error_data
        }

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon

    def get_pokemon_wanted(self):
        return self.pokemon_wanted

    def get_phone_number(self):
        return self.phone_number

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def get_errors(self):
        return self.error_data

    def is_location_set(self):
        return self.get_lat() is not None and self.get_lon() is not None

    def is_pokemon_wanted_set(self):
        pw = self.get_pokemon_wanted()
        return isinstance(pw, list) and len(pw) > 0

    def is_enrolled(self):
        return self.is_location_set() and self.is_pokemon_wanted_set()

    def is_active(self):
        return self.is_enrolled() and self.get_status() != constants.PAUSE

    def get_last_notif(self):
        return self.last_notif

    # returns the latest expiration time (i.e newest copy) of
    # the poke that the user has seen so far
    def get_last_notif_for_poke(self, poke):
        # convert to string because dict keys are strings
        poke_id_str = str(poke.get_id())
        if not isinstance(self.last_notif, dict):
            return None
        return self.last_notif.get(poke_id_str)

    def set_last_notif_for_poke(self, poke):
        if not isinstance(self.last_notif, dict):
            self.last_notif = {}

        expiration_time = poke.get_expiration_time()
        last_notif = self.get_last_notif_for_poke(poke)
        poke_id_str = str(poke.get_id())

        if last_notif is None or expiration_time > last_notif:
            self.last_notif[poke_id_str] = expiration_time

    def should_be_alerted(self, poke):
        # user should be alerted of pokemon if:
        # - status is not paused
        # - the pokemon is one that the user wants
        # - it's a new appearance of the pokemon
        if self.get_status() == constants.PAUSE:
            return False

        expiration = poke.get_expiration_time()
        last_notif = self.get_last_notif_for_poke(poke)
        poke_id = poke.get_id()

        wanted = self.get_pokemon_wanted()
        if not isinstance(wanted, list):
            wanted = []

        return (poke_id in wanted and
                (last_notif is None or expiration > last_notif))

    def empty(self):
        status = self.get_status()
        number = self.get_phone_number()
        location = self.is_location_set()
        pokemon = self.is_pokemon_wanted_set()
        return not (status or number or location or pokemon)

    def __str__(self):
        template = ("Phone #: {}\n"
                    "Pokemon wanted: {}\n"
                    "Latitude: {}\n"
                    "Longitude: {}\n"
                    "Status: {}\n"
                    "Last Notif: {}\n")
        return template.format(
            self.phone_number,
            self.pokemon_wanted,
            self.lat, self.lon,
            self.status,
            self.last_notif
        )
