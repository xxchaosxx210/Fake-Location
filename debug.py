import random

# Debugging
MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180

class Debug:

    # Global coordinates of current location
    latitude = random.uniform(MIN_LATITUDE, MAX_LATITUDE)
    longitude = random.uniform(MIN_LONGITUDE, MAX_LONGITUDE)

    @staticmethod
    def randomize_latlng():
        Debug.latitude = random.uniform(MIN_LATITUDE, MAX_LATITUDE)
        Debug.longitude = random.uniform(MIN_LONGITUDE, MAX_LONGITUDE)