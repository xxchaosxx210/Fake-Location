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

def load(filename):
    """
    load(str)
    takes in the name of the file to load. Doesnt require full path just the name of the file and extension
    returns loaded json object or None if no file exists
    """
    full_path = os.path.join(PATH, filename)
    _file_lock.acquire()
    data = None
    if not os.path.exists(PATH):
        os.mkdir(PATH)
    if os.path.exists(full_path):
        with open(full_path) as fp:
            data = json.loads(fp.read())
    _file_lock.release()
    return data

def save(filename, data):
    _file_lock.acquire()
    full_path = os.path.join(PATH, filename)
    if not os.path.exists(PATH):
        os.mkdir(PATH)
    with open(full_path) as fp:
        fp.write(json.dumps(data))
    _file_lock.release()

class Globals:

    # Stores the global LocationManager
    location_manager = None
    # Refernce to the MockLocation thread
    mock_thread = None