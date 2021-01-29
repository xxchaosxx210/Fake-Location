from kivymd.app import MDApp
import pydroid

class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
    
    def on_start(self):
        self.root.ids["mock_status"].text = "AaaaaBBBBbbbbbbbCCCccxxc\n" * 100
        if pydroid.is_android():
            from android.permissions import request_permissions
            from android.permissions import Permission
            request_permissions([Permission.ACCESS_FINE_LOCATION])

def main():
    MainApp().run()

if __name__ == '__main__':
    main()