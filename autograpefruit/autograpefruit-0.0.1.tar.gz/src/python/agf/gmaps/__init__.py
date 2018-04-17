import googlemaps
import json
import time
import traceback
import math
from math import radians, cos, sin, asin, sqrt, fabs
from random import uniform as urand

def bearing(coords_start, coords_end):
    lat1 = coords_start[0]
    lon1 = coords_start[1]
    lat2 = coords_end[0]
    lon2 = coords_end[1]
    startLat = math.radians(lat1)
    startLong = math.radians(lon1)
    endLat = math.radians(lat2)
    endLong = math.radians(lon2)
    dLong = endLong - startLong
    dPhi = math.log(math.tan(endLat/2.0+math.pi/4.0)/math.tan(startLat/2.0+math.pi/4.0))
    if abs(dLong) > math.pi:
        if dLong > 0.0:
            dLong = -(2.0 * math.pi - dLong)
        else:
            dLong = (2.0 * math.pi + dLong)
    bearing = (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0;
    return bearing

def haversine(coords_start, coords_end):
    # https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [coords_start[1], coords_start[0], coords_end[1], coords_end[0]])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def points_along_line(num_points, coords_start, coords_end):
    lat1 = coords_start[0]
    lon1 = coords_start[1]
    lat2 = coords_end[0]
    lon2 = coords_end[1]
    if num_points <= 0:
        return []
    if num_points == 1:
        return [(((lat1+lat2)/2),((lon1+lon2)/2))]
    if num_points == 2:
        return [(lat1,lon1), (lat2,lon2)]
    lat_diff = lat2 - lat1
    lon_diff = lon2 - lon1
    points = [(lat1 + i * (lat_diff/(num_points-1)), (lon1 + i * (lon_diff/(num_points-1)))) for i in range(0, num_points)]
    return points

def bounds(coords, radius_km=1):
    # Yeah, this generates a rectangle, not a circle.  I'm lazy.
    lat = coords[0]
    lon = coords[1]
    nelat = lat * 1.001
    nelon = lon * 1.001
    swlat = lat * .999
    swlon = lon * .999
    nedistance = haversine(lat, lon, nelat, nelon)
    while fabs(1 - nedistance / radius_km) > .1:
        if nedistance > radius_km:
            nelat = nelat - (nelat - lat) / 2
            nelon = nelon - (nelon - lon) / 2
        else:
            nelat = nelat + (nelat - lat) / 10
            nelon = nelon + (nelon - lon) / 10
        nedistance = haversine(lat, lon, nelat, nelon)

    swdistance = haversine(lat, lon, swlat, swlon)
    while fabs(1 - swdistance / radius_km) > .1:
        if swdistance > radius_km:
            swlat = swlat - (swlat - lat) / 2
            swlon = swlon - (swlon - lon) / 2
        else:
            swlat = swlat + (swlat - lat) / 10
            swlon = swlon + (swlon - lon) / 10
        swdistance = haversine(lat, lon, swlat, swlon)
    return (nelat,nelon), (swlat,swlon)

def canonical_address_from_result(result):
    if "vicinity" in result:
        return result["vicinity"]
    addr_parts = address_parts_from_result(result)
    if addr_parts:
        addr = ""
        if "street_number" in addr_parts:
            addr += addr_parts["street_number"] + " "
        if "route" in addr_parts:
            addr += addr_parts["route"] + ", "
        if "locality/political" in addr_parts:
            addr += addr_parts["locality/political"]
        return addr
    return None

class GMapper(object):

    def __init__(self, key):
        self._client = googlemaps.Client(key=key)

    def lookup(self, location):
        if 2 == len(location):
            result = self._client.reverse_geocode(location)[0]
        else:
            result = self._client.geocode(location)[0]
        return result

    def _coords_from_result(self, result):
        gps = result["geometry"]["location"]
        coords = (gps["lat"], gps["lng"])
        return coords

    def _address_from_result(self, result):
        return canonical_address_from_result(result)

    def address_from_coords(self, coords):
        result = self._client.reverse_geocode(coords)[0]
        return self._address_from_result(result)

    def coords_from_address(self, address):
        result = self._client.geocode(address)[0]
        return self._coords_from_result(result)

    def coords_and_address(self, location):
        result = self.lookup(location)
        return self._coords_from_result(result), self._address_from_result(result)

    def place_at_location(self, location, radius_m=50):
        coords, address = self.coords_and_address(location)
        places_result = self._client.places_nearby(location=coords, radius=radius_m)["results"]
        for place in places_result:
            place_addr = canonical_address_from_result(place)
            if place_addr == canonical_addr:
                return place

    def business_summary(self, location):
        place = self.place_at_location(location)
        if place:
            try:
                return "Name: {}, Type: {}".format(place.get("name","<name unknown>"), ", ".join(place.get("types", ["unknown"])))
            except:
                return "UNKNOWN"
        return None

    def find_random_house(self, coords, radius_km=1, attempts=10, retry_sleep=0.5, throw_on_failure=True):
        ne_pt, sw_pt = bounds(coords, radius_km)
        lat_range = (min(ne_pt[0], sw_pt[0]), max(ne_pt[0], sw_pt[0]))
        lon_range = (min(ne_pt[1], sw_pt[1]), max(ne_pt[1], sw_pt[1]))
        for i in range(attempts):
            new_coords = (urand(*lat_range), urand(*lon_range))
            result = self.lookup(new_coords)
            addr_coords = self._coords_from_result(result)
            new_address = self._address_from_result(result)
            address_point_distance = haversine(new_coords, addr_coords)
            if result["geometry"]["location_type"] == "ROOFTOP" and address_point_distance < .05:
                # Isn't obviously not a house or other dwelling.
                if self.business_summary(new_address):
                    # Likely a business.  Small chance it's a business run out of a home, but it's tough to avoid that without a zoning API.
                    pass
                else:
                    return result
            if retry_sleep > 0:
                time.sleep(retry_sleep)
        if throw_on_failure:
            raise RuntimeError("Unable to find random house near the given location.")
        return None
