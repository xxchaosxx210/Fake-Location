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
    from location import GpsManager

class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
    
    def on_stop(self):
        if is_android:
            self.provider.stop_gps_updates()
    
    def on_start(self):
        if is_android:
            self.provider = GpsManager(self.on_gps_update)
            
    @mainthread
    def on_gps_update(self, provider, event, *args):
        """
        any changes to location provider will be sent here
        """
        if event == 'location':
            location = args[0]
            lat = location.getLatitude()
            lng = location.getLongitude()
            if len(self.root.ids["mock_status"].text) > 500:
                self.root.ids["mock_status"].text = ""
            self.root.ids["mock_status"].text += f"\n Lat: {lat}, Lng: {lng}"
        
        elif event == 'permissions-result':
            print(args[0])
            print(type(args[0]))
            if args[0] == True:
                self.provider.start_gps_updates(3000, 10)
            else:
                Logger.info("APP: ACCESS_FINE_LOCATION has been rejected")
    
    def on_get_location(self):
        if is_android:
            loc = self.provider.get_location()
            print(f"lat = {loc.getLatitude()}, lng = {loc.getLongitude()}")
            

def main():
    MainApp().run()

if __name__ == '__main__':
    main()