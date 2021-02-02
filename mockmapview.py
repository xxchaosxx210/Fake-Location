from kivy.garden.mapview import MapView
from kivy.garden.mapview import MapMarker
from kivy.logger import Logger
from kivymd.app import App
from kivy.metrics import dp

from kivy.properties import ObjectProperty

class MockMapView(MapView):
    DEFAULT_ZOOM_IN = 8

    # reference to the mapview button toolbar
    # need this to check if touch up event was triggered inside
    # the toolbar if so then we ignore adding a target marker
    toolbar = ObjectProperty(None)

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
        window = App.get_running_app()
        # add coords to root windows textfields
        window.root.lat_text = str(lat)
        window.root.lon_text = str(lng)

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