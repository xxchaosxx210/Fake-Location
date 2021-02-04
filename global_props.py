from kivy.utils import platform
import os
import json
from threading import Lock

is_android = platform == "android"

VERSION = "0.1.3"

# Get settings folder path

APP_NAME = "fake_location"
SETTINGS_FILENAME = "settings.json"
LOG_FILENAME = "log.txt"

if platform == "win":
    PATH = os.path.join(os.environ.get("USERPROFILE"), APP_NAME)
elif platform == "android":
    from android.storage import app_storage_path
    PATH = app_storage_path()
else:
    PATH = os.path.join(os.environ.get("HOME"), APP_NAME)

_file_lock = Lock()

# Settings
# - 

def load_Settings():
    data = load(SETTINGS_FILENAME)
    if data:
        return json.loads(data)
    return data

def save_settings(data):
    save(SETTINGS_FILENAME, json.dumps(data))

def check_path_exists():
    if not os.path.exists(PATH):
        _file_lock.acquire()
        os.mkdir(PATH)
        _file_lock.release()

def load(filename):
    """
    load(str)
    takes in the name of the file to load. Doesnt require full path just the name of the file and extension
    returns loaded json object or None if no file exists
    """
    data = None
    check_path_exists()
    full_path = os.path.join(PATH, filename)
    _file_lock.acquire()
    if os.path.exists(full_path):
        with open(full_path, "r") as fp:
            data = fp.read()
    _file_lock.release()
    return data

def save(filename, data):
    _file_lock.acquire()
    full_path = os.path.join(PATH, filename)
    check_path_exists()
    with open(full_path, "w") as fp:
        fp.write(data)
    _file_lock.release()

class Globals:

    # Stores the global LocationManager
    location_manager = None
    # Refernce to the MockLocation thread
    mock_thread = None