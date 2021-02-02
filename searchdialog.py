from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivy.lang import Builder

Builder.load_string("""
<SearchContent>:
    orientation: "vertical"
    MDTextField:
        text: ""
        hint_text: "Search Address"
        id: id_search
        on_text: root.on_text(self, self.text)
""")

class SearchContent(MDBoxLayout):
    
    def on_search_button(self):
        print("help")
    
    def on_text(self, textfield, text):
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
        self.dismiss()
    


