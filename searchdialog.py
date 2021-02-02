from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineIconListItem
from kivy.lang import Builder
from kivy.metrics import dp


Builder.load_string("""
<SearchContent>:
    orientation: "vertical"
    size_hint: 1, None
    height: "300dp"
    MDTextField:
        size_hint: 1, .2
        text: ""
        hint_text: "Search Address"
        id: id_search
        on_text: root.on_text(self, self.text)
    ScrollView:
        size_hint: 1, None
        height: 0
        id: id_scroll_view
        MDList:
            canvas.before:
                Color:
                    rgba: 1, 0, 0, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            size_hint: 1, 1
            id: id_search_list
""")

class SearchContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_text(self, textfield, text):
        self.ids.id_scroll_view.size_hint_y = 1
        self.ids.id_search.add_widget(
            OneLineIconListItem(text=text)
            )
        print(text)


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
        self._callback(self.content_cls.ids.id_search.text, 0.0, 0.0)
        #self.dismiss()
    


