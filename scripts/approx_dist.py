import requests, urllib, csv

max_lat = max_lon = 0

MAP_API = "http://maps.googleapis.com/maps/api/geocode/json?address={}"
POKE_API = "https://pokevision.com/map/data/{}/{}"

with open('top100.csv', 'r') as f:
    reader = csv.reader(f)
    cities = list(reader)

out = open('out', 'w')

for x in cities:
    try:
        x = x[0].lower()
        url = MAP_API.format(urllib.parse.quote_plus(x))

        response = requests.get(url).json()
        city = response["results"][0]
        loc = city["geometry"]["location"]

        poke_url = POKE_API.format(loc["lat"], loc["lng"])
        res = requests.get(poke_url).json()

        lats = []
        lons = []
        for p in res["pokemon"]:
            lats.append(p["latitude"])
            lons.append(p["longitude"])
        
        sorted_lat = sorted(lats)
        sorted_lon = sorted(lons)

        cur_lat = abs(sorted_lat[-1] - sorted_lat[0])
        cur_lon = abs(sorted_lon[-1] - sorted_lon[0])
        
        max_lat = max(max_lat, cur_lat)
        max_lon = max(max_lon, cur_lon)
        out.write("{}: {} {}\n".format(x, cur_lat, cur_lon))
    except Exception as e:
        out.write("{}: {}\n".format(x, e))

out.close()

print(max_lat, max_lon)
