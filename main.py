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
    from location import GpsTesting
    from location import GpsListener
    from location import require_location_permissions

class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
    
    def on_stop(self):
        self.provider.remove_test_provider()
    
    def on_start(self):
        if is_android:
            require_location_permissions(self.on_gps_update)
            
    @mainthread
    def on_gps_update(self, provider, event, *args):
        """
        any changes to location provider will be sent here
        """    
        if event == 'permissions-result':
            print(args[0])
            print(type(args[0]))
            if args[0] == True:
                #self.provider.enable_mock_locations()
                Logger.info("APP: Location Permission requests have been accepted")
            else:
                Logger.info("APP: Location Permission requests have been rejected")
    
    def on_get_location(self):
        if is_android:
            loc = self.provider.get_location()
            if loc:
                self.root.ids["mock_status"].text += f"\n lat = {loc.getLatitude()}, lng = {loc.getLongitude()}"
    
    def on_start_fake_location(self):
        self.provider.set_mock_location(51.507351, -0.127758, 0)

    def on_stop_fake_location(self):
        self.provider.disable_mock_locations()



def main():
    MainApp().run()

if __name__ == '__main__':
    main()