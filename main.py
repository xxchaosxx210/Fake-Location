from kivymd.app import MDApp
from kivy.logger import Logger
import pydroid


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
    
    def on_start(self):
        self.root.ids["mock_status"].text = "AaaaaBBBBbbbbbbbCCCccxxc\n" * 100
        if pydroid.is_android():
            Logger.info("FakeGPS: Requesting Permissions")
            from android.permissions import request_permissions
            from android.permissions import Permission
            result = request_permissions([Permission.ACCESS_FINE_LOCATION])
            Logger.info(f"FakeGPS: request_permissions returned {result}")

def main():
    MainApp().run()

if __name__ == '__main__':
    main()