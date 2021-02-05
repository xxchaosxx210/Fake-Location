from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivymd.toast import toast

from global_props import save_settings
from global_props import load_Settings

_LOCATION_DENIED = """Fake Location does not have the Location Privileges enabled. 
Please enable location privileges, goto: Settings->Apps->Fake Location->Permissions"""


Builder.load_string("""
<SaveContent>:
    orientation: "vertical"
    size_hint_y: None
    height: "120dp"
    description_text: id_description.text
    app: app

    MDTextField:
        multiline: False
        hint_text: "Description"
        id: id_description
        text: root.description_text
    
    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: "48dp"
        Widget:
            size_hint: .5, 1
        MDFlatButton:
            text: "Cancel"
            id: id_cancel_button
            text_color: app.theme_cls.primary_color
            on_release: root.on_cancel_button()
        MDFlatButton:
            text: "Save"
            id: id_save_button
            text_color: app.theme_cls.primary_color
            on_release: root.on_save_button()
        Widget:
            size_hint: .5, 1
""")

class SaveContent(MDBoxLayout):

    description_text = StringProperty("")
    app = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_cancel_button(self):
        Dialogs._save.dismiss()
    
    def on_save_button(self):
        settings = load_Settings()
        lat, lng = self.app.container.mockmapview.get_target_coords()
        coords = {
            "lat": lat, 
            "lng": lng, 
            "name": self.description_text, 
            "zoom_level": self.app.container.mockmapview.zoom
            }
        settings["saved_coords"].append(coords)
        save_settings(settings)
        Dialogs._save.dismiss()
        toast("Coordinates have been saved")


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
    def show_save_dialog():
        if Dialogs._save:
            # clear the last text entry
            Dialogs._save.content_cls.description_text = ""
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
            title="Name of Coordinates",
            type="custom",
            content_cls=SaveContent(),
            auto_dismiss=False
        )
