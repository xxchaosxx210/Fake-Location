from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import mainthread
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivymd.app import MDApp

is_android = platform == "android"

if is_android:
    from location import get_geo_location

from debug import Debug

import threading

Builder.load_string("""

<SearchContent>:
    orientation: "vertical"
    scroll_view: id_scroll_view
    list_items: id_search_list
    address_text: id_address_text.text
    app: app

    MDToolbar:
        title: "Search Address"
        md_bg_color: app.theme_cls.primary_color

    MDTextField:
        size_hint_y: None
        height: "36dp"
        on_text: root.on_text(self, self.text)
        id: id_address_text
        text: root.address_text

    ScrollView:
        id: id_scroll_view
        MDList:
            id: id_search_list
    
    MDFloatLayout:
        MDFlatButton:
            size_hint: None, None
            size: dp(68), dp(48)
            text: "Cancel"
            id: id_cancel_button
            on_release: root.cleanup_and_exit()
            pos_hint: {"right": 1, "bottom": 1}

<SearchListItem>:
    font_style: "Body2"
""")

def format_geo_address(addr):
    return f"{addr.house_number} {addr.second_address} {addr.postcode} {addr.country}"

class SearchThread(threading.Thread):

    def __init__(self, address, callback, **kwargs):
        self.callback = callback
        self.address = address
        super().__init__(**kwargs)

    def run(self):
        """
        retrieve geo location list and notify parent thread
        """
        if is_android:
            try:
                addrs = get_geo_location(self.address, 10)
            except Exception as err:
                Debug.log("GEOTEST", error=err.__str__())
                addrs = []
            finally:
                self.callback(addrs)
        else:
            addrs = Debug.get_geo_address(self.address, 10)
            self.callback(addrs)

class SearchListItem(OneLineIconListItem):

    def __init__(self, geoloc, **kwargs):
        self.geoloc = geoloc
        super().__init__(**kwargs)

class SearchContent(MDBoxLayout):

    scroll_view = ObjectProperty(None)
    list_items = ObjectProperty(None)
    address_text = StringProperty("")
    # reference object to App instance
    app = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.thread = None
        self.item_selected = False
    
    def cleanup_and_exit(self):
        """
        clears the list and exits
        """
        self.list_items.clear_widgets()
        self.address_text = ""
        self.app.root.current = "mapview"
    
    @mainthread  
    def on_search_result(self, addr_list):
        """
        callback return function from SearchThread
        """
        # clear previous list
        self.list_items.clear_widgets()
        if addr_list:
            for addr in addr_list:
                # Will improve the way list items are handled
                address = format_geo_address(addr)
                # create a new list item
                listitem = SearchListItem(
                    geoloc=addr,
                    text=address, 
                    on_press=self.on_item_selected)
                # add it on
                self.list_items.add_widget(listitem)
    
    def on_item_selected(self, item):
        """
        Item got selected in the search list
        set the item_select to true so we 
        know that text has been added from search
        this is to avoid another search when on_text gets called
        """
        # get the app object
        self.item_selected = True
        self.app.container.mockmapview.update_target_center(
                                item.geoloc.latitude, 
                                item.geoloc.longitude
                            )
        self.item_selected = False
        self.cleanup_and_exit()
    
    def do_search(self, text):
        """
        init search thread and start it
        """
        self.thread = SearchThread(text, self.on_search_result)
        self.thread.start()
    
    def on_text(self, textfield, text):
        # check if text has been added after selecting item from MDList
        # make sure enough characters are filled into the search field
        # 4 is default
        if not self.item_selected and len(text) > 4:
            # Text was typed in so do a search
            if self.thread:
                # if the thread isnt alive then create a new one
                if not self.thread.is_alive():
                    self.do_search(text)
            else:
                # No thread running
                self.do_search(text)
        else:
            self.list_items.clear_widgets()
    


