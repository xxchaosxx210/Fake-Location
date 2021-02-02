__version__ = '0.2'
__author__ = 'Paul Millar'
__description__ = """

location.py
-----------

Contains functions and classes for dealing with Androids Location API
 Features include:

 GPSListener - A class for retrieving GPS location data
 Functions for performing tests ie. Mock Locations on device

In order to get location updates- call start_gps_updates
if just want location right away then call get_location
"""
import threading
import queue
import json

from jnius import autoclass
from jnius import PythonJavaClass
from jnius import java_method

# android request classess
from android.permissions import request_permissions
from android.permissions import Permission

from collections import namedtuple

# reflect our Android classes from the Android SDK

LocationManager = autoclass("android.location.LocationManager")
Location = autoclass("android.location.Location")
Looper = autoclass("android.os.Looper")
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = autoclass("android.content.Context")
System = autoclass("java.lang.System")
SystemClock = autoclass("android.os.SystemClock")
Geocoder = autoclass("android.location.Geocoder")
Locale = autoclass("java.util.Locale")

# Nested class requires $
VERSION = autoclass("android.os.Build$VERSION")
VERSION_CODES = autoclass("android.os.Build$VERSION_CODES")

_GeoAddress = namedtuple("Address", ["city", "county", "country",
                                     "postcode", "second_address",
                                     "house_number", "latitude",
                                     "longitude"])

def get_geo_location(address, max_result):
    """
    get_geo_location(str, int)
    address to look up, max_results are maximum results returned from look up
    returns a List of GeoAddress namedtuples on success
    each GeoAddress contains
    city
    county
    country
    postcode
    second_address
    house_number
    latitude
    longitude
    """
    if Geocoder.isPresent():
        print("GeoCoder is present...")
        geo = Geocoder(PythonActivity.mActivity, Locale.getDefault())
        print("Looked up addresses")
        java_list = geo.getFromLocationName(address, max_result)
        if java_list:
            print("List found...")
            addresses = []
            for addr in java_list.toArray():
                addresses.append(_GeoAddress(
                    city=str(addr.getLocality()),
                    county=str(addr.getSubAdminArea()),
                    country=str(addr.getAdminArea()),
                    postcode=str(addr.getPostalCode()),
                    second_address=str(addr.getThoroughfare()),
                    house_number=str(addr.getSubThoroughfare()),
                    latitude=addr.getLatitude(),
                    longitude=addr.getLongitude()
                ))
            return addresses
        else:
            print("No list found...")
    else:
        print("No GeCoder present")
    return []

def require_location_permissions(func_callback):
    """
    get the request results call callback
    def func_callback(obj, event, *args)
    """
    def on_request_result(permissions, grant_results):
        access_fine_ok = False
        access_coarse_ok = False
        for index, permission in enumerate(permissions):
            if permission == Permission.ACCESS_FINE_LOCATION:
                access_fine_ok = grant_results[index]
            if permission == Permission.ACCESS_COARSE_LOCATION:
                access_coarse_ok = grant_results[index]
        if access_coarse_ok == True and access_fine_ok == True:
            func_callback(None, "permissions-result", True)
        else:
            func_callback(None, "permissions-result", False)
    if VERSION.SDK_INT >= 23:
        request_permissions(
            [Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION], on_request_result)


class GPSListener(PythonJavaClass):

    """
    sets up a callback listener for location updates and changes to providers
    """

    __javainterfaces__ = ["android/location/LocationListener"]

    def __init__(self, location_manager, func_callback):
        self._func_callback = func_callback
        self._location_manager = location_manager
    
    def start_gps_updates(self, time_interval, min_dist):
        """
        time_interval - int
            minimum time interval between location updates in milliseconds
        min_dist - float
            minimum distance between location updates in meters
        """
        self._location_manager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            time_interval,
            min_dist,
            self,
            Looper.getMainLooper()
        )
    
    def stop_gps_updates(self):
        """
        stop listening for GPS updates
        """
        self._location_manager.removeUpdates(self)
    
    @java_method('()I')
    def hashCode(self):
        """
        should be return id(self) but gives int to large for C long type
        error. return 1 instead
        """
        return 1
    
    @java_method('(Landroid/location/Location;)V')
    def onLocationChanged(self, location):
        self._func_callback(self, "location", location)
    
    @java_method('(Ljava/lang/String;)V')
    def onProviderEnabled(self, provider):
        self._func_callback(self, "provider_enabled", provider)
    
    @java_method('(Ljava/lang/String;)V')
    def onProviderDisabled(self, provider):
        self._func_callback(self, "provider_disabled", provider)
    
    @java_method('(Ljava/lang/Object;)Z')
    def equals(self, obj):
        return obj.hashCode() == self.hashCode()


