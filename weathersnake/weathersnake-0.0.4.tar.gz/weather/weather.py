import requests
import googlemaps


API_KEY = 'e7d99fbae935d84dafae9ba51bc49270'
DEFAULT_WEATHER_UNITS = 'imperial'
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'


_gmaps = googlemaps.Client(key='AIzaSyByfGh6kuUNv31QHPWj6esmO94NkOQebrM')


def validate_input(location):
    """
    Validate that we are given a location in the form
    <CITY>,<STATE/COUNTRY>
    """
    return len(location.split(',')) is 2


def get_lat_lon(location):
    """
    Given an address, get the lat and lon back
    """
    res = _gmaps.geocode(location)

    if res:
        res = res[0]
        return res.get('geometry')
    return False


def fetch_weather(location, units=None):
    """
    Given a location, return the current temperature in that location
    """

    if validate_input(location):
        geo = get_lat_lon(location)
        if geo:
            payload = {
                'APPID': API_KEY,
                'lat': geo['location']['lat'],
                'lon': geo['location']['lng'],
                'units': units or DEFAULT_WEATHER_UNITS
            }

            resp = requests.get(WEATHER_URL, params=payload)
            return resp.status_code, resp.json()
    return False
