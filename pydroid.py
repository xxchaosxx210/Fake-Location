"""
note: if running on a non android platform you will only have access to is_android function 

info:

most of the code can be found here - https://developer.android.com/docs/

to compile java files with buildozer just add the java filename to 'android.add_src' line in your buildozer.spec file

for information on pyjnius visit - https://pyjnius.readthedocs.io/en/latest/
python-4-android page - https://python-for-android.readthedocs.io/en/latest/troubleshooting/
a better understanding for python-4-android check this link out - https://github.com/kivy/python-for-android/issues/388 

I spent quite a few days working a lot of undocumented python4android code out lost many hair strands in the process!!"""

__version__ = "0.2"
__author__ = "Paul Millar"

import threading

try:
	from android.runnable import run_on_ui_thread
	from android import api_version as API_VERSION
	_is_android = True
	import time
except ImportError:
	_is_android = False


def is_android():
	return _is_android
	
if is_android():

	from jnius import autoclass
	from jnius import cast
	from jnius import PythonJavaClass
	from jnius import java_method
	from android import activity

	## Java STD classes
	String = autoclass("java.lang.String")
	CharSequence = autoclass('java.lang.CharSequence')
	Locale = autoclass("java.util.Locale")

	## Android classes
	Toast = autoclass('android.widget.Toast')
	PythonActivity = autoclass('org.kivy.android.PythonActivity')
	TexttoSpeech = autoclass("android.speech.tts.TextToSpeech")
	Context = autoclass('android.content.Context')
	Activity = autoclass("android.app.Activity")
	Intent = autoclass("android.content.Intent")
	## android SPEECH api
	
	RecognizerIntent = autoclass('android.speech.RecognizerIntent')

	## Android Threading
	Looper = autoclass("android.os.Looper")
	
	## Android networking
	Uri = autoclass("android.net.Uri")

	RingtoneManager = autoclass("android.media.RingtoneManager")
	Ringtone = autoclass("android.media.Ringtone")
	
	## Android contacts
	#ContactsContract = autoclass('android.provider.ContactsContract')
	#Intents = autoclass('android.provider.Contacts.Intents')
	
	## Use the logging object to show output on logcat
	Log = autoclass("android.util.Log")
	TAG = "python"

	## Location Classes
	LocationManager = autoclass("android.location.LocationManager")
	LocationProvider = autoclass("android.location.LocationProvider")
	
	## Custom Classes
	Gps = autoclass("Gps")
	Contact = autoclass("Contact")
	
	CURRENT_CONTEXT = PythonActivity.mActivity.getApplicationContext()

else:
	# Not Android platform so create dummy decorators
	def run_on_ui_thread(func):
		def wrapper(*args):
			return False
		return wrapper
	
	def java_method(func):
		def wrapper(*args):
			return False
		return wrapper

	class PythonJavaClass:
		pass

def navigate_google_maps(uri):
	if is_android():
		gmm_intent_uri = Uri.parse(uri)
		map_intent = Intent(Intent.ACTION_VIEW, gmm_intent_uri)
		map_intent.setPackage('com.google.android.apps.maps')
		PythonActivity.mActivity.startActivity(map_intent)
	else:
		print("Cannot send intent to Google Maps as not Android platform")


def navigate_waze(lat, lng):
	if is_android():
		"""
		uses the older url format waze://. use https for newer phones
		"""
		#url = f"https://waze.com/ul?ll={lat},{lng}&navigate=yes"
		#url = f"https://waze.com/ul?ll={lat},{lng}"
		url = f"waze://?ll={lat},{lng}&navigate=yes&z=4"
		intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
		PythonActivity.mActivity.startActivity(intent)
	else:
		print("Cannot send intent to waze as not Android Platform")


def play_system_sound(sound_type):
	"""
	play_system_sound(sound_type) -> None
	Parameters:
		sound_type - str
			"notification"
			"alert"
			"ringtone"
	"""
	if is_android():
		if sound_type == "notification":
			uri_type = RingtoneManager.TYPE_NOTIFICATION
		elif sound_type == "alert":
			uri_type = RingtoneManager.TYPE_ALARM
		elif sound_type == "ringtone":
			uri_type = RingtoneManager.TYPE_RINGTONE
		else:
			raise NameError('''sound_type did not match any defaults. use one of these three - "notification", ""''')
		sound_uri = RingtoneManager.getDefaultUri(uri_type)
		ringtone = RingtoneManager.getRingtone(PythonActivity.mActivity, sound_uri)
		ringtone.play()
		return True
	else:
		return False


