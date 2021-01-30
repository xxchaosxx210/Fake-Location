__version__ = '0.1'
__author__ = 'Paul Millar'
__description__ = """

location.py
-----------

Contains functions and classes for dealing with Androids Location API
 Features include:

 GPSListener - A class for retrieving GPS location data

In order to get location updates- call start_gps_updates
if just want location right away the call get_location
"""

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
    return PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE)

def startup_testprovider(location_manager, provider_name):
    location_manager.addTestProvider(
        provider_name,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        0,
        1)

def set_provider_location(location_manager, provider_name, latitude, longitude):
    location = Location(provider_name)
    location.setAltitude(1)
    location.setTime(System.currentTimeMillis())
    location.setLatitude(latitude)
    location.setLongitude(longitude)
    location.setAccuracy(1)
    if VERSION.SDK_INT >= VERSION_CODES.JELLY_BEAN_MR1:
        location.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos())
    try:
        location_manager.setTestProviderLocation(provider_name, location)
    except Exception as err:
        print(f"ERROR: {err}")


class GpsManager:

    def __init__(self, func_callback):
        self._location_manager = PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE)
        self.provider_name = LocationManager.GPS_PROVIDER
        self._func_callback = func_callback
        self.gps_listener = _GPSListener(self._func_callback)
    
    def init_mock_provider(self):
        if not self._location_manager.getProvider(self.provider_name):
            print(f"{self.provider_name} was no found add provider")
            print("No Test Provider Found adding Test Provider")
            self._location_manager.addTestProvider(
                self.provider_name,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                0,
                1
            )
            self.start_mock_provider()
            return False
        else:
            print("Founc test provider no need to add")
            return True
    
    def remove_mock_provider(self):
        self._location_manager.removeTestProvider(self.provider_name)
    
    def set_mock_location(self, latitude, longitude):
        array = self._location_manager.getProviders(True).toArray()
        for item in array:
            print(f"Provider: {item}")
        print(f"Array[1] = {array[1]}")
        loc = Location(self.provider_name)
        loc.setAltitude(1)
        loc.setTime(System.currentTimeMillis())
        loc.setAccuracy(1)
        loc.setLatitude(latitude)
        loc.setLongitude(longitude)
        if VERSION.SDK_INT >= VERSION_CODES.JELLY_BEAN_MR1:
            loc.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos())
        try:
            self._location_manager.setTestProviderLocation(array[1], loc)
        except Exception as err:
            print(f"ERROR: {err}")

    def start_mock_provider(self):
        try:
            self._location_manager.setTestProviderEnabled(self.provider_name, True)
        except Exception:
            self.init_mock_provider()

    def stop_mock_provider(self):
        pass#self._location_manager.setTestProviderEnabled(self.provider_name, False)
    