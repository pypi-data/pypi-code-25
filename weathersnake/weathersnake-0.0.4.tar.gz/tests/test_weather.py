import unittest
import responses
import weather

from mock import patch


API_KEY = 'e7d99fbae935d84dafae9ba51bc49270'
DEFAULT_WEATHER_UNITS = 'imperial'
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'


class TestWeatherAPI(unittest.TestCase):

    def test_validate_input(self):
        """
        Given a location string, validate that the
        input is in the form of <CITY>,<STATE/COUNTRY>
        """
        self.assertTrue(weather.validate_input('Des Moines, IA'))
        self.assertFalse(weather.validate_input('Des Moines'))
        self.assertFalse(weather.validate_input(''))
        self.assertFalse(weather.validate_input('Des Moines, IA, FOO'))

    @patch('weather.weather.googlemaps.Client.geocode')
    def test_get_lat_lon(self, mock_goog):
        """
        Assert that the geocode library is called with
        the expected input
        """
        weather.get_lat_lon('location')
        mock_goog.assert_called_once_with('location')

    @patch('weather.weather.googlemaps.Client.geocode')
    def test_get_lat_lon_bad_location(self, mock_goog):
        """
        Given a location that is not real, return false
        """
        mock_goog.return_value = []

        res = weather.get_lat_lon('fake_location')
        mock_goog.assert_called_once_with('fake_location')
        self.assertFalse(res)

    def test_fetch_weather_invalid_input(self):
        """
        Given an invalid input, assert that we get a
        false return value
        """
        self.assertFalse(weather.fetch_weather(''))
        self.assertFalse(weather.fetch_weather('FOO BAR'))
        self.assertFalse(weather.fetch_weather('FOO, BAR, BAZ'))

    @responses.activate
    @patch('weather.weather.googlemaps.Client.geocode')
    def test_fetch_weather(self, mock_goog):
        """
        Given a valid location return both a response code and
        a JSON blob
        """
        mock_goog.return_value = [{
            "geometry": {
                "location": {
                    "lat": 38.8910644,
                    "lng": -77.032614
                }
            }
        }]

        url = WEATHER_URL + "?lat={}&lon={}&APPID={}&units={}".format(
            38.8910644,
            -77.032614,
            API_KEY,
            'imperial'
        )

        responses.add(
            responses.GET,
            url,
            status=200,
            body={}
        )

        res = weather.fetch_weather('Des Moines, IA')
        self.assertEqual(res[0], 200)
        self.assertEqual(res[1], {})

    @patch('weather.weather.googlemaps.Client.geocode')
    def test_fetch_weather_bad_location(self, mock_goog):
        """
        Given an invalid location, get a False response
        """
        mock_goog.return_value = []

        res = weather.fetch_weather('Fake City, Fake State')

        mock_goog.assert_called_once_with('Fake City, Fake State')
        self.assertFalse(res)
