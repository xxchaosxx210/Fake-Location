__title__ = "Fake Location"
__author__ = "Paul Millar"
__version__ = "0.1"
__description__ = "A Fake GPS app for android"

from kivymd.app import MDApp
from kivy.logger import Logger
from kivy.clock import mainthread
from kivy.utils import platform
from kivymd.toast import toast
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

from mockmapview import MockMapView

import time
import random

is_android = platform == "android"

# If android then load the Android classes
if is_android:
    from location import get_location_manager
    from location import GPSListener
    from location import require_location_permissions
    from location import MockLocation
    from location import get_system_location


def _getlatlng(location_manager):
    latlng = None
    if is_android:
        location = get_system_location(location_manager)
        if location:
            latlng = (location.getLatitude(), location.getLongitude())
    else:
        # generate random latitude and longitude coordinates
        latlng = (random.uniform(-90, 90), random.uniform(-180, 180))
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
            self._update.start()

    @mainthread
    def on_gps_update(self, provider, event, *args):
        """
        on_gps_update(str, str, tuple)
        Callback function for handling messages sent from
        Mock Locations thread and gps update listener.
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
                    self.root.mockmapview.setdefault(*latlng)
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
            latlng = get_system_location(self._location_manager)
            if latlng:
                self.root.mockmapview.setdefault(*latlng)
            else:
                toast("Could not find your location. Try turning Location on in settings")
        else:
            # generate random latitude and longitude coordinates
            latlng = _getlatlng(None)
            self.root.mockmapview.setdefault(*latlng)
    
    def on_start_mock(self):
        """
        Start button is pressed
        """
        if is_android:
            # get the latitude coordinates from mockmapview and send them
            # to mock location thread
            self._update.send_message("start", 
                self.root.mockmapview.lat,
                self.root.mockmapview.lon)
    
    def on_stop_mock(self):
        """
        Stop button is pressed
        """
        if is_android:
            self._update.send_message("stop")

def main():
    MainApp().run()

if __name__ == '__main__':
    main()