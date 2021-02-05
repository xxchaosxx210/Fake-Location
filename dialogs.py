from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.lang import Builder
from kivymd.toast import toast

from kivy.properties import(
    ObjectProperty,
    StringProperty
)

from kivymd.uix.list import (
    OneLineAvatarIconListItem,
    IRightBodyTouch
)

from global_props import (
    save_settings,
    load_Settings
)

_LOCATION_DENIED = """Fake Location does not have the Location Privileges enabled. 
Please enable location privileges, goto: Settings->Apps->Fake Location->Permissions"""


Builder.load_string("""
<SaveCoordsContent>:
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

<LoadLocationContainer>:
    orientation: "vertical"
    size_hint_y: None
    height: "200dp"
    id: id_load_container
    location_list: id_location_list

    ScrollView:
        id: id_scrollview
        MDList:
            id: id_location_list
    MDBoxLayout:
        size_hint_y: None
        height: "48dp"
        orientation: "horizontal"
        Widget:
            size_hint: .5, 1
        MDFlatButton:
            size_hint_x: None
            width: dp(70)
        Widget:
            size_hint: .5, 1

<LocationListItem>:
    delete_button: id_delete
    id: id_list_item
    IconRightWidget:
        icon: "delete"
        id: id_delete
        listitem: id_list_item
""")

class LocationListItem(OneLineAvatarIconListItem):

    delete_button = ObjectProperty(None)

    def __init__(self, loc, **kwargs):
        self.lat = loc["lat"]
        self.lng = loc["lng"]
        self.name = loc["name"]
        self.zoom = loc["zoom_level"]
        super().__init__(**kwargs)

class IconRightWidget(IRightBodyTouch, MDIconButton):
    listitem = ObjectProperty(None)

class LoadLocationContainer(MDBoxLayout):

    location_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def load_list(self, location_list):
        self.location_list.clear_widgets()
        for location in location_list:
            widget = LocationListItem(
                loc=location,
                text = location["name"],
                on_release = self.on_item_selected
            )
            widget.delete_button.bind(on_release=self.on_delete_button)
            self.location_list.add_widget(widget)
    
    def on_delete_button(self, icon_button):
        self.location_list.remove_widget(icon_button.listitem)

    def on_item_selected(self, *args):
        print("")
        Dialogs._load_location.dismiss()

class SaveCoordsContent(MDBoxLayout):

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
    _load_location = None

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
    def show_load_location_dialog():
        if Dialogs._load_location:
            # Load list from file
            settings = load_Settings()
            Dialogs._load_location.content_cls.load_list(settings["saved_coords"])
            Dialogs._load_location.open()

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
            content_cls=SaveCoordsContent(),
            auto_dismiss=False
        )

        Dialogs._load_location = MDDialog(
            title="Choose Location",
            type="custom",
            content_cls=LoadLocationContainer()
        )
