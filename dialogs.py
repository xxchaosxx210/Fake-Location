from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


_LOCATION_DENIED = """Fake Location does not have the Location Privileges enabled. 
Please enable location privileges, goto: Settings->Apps->Fake Location->Permissions"""

class Dialogs:

    _alert = None

    @staticmethod
    def show_alert(title, message):
        if Dialogs._alert:
            Dialogs._alert.title = title
            Dialogs._alert.text = message
            Dialogs._alert.open()
    
    @staticmethod
    def show_location_denied():
        Dialogs.show_alert("Permission Denied", _LOCATION_DENIED)

    @staticmethod
    def generate_dialogs(app):
        """
        must be called in app on_start method
        """
        Dialogs._alert = MDDialog(
            title="",
            text="",
            buttons=[
                MDFlatButton(
                    text="OK", 
                    text_color=app.theme_cls.primary_color,
                    on_release=lambda x: Dialogs._alert.dismiss())
            ]
        )
