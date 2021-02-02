from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineIconListItem
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import mainthread

is_android = platform == "android"

if is_android:
    from location import get_geo_location
else:
    from debug import Debug

import threading

Builder.load_string("""
<SearchContent>:
    orientation: "vertical"
    size_hint: 1, None
    height: "300dp"
    MDTextField:
        size_hint: 1, .2
        text: ""
        hint_text: "Search Address"
        id: id_search_text
        on_text: root.on_text(self, self.text)
    ScrollView:
        size_hint: 1, None
        height: 0
        id: id_scroll_view
        scroll_type: ["content"]
        MDList:
            id: id_search_list

<SearchListItem>:
    text: ""
""")

def format_geo_address(addr):
    return f"{addr.house_number} {addr.second_address} {addr.postcode} {addr.country}"

class SearchThread(threading.Thread):

    def __init__(self, address, callback, **kwargs):
        self.callback = callback
        self.address = address
        super().__init__(**kwargs)

    def run(self):
        if is_android:
            addrs = get_geo_location(self.address,
                                    10)
            self.callback(
                list(map(lambda x: format_geo_address(x), addrs))
            )
        else:
            addrs = Debug.get_geo_address(self.address, 10)
            self.callback(
                list(map(lambda x: format_geo_address(x), addrs))
            )

class SearchListItem(OneLineIconListItem):
    pass

class SearchContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.thread = None
    
    @mainthread
    def on_search_result(self, addr_list):
        """
        add new results to popup
        """
        if addr_list:
            self.ids.id_scroll_view.size_hint_y = 1
            for addr in addr_list:
                address = format_geo_address(addr)
                listitem = SearchListItem(text=address)
                self.ids.id_search_list.add_widget(listitem)
        else:
            self.ids.id_scroll_view.size_hint_y = 0
    
    def do_search(self, text):
        """
        init search thread and start it
        """
        self.thread = SearchThread(text, self.on_search_result)
        self.thread.start()
    
    def on_text(self, textfield, text):
        # make sure enough characters are filled into the search field
        if len(text) > 4:
            # do a geolocation search
            if self.thread:
                # if the thread isnt alive then create a new one
                if not self.thread.is_alive():
                    self.do_search(text)
            else:
                self.do_search(text)


class SearchPopupMenu(MDDialog):

    def __init__(self, callback, **kwargs):
        """
        callback function will be called when either
        cancel or search button pressed
        search - address, lat, lng
        """
        kwargs["type"] = "custom"
        kwargs["content_cls"] = SearchContent()
        kwargs["buttons"] = [
            MDFlatButton(text="Cancel", on_press=self.on_cancel),
            MDFlatButton(text="Search", on_press=self.on_search)
            ]
        kwargs["auto_dismiss"] = False
        super().__init__(**kwargs)
        self._callback = callback
    
    def on_cancel(self, *args):
        self.dismiss()
    
    def on_search(self, *args):
        self._callback(self.content_cls.ids.id_search_text.text, 0.0, 0.0)
        #self.dismiss()
    


