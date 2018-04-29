import json

from functools import lru_cache
from random import uniform

from shapely.geometry import MultiPolygon, Point, shape


@lru_cache(maxsize=None)
def get_land_polygons():
    """Read MultiPolygon for land."""
    with open('./land-polygons.geojson', 'r') as fp:
        data = json.load(fp)
        land = MultiPolygon(
            shape(feature['geometry'])
            for feature in data['features']
            if feature['geometry']['type'] == 'Polygon'
        )
    return land


def generate_land_coordinates():
    """Generate a point on land."""
    land = get_land_polygons()
    ntry = 0
    while 1:
        latitude = uniform(-56, 78)  # because of land bounds
        longitude = uniform(-180, 180)
        ntry += 1
        if land.contains(Point(longitude, latitude)):
            break
        if ntry == 100:
            raise
    return {
        'latitude': latitude,
        'longitude': longitude,
    }
