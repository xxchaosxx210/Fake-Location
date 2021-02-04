from kivy.utils import platform

is_android = platform == "android"

class Globals:

    # Stores the global LocationManager
    location_manager = None
    # Refernce to the MockLocation thread
    mock_thread = None