def get_system_location(location_manager):
    """
    get_system_location(object)
    trys to get best last known location from GPS_PROVIDER and GPS_NETWORK
    returns None if unsuccesful else returns Location object
    """
    location = location_manager.getLastKnownLocation(LocationManager.GPS_PROVIDER)
    if not location:
        location = location_manager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)
    return location

def get_location(location_manager, provider):
    """
    get_location(object, str)
    returns a LocationManager object. provider can be any provider name.
    Example of system wide providers - LocationManager.GPS_PROVIDER or LocationManager.NETWORK_PROVIDER
    """
    return location_manager.getLastKnownLocation(provider)

def get_location_manager():
    """
    get_location_manager()
    returns a LocationManager object from Android system
    """
    return PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE)


class MockLocation(threading.Thread):

    """
    Mock Locations needs to be constantly updated in order to bypass Google Maps and other Apps
    This thread handles requests
    call send_message to send events to thread
    event - stop, stop, quit
    args -
        if event is start then args = (float, float) - latitude and longitude values
        stop: - stop mock locations
        quit: - quit the thread
    """

    THREAD_TIMEOUT = 1 # Thread loop. Seconds

    def __init__(self, location_manager):
        """
        location_manager - LocationManager (call get_location_manager -> location_manager)
        """
        super().__init__()
        self.queue = queue.Queue()
        self.location_manager = location_manager
    
    def run(self):
        """
        sets mock location when start message sent
        send quit to obviously quit the loop
        """
        stop_mock = True
        latitude = 51.2323
        longitude = 1.23433
        while 1:
            try:
                s = self.queue.get(timeout=MockLocation.THREAD_TIMEOUT)
                msg = json.loads(s)
                event = msg["event"]
                if event == "stop":
                    stop_mock = True
                    stop_mock_updates(self.location_manager)
                elif event == "start":
                    stop_mock = False
                    args = msg["args"]
                    latitude = args[0]
                    longitude = args[1]
                elif event == "quit":
                    stop_mock_updates(self.location_manager)
                    break
            except queue.Empty:
                pass
            if not stop_mock:
                set_mock(self.location_manager, LocationManager.GPS_PROVIDER, latitude, longitude)
                set_mock(self.location_manager, LocationManager.NETWORK_PROVIDER, latitude, longitude)

    def send_message(self, event, *args):
        s = json.dumps({"event": event, "args": args})
        self.queue.put_nowait(s)


def stop_mock_updates(location_manager):
    try:
        location_manager.removeTestProvider(LocationManager.GPS_PROVIDER)
    except Exception as err:
        print(f"STOP_MOCK_UPDATES: {err}")
    try:
        location_manager.removeTestProvider(LocationManager.NETWORK_PROVIDER)
    except Exception as err:
        print(f"STOP_MOCK_UPDATES: {err}")

def set_mock(location_manager, provider, lat, lng):
    """
    set_mock(object, str, float, float)
        location_manager is a LocationManager object obtained from get_location_manager()

        provider is a string constant and can be LocationManager.GPS_PROVIDER or LocationManager.NETWORK_PROVIDER
            for system wide location testing. For app specific use a custom naming string
        
    """
    try:
        location_manager.addTestProvider(
            provider,
            False,
            False,
            False,
            False,
            False,
            True,
            True,
            0,
            5)
    except Exception as err:
        print(f"SET_MOCK: {err}")

    new_loc = Location(provider)
    new_loc.setLatitude(lat)
    new_loc.setLongitude(lng)
    new_loc.setAccuracy(1.0)
    new_loc.setTime(System.currentTimeMillis())
    new_loc.setSpeed(0.0)
    new_loc.setBearing(1.0)
    new_loc.setAltitude(3.0)
    if VERSION.SDK_INT >= VERSION_CODES.JELLY_BEAN_MR1:
        new_loc.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos())
    if VERSION.SDK_INT >= VERSION_CODES.O:
        new_loc.setBearingAccuracyDegrees(0.1)
        new_loc.setVerticalAccuracyMeters(0.1)
        new_loc.setSpeedAccuracyMetersPerSecond(0.0)
    
    try:
        location_manager.setTestProviderEnabled(provider, True)
    except Exception as err:
        print(f"SET_MOCK: {err}")
    try:
        location_manager.setTestProviderLocation(provider, new_loc)
    except Exception as err:
        print(f"SET_MOCK: {err}")