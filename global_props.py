from kivy.utils import platform

is_android = platform == "android"

class Globals:

    location_manager = None
    mock_thread = None