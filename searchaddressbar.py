from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.utils import platform
from kivy.clock import mainthread
import threading

is_android = platform == "android"

if is_android:
    from location import get_geo_location
else:
    from debug import Debug

def format_geo_result(addr):
    return f"{addr.house_number} {addr.second_address} {addr.postcode} {addr.country}"

class SearchLookupThread(threading.Thread):
    pass

class SearchAddressBar(BoxLayout):
    pass

class SearchTextField(MDTextField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._thread = None

    def on_text(self, searchtxtfield, text):
        if len(text) > 4:
            # perform a geo
            if is_android:
                pass
            else:
                geolist = Debug.get_geo_address("", 5)
                for geoaddr in geolist:
                    print(format_geo_result(geoaddr))
        super().on_text(searchtxtfield, text)