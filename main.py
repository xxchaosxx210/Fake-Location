from kivymd.app import MDApp
from kivy.logger import Logger
from kivy.clock import mainthread
import pydroid
import time

provider = None

class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        if pydroid.is_android():
            self.provider = pydroid.GpsListener(self.on_gps_update)
        else:
            self.provider = None
    
    def on_stop(self):
        if pydroid.is_android():
            if self.provider:
                self.provider.stop()
    
    def on_start(self):
        if pydroid.is_android():
            Logger.info("FakeGPS: Requesting Permissions")
            from android.permissions import request_permissions
            from android.permissions import Permission
            request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
            time.sleep(3)
            self.provider.start()
    
    @mainthread
    def on_gps_update(self, provider, event, *args):
        if event == 'location':
            print(args)
            #location = args[0].location
            #lat = location.getLatitude()
            #lng = location.getLongitude()
            #if len(self.root.ids["mock_status"].text) > 500:
            #    self.root.ids["mock_status"].text = ""
            #self.root.ids["mock_location"].text += f"\n Lat: {lat}, Lng: {lng}"

def main():
    MainApp().run()

if __name__ == '__main__':
    main()