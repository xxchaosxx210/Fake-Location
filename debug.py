import random
from collections import namedtuple

# Debugging
MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180

_GeoAddress = namedtuple("Address", ["city", "county", "country",
                                     "postcode", "second_address",
                                     "house_number", "latitude",
                                     "longitude"])

class Debug:

    # Global coordinates of current location
    latitude = random.uniform(MIN_LATITUDE, MAX_LATITUDE)
    longitude = random.uniform(MIN_LONGITUDE, MAX_LONGITUDE)

    @staticmethod
    def randomize_latlng():
        Debug.latitude = random.uniform(MIN_LATITUDE, MAX_LATITUDE)
        Debug.longitude = random.uniform(MIN_LONGITUDE, MAX_LONGITUDE)
    
    @staticmethod
    def get_geo_address(address, max_range):
        addresses = map(lambda index: _GeoAddress(
                            "London", "Essex", 
                            "UK", "SW1", "Test Street", "23",
                            51.458120868483164,
                            -0.1288632693726255), 
                            range(random.randrange(1, 20)))
        return addresses
    
    @staticmethod
    def log_object(obj):
        for item in dir(obj):
            print(item)