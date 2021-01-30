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
Criteria = autoclass("android.location.Criteria")

# Nested class requires $
VERSION = autoclass("android.os.Build$VERSION")


class GpsManager(PythonJavaClass):

    __javainterfaces__ = ["android/location/LocationListener"]

    def __init__(self, func_callback, **kwargs):
        """
        func_callback(GpsListener, event, object)
        """
        print(f"API Version: {VERSION.SDK_INT}")
        super().__init__(**kwargs)
        self.func_callback = func_callback
        self.location_manager = PythonActivity.mActivity.getSystemService(
            Context.LOCATION_SERVICE
        )
        # Get Permission Request to start using GPSlistener
        if VERSION.SDK_INT >= 23:
            request_permissions(
                [Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION], 
                self.on_request_result
            )
        criteria = Criteria()
        criteria.setAccuracy(Criteria.ACCURACY_FINE)
        self.best_provider = "test"#self.location_manager.getBestProvider(criteria, True)
        if not self.best_provider:
            print("No best provider found")
        else:
            print(f"Best Provider {self.best_provider}")
    
    def enable_mock_locations(self):
        self.location_manager.addTestProvider(
            self.best_provider, 
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            0,
            5
        )
        self.location_manager.setTestProviderEnabled(
            self.best_provider, True
        )
    
    def disable_mock_locations(self):
        self.location_manager.setTestProviderEnabled(
            self.best_provider, False
        )
    
    def remove_test_provider(self):
        self.location_manager.removeTestProvider(self.best_provider)
    
    def set_mock_location(self, latitude, longitude, altitude):
        loc = Location(self.best_provider)
        loc.setLatitude(latitude)
        loc.setLongitude(longitude)
        loc.setAltitude(altitude)
        loc.setTime(System.currentTimeMillis())
        self.location_manager.setTestProviderLocation(
            self.best_provider,
            loc
        )
    
    def on_request_result(self, permissions, grant_results):
        """
        get the request results
        """
        access_fine_ok = False
        access_coarse_ok = False
        for index, permission in enumerate(permissions):
            if permission == Permission.ACCESS_FINE_LOCATION:
                access_fine_ok = grant_results[index]
            if permission == Permission.ACCESS_COARSE_LOCATION:
                access_coarse_ok = grant_results[index]
        if access_coarse_ok == True and access_fine_ok == True:
            self.func_callback(self, "permissions-result", True)
        else:
            self.func_callback(self, "permissions-result", False)
    
    def start_gps_updates(self, time_interval, min_dist):
        """
        time_interval - int
            minimum time interval between location updates in milliseconds
        min_dist - float
            minimum distance between location updates in meters
        """
        self.location_manager.requestLocationUpdates(
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
        self.location_manager.removeUpdates(self)
    
    def get_location(self):
        """
        returns Location object or None if no GPS availible
        """
        return self.location_manager.getLastKnownLocation(LocationManager.GPS_PROVIDER)
    
    @java_method('()I')
    def hashCode(self):
        """
        should be return id(self) but gives int to large for C long type
        error. return 1 instead
        """
        return 1
    
    @java_method('(Landroid/location/Location;)V')
    def onLocationChanged(self, location):
        self.func_callback(self, "location", location)
    
    @java_method('(Ljava/lang/String;)V')
    def onProviderEnabled(self, provider):
        self.func_callback(self, "provider_disabled", provider)
    
    @java_method('(Ljava/lang/String;)V')
    def onProviderDisabled(self, provider):
        self.func_callback(self, "provider_disabled", provider)
    
    @java_method('(Ljava/lang/Object;)Z')
    def equals(self, obj):
        return obj.hashCode() == self.hashCode()