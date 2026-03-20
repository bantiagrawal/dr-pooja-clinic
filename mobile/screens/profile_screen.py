"""Profile screen — view and edit patient profile."""
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
import threading

from mobile.services.api_client import api
from mobile.components.helpers import show_snackbar

from mobile.services.api_client import api


class ProfileScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "profile"
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="My Profile",
            left_action_items=[["arrow-left", lambda x: setattr(self.manager, "current", "home")]],
            md_bg_color=(0.96, 0.26, 0.45, 1),
        )
        root.add_widget(toolbar)

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(24),
            adaptive_height=True,
        )

        self.name_field = MDTextField(hint_text="Full Name", size_hint_y=None, height=dp(56))
        self.email_field = MDTextField(hint_text="Email", size_hint_y=None, height=dp(56), readonly=True)
        self.phone_field = MDTextField(hint_text="Phone Number", size_hint_y=None, height=dp(56))

        content.add_widget(MDLabel(text="Account Details", font_style="H6", size_hint_y=None, height=dp(40)))
        content.add_widget(self.name_field)
        content.add_widget(self.email_field)
        content.add_widget(self.phone_field)

        self.provider_label = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(30),
        )
        content.add_widget(self.provider_label)

        save_btn = MDRaisedButton(
            text="Save Changes",
            size_hint_x=1,
            md_bg_color=(0.96, 0.26, 0.45, 1),
            on_release=self._save,
        )
        content.add_widget(save_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        threading.Thread(target=self._load_profile, daemon=True).start()

    def _load_profile(self):
        try:
            user = api.get_my_profile()
            Clock.schedule_once(lambda dt, u=user: self._populate(u))
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): show_snackbar(f"Error: {err}"))

    def _populate(self, user: dict):
        self.name_field.text  = user.get("full_name", "")
        self.email_field.text = user.get("email", "")
        self.phone_field.text = user.get("phone") or ""
        self.provider_label.text = f"Signed in via {user.get('provider', '').capitalize()}"

    def _save(self, *args):
        def _do():
            try:
                api.update_profile(
                    full_name=self.name_field.text.strip(),
                    phone=self.phone_field.text.strip() or None,
                )
                Clock.schedule_once(lambda dt: show_snackbar("Profile updated!"))
            except Exception as e:
                Clock.schedule_once(lambda dt, err=str(e): show_snackbar(f"Error: {err}"))
        threading.Thread(target=_do, daemon=True).start()
