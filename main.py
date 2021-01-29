from kivymd.app import MDApp

class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"


def main():
    MainApp().run()

if __name__ == '__main__':
    main()