from kivy.garden.mapview import MapView
from kivy.garden.mapview import MapMarker
from kivy.logger import Logger

class MockMapView(MapView):
    DEFAULT_ZOOM_IN = 16

    def __init__(self, **kwargs):
        self._target_marker = None
        self._current_loc_marker = None
        super().__init__(**kwargs)

    def on_zoom(self, view, zoom_level):
        Logger.info(f"ZOOM: {zoom_level}")
        super().on_zoom(view, zoom_level)
    
    def on_touch_up(self, touch):
        lat, lng = self.get_latlon_at(touch.x, touch.y, self.zoom)
        self.update_target_marker(lat, lng)
        super().on_touch_up(touch)
    
    def update_target_marker(self, lat, lng):
        if self._target_marker:
            self.remove_marker(self._target_marker)
        self._target_marker = MapMarker(source="target.png", lat=lat, lon=lng)
        self.add_marker(self._target_marker)

    def update_current_locmarker(self, lat, lng, zoom):
        self.center_on(lat, lng)
        if zoom:
            self.zoom = MockMapView.DEFAULT_ZOOM_IN
        if self._current_loc_marker:
            self.remove_marker(self._current_loc_marker)
        self._current_loc_marker = MapMarker(source="current_marker.png", lat=lat, lon=lng)
        self.add_marker(self._current_loc_marker)