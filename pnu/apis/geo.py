from math import cos, sin, asin, atan2, sqrt, radians, degrees, pi
from pnu.models import Base
from pnu.config import pub_config

earth_radius = pub_config["geo"]["earth_radius_km"]

# how close locations have to be in order to be grouped together
group_member_dist = pub_config["geo"]["group_member_dist_km"]

def pos_changed (user_a, user_b):
    if user_a is None or user_b is None:
        raise ValueError("invalid users")
    return (user_a.is_active() != user_b.is_active()) or (distance(user_a, user_b) > 0)

def distance (loc_a, loc_b):
    if isinstance(loc_a, Base):
        loc_a = (loc_a.get_lat(), loc_a.get_lon())
    if isinstance(loc_b, Base):
        loc_b = (loc_b.get_lat(), loc_b.get_lon())

    lat1 = radians(float(loc_a[0]))
    lon1 = radians(float(loc_a[1]))
    lat2 = radians(float(loc_b[0]))
    lon2 = radians(float(loc_b[1]))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c

def close_enough (loc_a, loc_b):
    return distance(loc_a, loc_b) < group_member_dist

def get_center_of_group (group):
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

def get_coor_in_dir (init_loc, distance, bearing):
    """ Given an initial lat/lng, a distance(in kms),
    and a bearing (degrees), this will calculate the resulting lat/lng
    coordinates.
    """
    R = earth_radius
    bearing = radians(bearing)

    init_coords = [radians(init_loc[0]),
                   radians(init_loc[1])]  # convert lat/lng to radians

    new_lat = asin(sin(init_coords[0]) * cos(distance/R) +
                        cos(init_coords[0]) * sin(distance/R) *
                        cos(bearing))

    new_lon = (init_coords[1] +
               atan2(sin(bearing) * sin(distance/R) *
                          cos(init_coords[0]),
                          cos(distance/R) - sin(init_coords[0]) *
                          sin(new_lat)))

    return [degrees(new_lat), degrees(new_lon)]
