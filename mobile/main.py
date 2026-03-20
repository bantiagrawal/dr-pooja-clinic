"""
Dr. Pooja Agrawal Clinic — KivyMD Mobile App Entry Point
"""
import sys
import os

# Ensure the project root is on the path so 'mobile' is importable as a package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.metrics import dp

from mobile.screens.login_screen import LoginScreen
from mobile.screens.home_screen import HomeScreen
from mobile.screens.book_screen import BookScreen
from mobile.screens.appointments_screen import AppointmentsScreen
from mobile.screens.profile_screen import ProfileScreen
from mobile.services.api_client import api
from mobile.services.storage import load_tokens

# Simulate phone dimensions on desktop during development
Window.size = (390, 844)


class DrPoojaClinicApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.primary_hue = "600"
        self.theme_cls.accent_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"
        self.title = "Dr. Pooja Agrawal"

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(LoginScreen())
        sm.add_widget(HomeScreen())
        sm.add_widget(BookScreen())
        sm.add_widget(AppointmentsScreen())
        sm.add_widget(ProfileScreen())

        # Auto-login if tokens exist
        access, refresh = load_tokens()
        if access and refresh:
            api.set_tokens(access, refresh)
            sm.current = "home"
        else:
            sm.current = "login"

        return sm

    def on_start(self):
        """Called after the app window is ready."""
        pass


if __name__ == "__main__":
    DrPoojaClinicApp().run()
