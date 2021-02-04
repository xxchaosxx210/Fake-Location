from kivy.utils import platform

is_android = platform == "android"

VERSION = "0.1.3"

class Globals:

    # Stores the global LocationManager
    location_manager = None
    # Refernce to the MockLocation thread
    mock_thread = None