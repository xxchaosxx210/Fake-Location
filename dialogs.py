from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.lang import Builder
from kivymd.toast import toast

from kivy.properties import(
    ObjectProperty,
    StringProperty,
    ListProperty
)

from kivymd.uix.list import (
    OneLineAvatarIconListItem,
    IRightBodyTouch
)

from global_props import (
    save_settings,
    load_Settings
)

from debug import Debug

_LOCATION_DENIED = """Fake Location does not have the Location Privileges enabled. 
Please enable location privileges, goto: Settings->Apps->Fake Location->Permissions"""


Builder.load_string("""

<MDDialog>:
    padding: 0
    spacing: 0

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
    size_hint: .9, None
    height: dp(400)
    id: id_load_container
    location_list: id_location_list
    app: app
    
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
        MDRectangleFlatIconButton:
            text:"Close"
            icon: "close"
            size_hint_x: None
            width: dp(70)
            on_release: root.on_close_button()
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
        self.location_settings = loc
        super().__init__(**kwargs)

class IconRightWidget(IRightBodyTouch, MDIconButton):
    listitem = ObjectProperty(None)

class LoadLocationContainer(MDBoxLayout):

    location_list = ObjectProperty(None)
    app = ObjectProperty(None)
    
    def load_list(self, location_list):
        """
        load_list(list)
        iterate through the location list loaded from settings.json
        and create a new listitem for item it and it to the MDList
        """
        self.location_list.clear_widgets()
        for location in location_list:
            widget = LocationListItem(
                loc=location,
                text = location["name"],
                on_release = self.on_item_selected
            )
            widget.delete_button.bind(on_release=self._on_delete_button)
            self.location_list.add_widget(widget)
    
    def _on_delete_button(self, icon_button):
        # create a new list for stored location settings
        saved_coords = []
        settings = load_Settings()
        # remove the widget from the MDList
        self.location_list.remove_widget(icon_button.listitem)
        # Loop through the new list appending each location_setting
        for widget in self.location_list.children:
            saved_coords.append(widget.location_settings)
        # store new location list and save to file
        settings["saved_coords"] = saved_coords
        save_settings(settings)
        Debug.log_file("Saved Settings", "on_delete_button dialogs.py", "Saved settings to settings.json")

    def on_item_selected(self, listitem):
        """
        set the target marker on the mapview with
        selected coordinates
        """
        Dialogs._load_location.dismiss()
        lat = listitem.location_settings["lat"]
        lng = listitem.location_settings["lng"]
        zoom = listitem.location_settings["zoom_level"]
        # Place the Target Marker at the new coordinates
        self.app.container.mockmapview.update_target_marker(lat, lng)
        # Set the Zoom level
        self.app.container.mockmapview.zoom = zoom
        # Center on New Target Marker
        self.app.container.mockmapview.center_on(lat, lng)
    
    def on_close_button(self):
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
            title="Locations",
            type="custom",
            content_cls=LoadLocationContainer(),
            auto_dismiss=False
        )
