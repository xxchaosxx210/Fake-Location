__version__ = '0.1'
__author__ = 'Paul Millar'
__description__ = """

location.py
-----------

Contains functions and classes for dealing with Androids Location API
 Features include:

 GPSListener - A class for retrieving GPS location data
 Functions for performing tests ie. Mock Locations on device

 Note: I can't for the love of me get this to work on SDK 29 and above

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

# reflect our Android classes from the Android SDK

LocationManager = autoclass("android.location.LocationManager")
Location = autoclass("android.location.Location")
Looper = autoclass("android.os.Looper")
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = autoclass("android.content.Context")
System = autoclass("java.lang.System")
SystemClock = autoclass("android.os.SystemClock")

# Nested class requires $
VERSION = autoclass("android.os.Build$VERSION")
VERSION_CODES = autoclass("android.os.Build$VERSION_CODES")

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
    
    def get_location(self):
        """
        returns Location object or None if no GPS availible
        """
        return self._location_manager.getLastKnownLocation(LocationManager.GPS_PROVIDER)
    
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


def get_location_manager():
    """
    returns a LocationManager object from Android system
    """
    return PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE)

def startup_testprovider(location_manager, provider_name):
    """
    adds test provider for testing
    """
    try:
        location_manager.addTestProvider(
            provider_name,
            True,
            True,
            False,
            False,
            False,
            True,
            True,
            0,
            5)
        return True
    except Exception as err:
        print(f"Error: {err}")
        return False

def remove_test_provider(location_manager, provider_name):
    try:
        location_manager.removeTestProvider(provider_name)
        return True
    except Exception as err:
        print(f"Error: {err}")
        return False

def set_provider_enabled(location_manager, provider_name, enabled):
    try:
        location_manager.setTestProviderEnabled(provider_name, enabled)
        return True
    except Exception as err:
        print(f"Error: {err}")
        return  False

def set_provider_location(location_manager, provider_name, latitude, longitude):
    """
    set the fake latitude and longitude coordinates
    """
    location = Location(provider_name)
    location.setAltitude(1)
    location.setTime(System.currentTimeMillis())
    location.setLatitude(latitude)
    location.setLongitude(longitude)
    location.setAccuracy(5)
    if VERSION.SDK_INT >= VERSION_CODES.JELLY_BEAN_MR1:
        location.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos())
    try:
        location_manager.setTestProviderLocation(provider_name, location)
        return True
    except Exception as err:
        print(f"Error: {err}")
        return False


class MockLocation(threading.Thread):

    def __init__(self, location_manager, callback):
        super().__init__()
        self._callback = callback
        self.queue = queue.Queue()
        self.location_manager = location_manager
    
    def run(self):
        stop_mock = True
        latitude = 51.2323
        longitude = 1.23433
        while 1:
            try:
                s = self.queue.get(timeout=1)
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
    
    def dispatch_message(self, event, *args):
        self._callback(self, event, args)


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
        new_loc = Location(provider)
    except Exception as err:
        print(f"SET_MOCK: {err}")

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