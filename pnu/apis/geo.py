from math import cos, sin, atan2, sqrt, radians, pi
from pnu.config import pub_config

earth_radius = pub_config["geo"]["earth_radius_km"]

# how close locations have to be in order to be grouped together
group_member_dist = pub_config["geo"]["group_member_dist_km"]

def pos_changed (self, user_a, user_b):
    if user_a is None or user_b is None:
        raise ValueError("invalid users")
    return (user_a.is_active() != user_b.is_active()) or (self.distance(user_a, user_b) > 0)

def distance (self, user_a, user_b):
    lat1 = radians(float(user_a.get_lat()))
    lon1 = radians(float(user_a.get_lon()))
    lat2 = radians(float(user_b.get_lat()))
    lon2 = radians(float(user_b.get_lon()))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c

def close_enough (self, user_a, user_b):
    return self.distance(user_a, user_b) < group_member_dist

def get_center_of_group (self, group):
    x = 0
    y = 0
    z = 0

    for member in group:
        lat = radians(float(member.get_lat()))
        lon = radians(float(member.get_lon()))
        x += cos(lat) * cos(lon)
        y += cos(lat) * sin(lon)
        z += sin(lat)

    x = float(x / len(group))
    y = float(y / len(group))
    z = float(z / len(group))

    center_lat = 180 * atan2(z, sqrt(x * x + y * y)) / pi
    center_lon = 180 * atan2(y, x) / pi

    return center_lat, center_lon

def get_coor_in_dir (self, init_loc, distance, bearing):
    """ Given an initial lat/lng, a distance(in kms),
    and a bearing (degrees), this will calculate the resulting lat/lng
    coordinates.
    """
    R = self._earth_radius
    bearing = math.radians(bearing)

    init_coords = [math.radians(init_loc[0]),
                   math.radians(init_loc[1])]  # convert lat/lng to radians

    new_lat = math.asin(math.sin(init_coords[0]) * math.cos(distance/R) +
                        math.cos(init_coords[0]) * math.sin(distance/R) *
                        math.cos(bearing))

    new_lon = (init_coords[1] +
               math.atan2(math.sin(bearing) * math.sin(distance/R) *
                          math.cos(init_coords[0]),
                          math.cos(distance/R) - math.sin(init_coords[0]) *
                          math.sin(new_lat)))

    return [math.degrees(new_lat), math.degrees(new_lon)]
