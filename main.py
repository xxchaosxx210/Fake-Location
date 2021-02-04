__title__ = "Fake Location"
__author__ = "Paul Millar"
__version__ = "0.1.1"
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
from kivy.utils import platform
from kivymd.toast import toast
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import NoTransition
from kivy.base import EventLoop

from mockmapview import MockMapView

# Debugging
from debug import Debug

from dialogs import Dialogs

is_android = platform == "android"

# If android then load the Android classes
if is_android:
    from location import get_location_manager
    from location import require_location_permissions
    from location import MockLocation
    from location import get_system_location

def _getlatlng(location_manager):
    latlng = None
    if is_android:
        location = get_system_location(location_manager)
        if location:
            latlng = (location.getLatitude(), location.getLongitude())
    else:
        # use the debugging location
        latlng = (Debug.latitude, Debug.longitude)
    return latlng


class Container(MDBoxLayout):
    # Mpaview object
    mockmapview = ObjectProperty(None)
    lat_text = StringProperty("-12.98989")
    lon_text = StringProperty("52.87878")

class MainApp(MDApp):

    container = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        if is_android:
            # Get LocationManager from Android API
            self._location_manager = get_location_manager()
            # Mock handler thread for setting mock location and enabling and disabling the mock locations
            self._update = MockLocation(self._location_manager, self._on_mock_error)
        else:
            self._location_manager = None
    
    def _on_mock_error(self, status, err):
        if status == "permission-denied":
            Logger.info(f"ERROR: Mock Permisisson denied")
        elif status == "provider-exists":
            Logger.info(f"Error: Provider exists")
        else:
            Logger.info(f"Unknown: {err.__str__()}")
    
    def on_search_button(self, *args):
        self.root.current = "search"
    
    def on_stop(self):
        print("Stop method called")
        if is_android:
            # wait for the thread to cancel before quitting the thread
            self._update.join()
    
    def on_start(self):
        # Capture the Escape key
        EventLoop.window.bind(on_keyboard=self.on_keyboard_press)
        # init basic dialogs
        Dialogs.generate_dialogs(self)
        # Obtain a reference to the Container Layout object
        self.container = self.root.ids.id_map_screen_container
        if is_android:
            # Get ACCESS_FINE_LOCATION Permission from user
            require_location_permissions(self.on_gps_update)
            # start the mock location thread
            self._update.start()
        else:
            # Set a random location on Windows or Linux
            Debug.randomize_latlng()
            self.container.mockmapview.update_current_locmarker(Debug.latitude, Debug.longitude, False)
    
    def on_keyboard_press(self, window, key, *args):
        if key == 27:
            # Escape key or back in android
            # add more screen conditions later
            if self.root.current == "mapview":
                # Close mock update thread
                # before the window closes
                if is_android:
                    self._update.kill.set()
                return False
            return True

    @mainthread
    def on_gps_update(self, provider, event, *args):
        """
        on_gps_update(str, str, tuple)
        Callback function for handling messages sent from
        Mock Locations thread. This method
        is only used on the Android version
        Is also the handler for permission request results.
        permission-result -     args[bool]
        """    
        if event == 'permissions-result':
            if args[0] == True:
                # Permission accepted get last known location
                latlng = _getlatlng(self._location_manager)
                if latlng:
                    self.container.mockmapview.update_current_locmarker(latlng[0], latlng[1], False)
                else:
                    toast("Could not find your location. Try turning Location on in settings")
            else:
                toast("Request to use Locations rejected. Please enable Locations in App Permissions")
    
    def on_loc_button_released(self):
        """
        Get Location position is pressed
        """
        try:
            latlng = _getlatlng(self._location_manager)
        except Exception as err:
            if "ACCESS_FINE_LOCATION" in err.__str__():
                Dialogs.show_location_denied()
                return
        if latlng:
            self.container.mockmapview.update_current_locmarker(latlng[0], latlng[1], True)
        else:
            toast("Could not find your location. Try turning Location on in settings")
    
    def on_start_mock(self):
        """
        Start button is pressed
        """
        # get the target marker coordinates
        latitude, longitude = self.container.mockmapview.get_last_target_coords()
        if latitude and longitude:
            # if target marker exists then set the mock location
            if is_android:
                # tell mock location thread to set new coordinates
                self._update.send_message("start", latitude, longitude)
            else:
                # set global debugging coordinates
                Debug.latitude = latitude
                Debug.longitude = longitude
                self.container.mockmapview.update_current_locmarker(Debug.latitude, Debug.longitude, False)
        else:
            # Let user know nothing was selected
            Dialogs.show_alert("No Target found", "Press on the map to select target location and then press the start button")
    
    def on_stop_mock(self):
        """ 
        Stop button is pressed
        """
        if is_android:
            self._update.send_message("stop")
        else:
            # Set a random location on Windows or Linux
            Debug.randomize_latlng()
            self.container.mockmapview.update_current_locmarker(Debug.latitude, Debug.longitude, False)
        self.container.mockmapview.remove_target_marker()

def main():
    MainApp().run()

if __name__ == '__main__':
    main()