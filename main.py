__title__ = "Fake Location"
__author__ = "Paul Millar"
__version__ = "0.1"
__description__ = "A Fake GPS app for android"

from kivymd.app import MDApp
from kivy.logger import Logger
from kivy.clock import mainthread
from kivy.utils import platform
from kivymd.toast import toast

import time

is_android = platform == "android"

# If android then load the Android classes
if is_android:
    from location import get_location_manager
    from location import startup_testprovider
    from location import set_provider_location
    from location import remove_test_provider
    from location import set_provider_enabled
    from location import GPSListener
    from location import LocationManager
    from location import require_location_permissions
    from location import MockLocation

class MainApp(MDApp):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        if is_android:
            # Get LocationManager from Android API
            self._location_manager = get_location_manager()
            self._update = MockLocation(self.on_gps_update)
    
    def on_stop(self):
        if is_android:
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
        any changes to location provider will be sent here
        """    
        if event == 'permissions-result':
            if args[0] == True:
                # Permission accepted start the LocationListener update
                self.gps_listener.start_gps_updates(3, 10)
            else:
                toast("Request to use Locations rejected. Please enable Locations in App Permissions")
        elif event == "location":
            loc = args[0]
            self.add_status(f"Latitude: {loc.getLatitude()}, Longitutde: {loc.getLongitude()}")
        elif event == "provider_enabled":
            prov = args[0]
            self.add_status(f"{prov} Provider enabled")
        elif event == "provider_disabled":
            prov = args[0]
            self.add_status(f"{prov} Provider disabled")
    
    def on_get_location(self):
        if is_android:
            loc = self.gps_listener.get_location()
            if loc:
                self.add_status(f"\n {loc.getLatitude()}, lng = {loc.getLongitude()}")
    
    def on_start_mock(self, lat, lng):
        if is_android:
            latitude = float(self.root.ids["latitude"].text)
            longitude = float(self.root.ids["longitude"].text)
            self._update.send_message("start", [latitude, longitude])
    
    def on_stop_mock(self):
        if is_android:
            self._update.send_message("stop")
    
    def add_status(self, textline):
        self.root.ids["mock_status"].text += f"\n {textline}"



def main():
    MainApp().run()

if __name__ == '__main__':
    main()