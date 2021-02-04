__title__ = "main_map"
__description__ = """Holds the mapview and mapcontainer classes"""

from kivy.garden.mapview import MapView
from kivy.garden.mapview import MapMarker
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivymd.toast import toast
from kivy.logger import Logger

from kivy.properties import ObjectProperty

from global_props import is_android
from global_props import Globals

if is_android:
    from location import get_system_location

from debug import Debug
from dialogs import Dialogs


def getlatlng(location_manager):
    """
    getlatlng(object)
    if on android platform gets last known location
    if on Windows Linux or iOS then dummy coordinates returned
    could use plyer for kivy if migrate over
    to cross platforms
    """
    latlng = None
    if is_android:
        location = get_system_location(location_manager)
        if location:
            latlng = (location.getLatitude(), location.getLongitude())
    else:
        # use the debugging location
        latlng = (Debug.latitude, Debug.longitude)
    return latlng


class MapContainer(MDBoxLayout):
    # Mpaview object
    app = ObjectProperty(None)
    mockmapview = ObjectProperty(None)
    lat_text = StringProperty("-12.98989")
    lon_text = StringProperty("52.87878")

    def on_search_button(self, *args):
        self.app.root.current = "search"

    def on_loc_button_released(self):
        """
        Get Location position is pressed
        """
        try:
            latlng = getlatlng(Globals.location_manager)
            if latlng:
                self.mockmapview.update_current_locmarker(latlng[0], latlng[1], True)
            else:
                toast("Could not find your location. Try turning Location on in settings")
        except Exception as err:
            if "ACCESS_FINE_LOCATION" in err.__str__():
                Dialogs.show_location_denied()
                return
            else:
                Logger.info(err.__str__())
    
    def on_start_mock(self):
        """
        Start button is pressed
        """
        # get the target marker coordinates
        latitude, longitude = self.mockmapview.get_last_target_coords()
        if latitude and longitude:
            # if target marker exists then set the mock location
            if is_android:
                # tell mock location thread to set new coordinates
                Globals.mock_thread.send_message("start", latitude, longitude)
            else:
                # set global debugging coordinates
                Debug.latitude = latitude
                Debug.longitude = longitude
                self.mockmapview.update_current_locmarker(Debug.latitude, Debug.longitude, False)
        else:
            # Let user know nothing was selected
            Dialogs.show_alert("No Target found", "Press on the map to select target location and then press the start button")
    
    def on_stop_mock(self):
        """ 
        Stop button is pressed
        """
        if is_android:
            Globals.mock_thread.send_message("stop")
        else:
            # Set a random location on Windows or Linux
            Debug.randomize_latlng()
            self.mockmapview.update_current_locmarker(Debug.latitude, Debug.longitude, False)
        self.mockmapview.remove_target_marker()


class MockMapView(MapView):
    DEFAULT_ZOOM_IN = 8

    # reference to the mapview button toolbar
    # need this to check if touch up event was triggered inside
    # the toolbar if so then we ignore adding a target marker
    toolbar = ObjectProperty(None)
    app = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._target_marker = None
        self._current_loc_marker = None
        super().__init__(**kwargs)
    
    def on_touch_up(self, touch):
        """
        Map pressed get coordinates and update target marker position
        """
        # make sure was inside the mapview bounds before updating target marker
        if self.collide_point(touch.x, touch.y) == True and self.toolbar.collide_point(touch.x, touch.y) == False:
            lat, lng = self.get_latlon_at(touch.x, touch.y - dp(23), None)
            self.update_target_marker(lat, lng)
        super().on_touch_up(touch)
    
    def update_target_center(self, lat, lng):
        self.update_target_marker(lat, lng)
        self.center_on(lat, lng)
    
    def update_target_marker(self, lat, lng):
        """
        update_target_locmarker(float, float)
        updates the target location marker
        lat - Latitude coordinates
        lng - Longitude coords
        """
        if self._target_marker:
            self.remove_marker(self._target_marker)
        self._target_marker = MapMarker(source="target.png", lat=lat, lon=lng)
        self.add_marker(self._target_marker)
        # add coords to root windows textfields
        self.app.root.lat_text = str(lat)
        self.app.root.lon_text = str(lng)

    def update_current_locmarker(self, lat, lng, zoom):
        """
        update_current_locmarker(float, float, bool)
        updates the current location marker
        lat - Latitude coordinates
        lng - Longitude coords
        zoom - Zoom into marker if True else ignore Zoom
        """
        self.center_on(lat, lng)
        if zoom:
            self.zoom = MockMapView.DEFAULT_ZOOM_IN
        if self._current_loc_marker:
            self.remove_marker(self._current_loc_marker)
        self._current_loc_marker = MapMarker(source="current_marker.png", lat=lat, lon=lng)
        self.add_marker(self._current_loc_marker)
        #Logger.info(f"UPDATE_CURRENT_MARKER: lat={lat}, lng={lng}, zoom={zoom}")
    
    def get_last_target_coords(self):
        """
        returns last targets latitude and lonitude coordinates. None is no target selected
        """
        if self._target_marker:
            lat, lng = (self._target_marker.lat, self._target_marker.lon)
        else:
            lat, lng = (None, None)
        #Logger.info(f"GET_LAST_TARGET_COORDS: lat{lat}, lng={lng}")
        return (lat, lng)
    
    def remove_target_marker(self):
        if self._target_marker:
            self.remove_marker(self._target_marker)
    
    def on_zoom_button(self, zoom_value):
        """
        on_zoom(int)
        zoom_value is the zoom value to change
        zooms on target marker if no target marker then zoom
        to center of map
        """
        if self._target_marker:
            self.center_on(self._target_marker.lat, self._target_marker.lon)
            self.zoom = zoom_value
        else:
            self.zoom = zoom_value
        