from global_props import VERSION

__title__ = "Fake Location"
__author__ = "Paul Millar"
__version__ = VERSION
__description__ = """
A Fake GPS app for android using the kivy and kivymd framework.
This App will run on Windows and Linux but because they lack
the GPS API the Win and *nix are for testing purposes only

Version 0.1
-----------
laying the framework down. Setting up android testing provider
trying for days to get the mock locations to work on google maps.
the another few days trying to get mapview to work and compile
using buildozer

Version 0.1.1
-------------
Modified the toolbar buttons
"""

from kivymd.app import MDApp
from kivy.logger import Logger
from kivy.clock import mainthread
from kivymd.toast import toast
from kivy.properties import ObjectProperty
from kivy.base import EventLoop

from main_map import MockMapView
from main_map import getlatlng

# Debugging
from debug import Debug
from dialogs import Dialogs

from global_props import Globals
from global_props import is_android
from global_props import save_settings
from global_props import load_Settings

# If android then load the Android classes
if is_android:
    from location import get_location_manager
    from location import require_location_permissions
    from location import MockLocationListener

class MainApp(MDApp):

    container = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        if is_android:
            # Get LocationManager from Android API
            Globals.location_manager = get_location_manager()
            # Mock handler thread for setting mock location and enabling and disabling the mock locations
            Globals.mock_thread = MockLocationListener(Globals.location_manager, self._on_mock_error)
    
    def _on_mock_error(self, status, err):
        if status == "permission-denied":
            Debug.log_file("Error", "_on_mock_error main.py", "MOCK LOCATION Permission denied")
        elif status == "provider-exists":
            Debug.log_file("Error", "_on_mock_error main.py", "Provider exists")
        else:
            Debug.log_file("Error", "_on_mock_error main.py", f"{err.__str__()}")
    
    def on_start(self):
        # Capture the Escape key
        EventLoop.window.bind(on_keyboard=self.on_keyboard_press)
        # init basic dialogs
        Dialogs.generate_dialogs(self)
        # Obtain a reference to the Container Layout object
        self.container = self.root.ids.id_map_screen_container
        if is_android:
            # Get ACCESS_FINE_LOCATION Permission from user
            require_location_permissions(self._on_permissions_result)
            # start the mock location thread
            Globals.mock_thread.start()
        else:
            # Set a random location on Windows or Linux
            Debug.randomize_latlng()
            self.container.mockmapview.update_current_locmarker(Debug.latitude, Debug.longitude, False)
        
        # Set the zoom level from last time
        settings = load_Settings()
        self.container.mockmapview.zoom = settings["last_zoom_level"]
    
    def on_keyboard_press(self, window, key, *args):
        if key == 27:
            # Escape key or back in android
            # add more screen conditions later
            if self.root.current == "mapview":
                # Close mock update thread
                # before the window closes
                if is_android:
                    Globals.mock_thread.kill.set()
                    print("Waiting for thread to quit")
                    Globals.mock_thread.join()
                return False
            elif self.root.current == "search":
                self.root.current = "mapview"
            elif self.root.current == "log":
                self.root.current = "mapview"
            return True

    @mainthread
    def _on_permissions_result(self, result):
        # Gets result from permission request 
        if result == True:
            # Permission accepted get last known location
            latlng = getlatlng(Globals.location_manager)
            if latlng:
                self.container.mockmapview.update_current_locmarker(latlng[0], latlng[1], False)
            else:
                toast("Could not find your location. Try turning Location on in settings")
        else:
            toast("Request to use Locations rejected. Please enable Locations in App Permissions")

def main():
    MainApp().run()

if __name__ == '__main__':
    main()