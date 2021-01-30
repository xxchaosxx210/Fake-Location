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

class Gps(PythonJavaClass):

    __javainterfaces__ = ["android/location/LocationListener"]

    def __init__(self, func_callback):
        self._location_manager = PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE)
        self.provider_name = LocationManager.GPS_PROVIDER
        self._func_callback = func_callback
    
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
        else:
            print(f"{self.provider_name} was found")
    
    def remove_mock_provider(self):
        self._location_manager.removeTestProvider(self.provider_name)
    
    def set_mock_location(self, latitude, longitude):
        mockloc = Location(self.provider_name)
        mockloc.setTime(System.currentTimeMillis())
        mockloc.setAccuracy(1)
        mockloc.setLatitude(latitude)
        mockloc.setLongitude(longitude)
        if VERSION.SDK_INT >= 17:
            mockloc.setElapsedRealtimeNanos(
                SystemClock.elapsedRealtimeNanos())
        self._location_manager.setTestProviderLocation(
            self.provider_name,  mockloc)
    
    def start_mock_provider(self):
        for provider in self._location_manager.getProviders(False).toArray():
            print(provider)
        try:
            self._location_manager.setTestProviderEnabled(self.provider_name, True)
        except Exception:
            pass

    def stop_mock_provider(self):
        for provider in self._location_manager.getProviders(True).toArray():
            print(provider)
        try:
            self._location_manager.setTestProviderEnabled(self.provider_name, False)
        except Exception:
            pass
        
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
    