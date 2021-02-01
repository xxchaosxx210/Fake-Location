from kivy.garden.mapview import MapView
from kivy.logger import Logger


class MockMapView(MapView):
    DEFAULT_ZOOM_IN = 16

    def on_zoom(self, view, zoom_level):
        Logger.info(f"ZOOM: {zoom_level}")
        super().on_zoom(view, zoom_level)
    
    def on_touch_down(self, touch):
        if touch.is_double_tap:
            Logger.info("ON_TOUCH_DOWN: Double Tapped")
            lat, lng = self.get_latlon_at(touch.x, touch.y, self.zoom)
            self.center_on(lat, lng)
        super().on_touch_down(touch)
    
    def setdefault(self, lat, lng):
        self.center_on(lat, lng)
        self.zoom = MockMapView.DEFAULT_ZOOM_IN