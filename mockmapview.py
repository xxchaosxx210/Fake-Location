from kivy.garden.mapview import MapView
from kivy.logger import Logger


class MockMapView(MapView):
    DEFAULT_ZOOM_IN = 10

    def on_zoom(self, view, zoom_level):
        Logger.info(f"ZOOM: {zoom_level}")
        super().on_zoom(view, zoom_level)