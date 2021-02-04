import random
import time
import json
import os
from collections import namedtuple
from kivy.logger import Logger
import global_props

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
                            "UK", "SW1", "Test By Test Test Test Long Address", "23",
                            51.458120868483164,
                            -0.1288632693726255), 
                            range(random.randrange(1, 20)))
        return addresses
    
    @staticmethod
    def log_object(obj):
        for item in dir(obj):
            print(item)
    
    @staticmethod
    def log(event_type="APP", obj=None, **kwargs):
        """
        place key value pairs
        """
        text = f"{event_type}: "
        for key, value in kwargs.items():
            text += f"{key}={value}, "
        if len(text) >= 2:
            Logger.info(text[:-2])
    
    @staticmethod
    def log_file(event, function_name, message):
        """
        log_file(str, str, str)
            saves a log message to the log file on disk
        """

        global_props.check_path_exists()
        logs = ""
        if os.path.exists(global_props.LOG_PATH):
            stat = os.stat(global_props.LOG_PATH)
            if stat.st_size <= 1000000:
                # if logs is less than 1MB then load
                with open(global_props.LOG_PATH, "r") as fp:
                    logs = fp.read()
        current_time = time.ctime(time.time())
        logs += f"\n[{current_time}]:{function_name}:{message}"
        global_props.save(global_props.LOG_PATH, logs)
    
    @staticmethod
    def getlogfromfile():
        return global_props.load(global_props.LOG_PATH)
        


        