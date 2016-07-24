class User:
    def __init__(self, **kwargs):
        if 'data' in kwargs:
            self.load_json(kwargs.pop('data'))
        else:
            self.load(**kwargs)

    def load(self, **kwargs):
        try:
            for k in ['phone_number', 'pokemon_wanted', 'lat', 'lon']:
                self[k] = kwargs.pop(k)
        except:
            raise Exception('invalid user arguments')

    def load_json(self, data):
        try:
            self.phone_number = data["phone_number"]
            self.pokemon_wanted = data["pokemon_wanted"]
            self.lat = data["location"]["lat"]
            self.lon = data["location"]["lon"]
        except:
            raise Exception('invalid user object')

    def get_json(self):
        return {
            "phone_number": self.phone_number,
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
