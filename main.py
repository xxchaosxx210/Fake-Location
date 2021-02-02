__title__ = "Fake Location"
__author__ = "Paul Millar"
__version__ = "0.1.1"
__description__ = """
A Fake GPS app for android using the kivy and kivymd framework.
This App will run on Windows and Linux but because they lack
the GPS API the Win and *nix are for testing purposes only

Version 0.1
-----------
laying the framework down. Setting up android testing provider
trying for days to get the mock locations to work on google maps.
the another few days trying to get mapview to work and compile
using buildozer

Version 0.1.1
-------------
Modified the toolbar buttons
"""

from kivymd.app import MDApp
from kivy.logger import Logger
from kivy.clock import mainthread
from kivy.utils import platform
from kivymd.toast import toast
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

from mockmapview import MockMapView

# Debugging
from debug import Debug

is_android = platform == "android"

# If android then load the Android classes
if is_android:
    from location import get_location_manager
    from location import GPSListener
    from location import require_location_permissions
    from location import MockLocation
    from location import get_system_location
    from location import get_geo_location

def _getlatlng(location_manager):
    latlng = None
    if is_android:
        location = get_system_location(location_manager)
        if location:
            latlng = (location.getLatitude(), location.getLongitude())
    else:
        # use the debugging location
        latlng = (Debug.latitude, Debug.longitude)
    return latlng


class Container(MDBoxLayout):
    # Mpaview object
    mockmapview = ObjectProperty(None)
    lat_text = StringProperty("-12.98989")
    lon_text = StringProperty("52.87878")

class MainApp(MDApp):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        if is_android:
            # Get LocationManager from Android API
            self._location_manager = get_location_manager()
            # Mock handler thread for setting mock location and enabling and disabling the mock locations
            self._update = MockLocation(self._location_manager)
        else:
            self._location_manager = None
    
    def on_stop(self):
        if is_android:
            # close thread and gps listener
            self.gps_listener.stop_gps_updates()
            self._update.send_message("quit")
    
    def on_start(self):
        if is_android:
            # Get ACCESS_FINE_LOCATION Permission from user
            require_location_permissions(self.on_gps_update)
            self.gps_listener = GPSListener(self._location_manager, self.on_gps_update)
            # start the mock location thread
            self._update.start()
        else:
            # Set a random location on Windows or Linux
            Debug.randomize_latlng()
            self.root.mockmapview.update_current_locmarker(Debug.latitude, Debug.longitude, False)

    @mainthread
    def on_gps_update(self, provider, event, *args):
        """
        on_gps_update(str, str, tuple)
        Callback function for handling messages sent from
        Mock Locations thread and gps update listener. This method
        is only used on the Android version
        Is also the handler for permission request results.
        event - location, provider-enabled, provider-disabled, permission-result
        location -              args[float, float]
        permission-result -     args[bool]
        """    
        if event == 'permissions-result':
            if args[0] == True:
                # Permission accepted start the LocationListener update
                self.gps_listener.start_gps_updates(3, 10)
                latlng = _getlatlng(self._location_manager)
                if latlng:
                    self.root.mockmapview.update_current_locmarker(latlng[0], latlng[1], False)
                else:
                    toast("Could not find your location. Try turning Location on in settings")
            else:
                toast("Request to use Locations rejected. Please enable Locations in App Permissions")
        elif event == "location":
            loc = args[0]
            Logger.info(f"LOCATION_EVENT: lat={loc.getLatitude()},lng={loc.getLongitude()}")
        elif event == "provider_enabled":
            Logger.info(f"{args[0]}: Enabled")
        elif event == "provider_disabled":
            Logger.info(f"{args[0]}: Disabled")
    
    def on_loc_button_released(self):
        """
        Get Location position is pressed
        """
        if is_android:
            get_geo_location("69 Berners Street NR3", 4)
        latlng = _getlatlng(self._location_manager)
        if latlng:
            self.root.mockmapview.update_current_locmarker(latlng[0], latlng[1], True)
        else:
            toast("Could not find your location. Try turning Location on in settings")
    
    def on_start_mock(self):
        """
        Start button is pressed
        """
        # get the target marker coordinates
        latitude, longitude = self.root.mockmapview.get_last_target_coords()
        if latitude and longitude:
            # if target marker exists then set the mock location
            if is_android:
                # tell mock location thread to set new coordinates
                self._update.send_message("start", latitude, longitude)
            else:
                # set global debugging coordinates
                Debug.latitude = latitude
                Debug.longitude = longitude
                self.root.mockmapview.update_current_locmarker(Debug.latitude, Debug.longitude, False)
        else:
            # Let user know nothing was selected
            toast("Press on the map to select target location and then press the start button")
    
    def on_stop_mock(self):
        """ 
        Stop button is pressed
        """
        if is_android:
            self._update.send_message("stop")
        else:
            # Set a random location on Windows or Linux
            Debug.randomize_latlng()
            self.root.mockmapview.update_current_locmarker(Debug.latitude, Debug.longitude, False)
        self.root.mockmapview.remove_target_marker()

def main():
    MainApp().run()

if __name__ == '__main__':
    main()