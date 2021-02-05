from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from debug import Debug
import global_props

Builder.load_string("""
<LogButton@MDIconButton>:
    size_hint_x: None
    width: dp(100)

<LogScreen>:
    log_container: id_log_container
    LogContainer:
        orientation: "vertical"
        id: id_log_container
        log: id_log_text.text

        MDToolbar:
            title: "Logs"
            right_action_items: [["refresh", id_log_container.on_refresh_button], ["delete", id_log_container.on_clear_button], ["alien", id_log_container.on_fake_entries]]
            md_bg_color: app.theme_cls.primary_color
            id: id_title_toolbar
        
        ScrollView:
            scroll_type: ["content", "bars"]
            id: id_scrollview
            MDTextField:
                multiline: True
                text: id_log_container.log
                id: id_log_text
""")

class LogScreen(MDScreen):

    log_container = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
    
    def on_enter(self, *args):
        log = Debug.getlogfromfile()
        if log:
            self.log_container.log = log
        return super().on_enter(*args)

class LogContainer(MDBoxLayout):

    log = StringProperty("")

    def on_clear_button(self, *args):
        self.log = ""
        global_props.delete_file(global_props.LOG_PATH)
    
    def on_fake_entries(self, *args):
        for x in range(10):
            Debug.log_file(f"Test{x}", "on_fake_entries", f"Test number {x}")
        log = Debug.getlogfromfile()
        if log:
            self.log = log
    
    def on_refresh_button(self, *args):
        log = Debug.getlogfromfile()
        if log:
            self.log = log

    