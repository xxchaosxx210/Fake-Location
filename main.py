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
    from location import GpsListener
    from android.permissions import request_permissions
    from android.permissions import Permission

class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        if is_android:
            self.provider = GpsListener(self.on_gps_update)
        else:
            self.provider = None
    
    def on_stop(self):
        if is_android:
            self.provider.stop_gps_updates()
    
    def on_start(self):
        if is_android:
            request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION], self.on_request_result)
    
    def on_request_result(self, permissions, grant_results):
        """
        get the request results
        """
        for index, permission in enumerate(permissions):
            if permission == Permission.ACCESS_FINE_LOCATION:
                if grant_results[index]:
                    Logger.info("APP: ACCESS_FINE_LOCATION has been accepted")
                    self.provider.start_gps_updates(3000, 10)
    
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

def main():
    MainApp().run()

if __name__ == '__main__':
    main()