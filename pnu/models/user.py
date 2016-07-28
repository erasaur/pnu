from pnu.models.base import Base
import logging
logging = logging.getLogger(__name__)

class User (Base):
    def load_args (self, phone_number, pokemon_wanted, lat, lon, status):
        self.load_json({
            "phone_number": phone_number,
            "pokemon_wanted": pokemon_wanted,
            "latitude": lat,
            "longitude": lon,
            "status": status,
            "last_notif": last_notif
        })

    def load_json (self, data):
        try:
            self.phone_number = data.get("phone_number")
            self.status = data.get("status")

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
            "status": self.status,
            "last_notif": self.last_notif
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

    def get_last_notif (self):
        return self.last_notif

    def set_last_notif_for_poke (self, poke):
        if not isinstance(self.last_notif, dict):
            self.last_notif = {}

        expiration_time = poke.get_expiration_time()
        last_notif = self.get_last_notif_for_poke(poke)
        poke_id_str = str(poke.get_id())

        if last_notif is None or expiration_time > last_notif:
            self.last_notif[poke_id_str] = expiration_time

    # returns the latest expiration time (i.e newest copy) of
    # the poke that the user has seen so far
    def get_last_notif_for_poke (self, poke):
        if not isinstance(self.last_notif, dict):
            return None
        return self.last_notif.get(poke.get_id())

    def should_be_alerted (self, poke):
        # user should be alerted of pokemon if:
        # - the pokemon is one that the user wants
        # - it's a new appearance of the pokemon
        expiration = poke.get_expiration_time()
        last_notif = self.get_last_notif_for_poke(poke)
        poke_id_str = str(poke.get_id())

        wanted = self.get_pokemon_wanted()
        if not isinstance(wanted, list):
            wanted = []

        return (poke_id_str in wanted and 
            (last_notif is None or expiration > last_notif))

    def empty (self):
        status = self.get_status()
        number = self.get_phone_number()
        is_active = self.is_active()
        return not (status or number or is_active)

    def __str__ (self):
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
