class User:
    def __init__(self, phone_number, pokemon_wanted, lat, lon):
        self.phone_number = phone_number
        self.pokemon_wanted = pokemon_wanted
        self.lat = lat
        self.lon = lon

    def get_all_properties(self):
        return {"phone_number": self.phone_number,
                "pokemon_wanted": self.pokemon_wanted,
                "location": {
                        "lat": self.lat,
                        "lon": self.lon
                    }
                }

    def get_lat(self):
        return self.lat

    def get_lon(sefl):
        return self.lon

    def get_pokemon_wanted(self):
        return self.pokemon_wanted

    def get_phone_number(self):
        return self.phone_number

    def __str__(self):
        return ("Phone #: " + self.phone_number + "\n" +
               "Pokemon wanted: " + self.pokemon_wanted + "\n" +
               "Latitude: " + self.lat + "\n" +
               "Longitude: " + self.lon + "\n")
