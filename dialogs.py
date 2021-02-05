from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

_LOCATION_DENIED = """Fake Location does not have the Location Privileges enabled. 
Please enable location privileges, goto: Settings->Apps->Fake Location->Permissions"""


Builder.load_string("""
<SaveContent>:
    orientation: "vertical"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        multiline: False
        hint_text: "Description"
        id: id_description
        text: ""
""")

class SaveContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Dialogs:

    _alert = None
    _save = None

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
    def show_save_dialog(title):
        if Dialogs._save:
            Dialogs._save.title = title
            Dialogs._save.open()

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

        Dialogs._save = MDDialog(
            title="",
            type="custom",
            content_cls=SaveContent(),
            buttons=[
                MDFlatButton(
                    text="Cancel", 
                    text_color=app.theme_cls.primary_color,
                    on_release=lambda x: Dialogs._save.dismiss()
                ),
                MDFlatButton(
                    text="Save", 
                    text_color=app.theme_cls.primary_color,
                    on_release=lambda x: Dialogs._save.dismiss()
                )
            ]
        )