def ask_permission(permissions=[], timeout=5):
	"""
	api level > 21 requires permissions to be prompted by the user rather than set in the manifest file
	dialog box will oonly be displayed if permission not applied
	"""
	if is_android():
		global PythonActivity
		if API_VERSION > 21:
			print(f"NOW ASKING FOR PERMISSIONS. API LEVEL = {API_VERSION}")
			PythonActivity.requestPermissions(permissions)
			time.sleep(timeout)
		else:
			print(f"THIS OS DOES NOT REQUIRE PERMISSIONS TO BE ASKED. ADD PERMISSIONS IN BUILDOZER.SPEC INSTEAD\nAPI LEVEL = {API_VERSION}")
		return True
	else:
		return False


@run_on_ui_thread
def toast(message="", long_time=False):
	"""
	displays a toast dialog box
	"""
	if is_android():
		c = cast(CharSequence, String(message))
		if long_time:
			length = Toast.LENGTH_LONG
		else:
			length = Toast.LENGTH_SHORT
		Toast.makeText(PythonActivity.mActivity, c, length).show()	
		return True
	else:
		return False		


def get_telephony_manager():
	if is_android():
		ask_permission(["android.permission.READ_PHONE_STATE"])
		return PythonActivity.mActivity.getSystemService(Context.TELEPHONY_SERVICE)
	else:
		None


def insert_contact(name, phone):
	"""
	Requires Contact.java 
	"""
	if is_android():
		Contact.addContact(PythonActivity.mActivity, name, phone)
		return True
	else:
		return False


@run_on_ui_thread
def phone_call(phone_number):
	## note: make skype call "skype:<username>?call&video=false"
	if is_android():
		i = Intent('android.intent.action.VIEW')
		i.setData(Uri.parse("tel:" + phone_number))
		Log.i(TAG, "tel:" + phone_number)
		PythonActivity.mActivity.startActivity(i)
		return True
	else:
		return False


class SpeechtoText:
	
	""" SpeechtoText only needs to be instanced once. call show_sp2txt_dialog to prompt user for speech """
	
	REQUEST_SPEECH_RECOGNIZER = 3000
	
	def __init__(self):
		if is_android():
			## reflect our activity with the main apps activity
			self.current_activity = cast("android.app.Activity", PythonActivity.mActivity)
			## tell android where to send our speech results
			activity.bind(on_activity_result=self.on_activity_result)
	
	@run_on_ui_thread
	def show_sp2txt_dialog(self, callback):
		"""callback = must be a python method with a text parameter this will be the processed text from androids speechtotext algorithim"""
		if is_android():
			self._callback = callback
			
			## Create our intent for the recognizerspeech
			intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
			intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
			RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
			intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Tell me what you want to send?")
			## start the speech recognizer activity
			self.current_activity.startActivityForResult(intent, SpeechtoText.REQUEST_SPEECH_RECOGNIZER)
			return True
		else:
			return False
		
	def on_activity_result(self, request_code, result_code, intent):
		if request_code == SpeechtoText.REQUEST_SPEECH_RECOGNIZER:
			if result_code == Activity.RESULT_OK:
				results = intent.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
				self._callback(results.get(0))


class TextSpeak:

	"""
	converts text to speech
	"""
	
	def __init__(self, **kwargs):
		## setup the tts engine. can not be initiated during runtime
		## this only needs to be initiated once
		if is_android():
			self.__tts = TexttoSpeech(PythonActivity.mActivity, None)
			self.__tts.setLanguage(Locale.US)
	
	@run_on_ui_thread
	def speak(self, text=""):
		if is_android():
			c = cast(CharSequence, String(text))
			self.__tts.speak(c, TexttoSpeech.QUEUE_ADD, None, String("python-speak-id"))
			return True
		else:
			return False

class GpsListener(PythonJavaClass):

	__javainterfaces__ = ['android/location/LocationListener']

	def __init__(self, callback):
		super(GpsListener, self).__init__()
		self.callback = callback
		self.location_manager = PythonActivity.mActivity.getSystemService(
			Context.LOCATION_SERVICE
		)
	
	def start(self):
		self.location_manager.requestLocationUpdates(
			LocationManager.GPS_PROVIDER,
			10000,
			10,
			self,
			Looper.getMainLooper()
		)
	
	def stop(self):
		print("Stop method started")
		self.location_manager.removeUpdates(self)
	
	@java_method('()I')
	def hashCode(self):
		# return id(self)
		return 1 

	@java_method('(Landroid/location/Location;)V')
	def onLocationChanged(self, location):
		self.callback(self, "location", location)
	
	@java_method('(Ljava/lang/String;)V')
	def onProviderDisabled(self, status):
		self.callback(self, "provider-disabled", status)
	
	@java_method('(Ljava/lang/String;)V')
	def onProviderEnabled(self, provider):
		self.callback(self, "provider-enabled", provider)
	
	@java_method('(Ljava/lang/Object;)Z')
	def equals(self, obj):
		return obj.hashCode() == self.hashCode()
		