__title__ = "Fake Location"
__author__ = "Paul Millar"
__version__ = "0.1"
__description__ = "A Fake GPS app for android"

from kivymd.app import MDApp
from kivy.logger import Logger
from kivy.clock import mainthread
from kivy.utils import platform

import time

is_android = platform == "android"

# If android then load the Android classes
if is_android:
    from location import Gps
    from location import require_location_permissions
    from kivy.clock import Clock

class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
    
    def on_stop(self):
        if is_android:
            self.gps.stop_gps_updates()
            #self.gps.stop_mock_provider()
            #self.gps.start_mock_provider()
    
    def on_start(self):
        if is_android:
            require_location_permissions(self.on_gps_update)
            self.gps = Gps(self.on_gps_update)
            
    @mainthread
    def on_gps_update(self, provider, event, *args):
        """
        any changes to location provider will be sent here
        """    
        if event == 'permissions-result':
            print(args[0])
            print(type(args[0]))
            if args[0] == True:
                # setup locations
                self.gps.init_mock_provider()
                self.gps.start_gps_updates(3, 10)
                Logger.info("APP: Location Permission requests have been accepted")
            else:
                Logger.info("APP: Location Permission requests have been rejected")
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
            loc = self.gps_location.get_location()
            if loc:
                self.add_status(f"\n {loc.getLatitude()}, lng = {loc.getLongitude()}")
    
    def on_start_mock(self, lat, lng):
        if is_android:
            self.gps.stop_mock_provider()
            self.gps.start_mock_provider()
            self.gps.set_mock_location(lat, lng)
    
    def on_stop_mock(self):
        if is_android:
            self.gps.stop_mock_provider()
            self.gps.start_mock_provider()
    
    def add_status(self, textline):
        self.root.ids["mock_status"].text += f"\n {textline}"



def main():
    MainApp().run()

if __name__ == '__main__':
    main()