import time
import requests


BASE_URL= 'https://maps.googleapis.com/maps/api/place/textsearch/json?'
PLACES_URL = 'https://maps.googleapis.com/maps/api/place/details/json?'


class PlacesRequest:
    """
    Represents a request to the Google Places API
    """
    def __init__(self, query, key):
        self.query = query
        self.key = key
        self.url = BASE_URL + f'query={self.query}&key={self.key}'
        self.response = None
        self.token = None
        self.results = []
    
    def fetch_results(self):
        self.response = self.request(self.url)
        self.token = self.response.next_page_token
        self.results.append(self.response)

        while self.next_token_exists():
            time.sleep(2)
            self.response = self.fetch_next_page(self.response.next_page_token)
            self.token = self.response.next_page_token
            self.results.append(self.response)
        return self.results
    
    def fetch_next_page(self, token):
        url = BASE_URL + f'pagetoken={token}&key={self.key}'
        return self.request(url)
    
    def request(self, url):
        response = requests.get(url)
        return PlacesSearchResult(response, self.key)
    
    def next_token_exists(self):
        return bool(self.token)

    def __repr__(self):
        return f'<PlacesRequest query: {self.query}>'        


class PlacesSearchResult:
    """
    Represents a search result from the Google Places API
    """
    def __init__(self, response, key):
        self.key = key
        self.response = response
        self.results = response.json()
    
    @property
    def status_code(self):
        return self.response.status_code
    
    @property
    def status_text(self):
        return self.results.get('status')
    
    @property
    def next_page_token(self):
        return self.results.get('next_page_token')
    
    @property
    def places(self):
        return [Place(result, self.key) for result in self.results['results']]
    
    def __repr__(self):
        return f'<PlacesRequestResult status: {self.status_code}>'
    

class Place:
    """
    Represents a Place from Google Places API
    """
    def __init__(self, place, key):
        self.place = place
        self.key = key
        self.place_id = self.place.get('place_id')        
        self.url = PLACES_URL + f'placeid={self.place_id}&key={self.key}'
        self.details = self._request_details()
    
    def _request_details(self):
        response = requests.get(self.url)
        details = response.json()
        return details['result']
    
    @property
    def name(self):
        return self.place.get('name')
    
    @property
    def geo_location(self):
        return self.place['geometry']['location']
    
    @property
    def rating(self):
        if 'rating' in self.place:
            return self.place.get('rating')
    
    @property
    def icon(self):
        return self.place.get('icon')
    
    @property
    def is_open_now(self):
        if 'opening_hours' in self.details:
            return self.details['opening_hours']['open_now']

    @property
    def vicinity(self):
        return self.place.get('vicinity')
    
    @property
    def address(self):
        return self.place.get('formatted_address')
    
    @property
    def website(self):
        if 'website' in self.details:
            return self.details.get('website')
    
    @property
    def phone_number(self):
        return self.details.get('formatted_phone_number')
    
    @property
    def reviews(self):
        return self.details.get('reviews')
    
    def __repr__(self):
        return f'<Place name="{self.name}">'
