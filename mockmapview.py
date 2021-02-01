from kivy.garden.mapview import MapView
from kivy.garden.mapview import MapMarker
from kivy.logger import Logger

class MockMapView(MapView):
    DEFAULT_ZOOM_IN = 16

    def __init__(self, **kwargs):
        self._marker = None
        super().__init__(**kwargs)

    def on_zoom(self, view, zoom_level):
        Logger.info(f"ZOOM: {zoom_level}")
        super().on_zoom(view, zoom_level)
    
    def on_touch_down(self, touch):
        # if touch.is_double_tap:
        #     Logger.info("ON_TOUCH_DOWN: Double Tapped")
        #     lat, lng = self.get_latlon_at(touch.x, touch.y, self.zoom)
        #     self.center_on(lat, lng)
        #     if self._marker:
        #         self.remove_marker(self._marker)
        #     self._marker = MapMarker(source="target.png", lat=lat, lon=lng)
        #     self.add_marker(self._marker)        
        super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        lat, lng = self.get_latlon_at(touch.x, touch.y, self.zoom)
        self.update_marker(lat, lng)
        super().on_touch_up(touch)
    
    def update_marker(self, lat, lng):
        if self._marker:
            self.remove_marker(self._marker)
        self._marker = MapMarker(source="target.png", lat=lat, lon=lng)
        self.add_marker(self._marker)

    def setdefault(self, lat, lng):
        self.center_on(lat, lng)
        self.zoom = MockMapView.DEFAULT_ZOOM_IN