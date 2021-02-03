from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineIconListItem
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import mainthread
from kivy.properties import ObjectProperty

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

    MDTextFieldRect:
        size_hint_y: None
        height: "36dp"
        on_text: root.on_text(self, self.text)
        id: id_text_field

    ScrollView:
        id: id_scroll_view
        scroll_type: ["content"]
        MDList:
            id: id_search_list
    
    MDFloatLayout:
        MDFlatButton:
            text: "Cancel"
            id: id_cancel_button
            pos_hint: {"right": 1, "bottom": 1}
        MDFlatButton:
            text: "Search"
            id: id_search_button
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
            addrs = get_geo_location(self.address, 10)
            self.callback(addrs)
        else:
            addrs = Debug.get_geo_address(self.address, 10)
            self.callback(addrs)

class SearchListItem(OneLineIconListItem):
    pass

class SearchContent(MDBoxLayout):

    scroll_view = ObjectProperty(None)
    list_items = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.thread = None
        self.item_selected = False
    
    @mainthread
    def on_search_result(self, addr_list):
        """
        callback return function from SearchThread
        """
        if addr_list:
            for addr in addr_list:
                # Will improve the way list items are handled
                address = format_geo_address(addr)
                # create a new list item
                listitem = SearchListItem(
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
        Debug.log_object(item)
        self.item_selected = True
        self.ids.id_text_field.text = item.text
        self.list_items.clear_widgets()
        self.item_selected = False
    
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
    


