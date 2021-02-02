from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.utils import platform
from kivy.clock import mainthread
import threading
import time

is_android = platform == "android"

if is_android:
    from location import get_geo_location
else:
    from debug import Debug

def format_geo_result(addr):
    return f"{addr.house_number} {addr.second_address} {addr.postcode} {addr.country}"

class SearchLookupThread(threading.Thread):

    """
    performs a geo location lookup. Because androids GeoCoder
    requires a network request. Must use a thread to handle
    the request. return result with callback. max_range is the
    maximum number of geoaddress to return
    """
    
    def __init__(self, callback, address, max_range, **kwargs):
        super().__init__(**kwargs)
        self._callback = callback
        self._address = address
        self._max_range = max_range
    
    def run(self):
        if is_android:
            geolist = get_geo_location(self._address, self._max_range)
        else:
            #time.sleep(2)
            geolist = Debug.get_geo_address(self._address, self._max_range)
        self._callback(geolist)

class SearchAddressBar(BoxLayout):
    pass

class SearchTextField(MDTextField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._thread = None
    
    @mainthread
    def on_geo_result(self, geolist):
        for addr in geolist:
            print(format_geo_result(addr))

    def on_text(self, searchtxtfield, text):
        if len(text) > 4:
            # perform a geo
            if not self._thread:
                self._thread = SearchLookupThread(self.on_geo_result, text, 6)
                self._thread.start()
            if not self._thread.is_alive():
                self._thread = SearchLookupThread(self.on_geo_result, text, 6)
                self._thread.start()
        super().on_text(searchtxtfield, text)