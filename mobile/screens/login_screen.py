"""
Login screen: name+bio top, photo middle (proper ratio), login buttons bottom.
"""
import os, threading
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
import webbrowser
from mobile.services.api_client import api
from mobile.services.storage import save_tokens

ASSETS     = os.path.join(os.path.dirname(__file__), '..', 'assets')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'images')
PHOTO_PATH = os.path.join(IMAGES_DIR, 'dr_pooja_profile.png')

PURPLE = [0.43, 0.29, 0.89, 1]
PURPLE_L = [0.93, 0.90, 0.99, 1]
DARK   = [0.08, 0.08, 0.18, 1]
GRAY   = [0.50, 0.50, 0.60, 1]
WHITE  = [1, 1, 1, 1]
BG     = [0.97, 0.97, 0.99, 1]


class LoginScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = 'login'
        self._build()

    def _build(self):
        # White page background
        root = MDBoxLayout(orientation='vertical')
        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, 'pos', root.pos),
                  size=lambda *a: setattr(self._bg, 'size', root.size))

        # ── TOP: name + bio (~22% height) ────────────────────────────────────
        top = MDBoxLayout(
            orientation='vertical', spacing=dp(4),
            padding=[dp(24), dp(36), dp(24), dp(8)],
            size_hint=(1, 0.22)
        )
        top.add_widget(MDLabel(
            text='Dr. Pooja Agrawal', font_style='H5', bold=True,
            halign='center', theme_text_color='Custom', text_color=DARK,
            size_hint_y=None, height=dp(40)
        ))
        top.add_widget(MDLabel(
            text='MBBS  •  General Physician  •  15+ Years',
            font_style='Body2', halign='center',
            theme_text_color='Custom', text_color=GRAY,
            size_hint_y=None, height=dp(24)
        ))
        top.add_widget(MDLabel(
            text='Apollo  •  BGS Global  •  NIMHANS  •  Railways',
            font_style='Caption', halign='center',
            theme_text_color='Custom', text_color=[0.55, 0.45, 0.80, 1],
            size_hint_y=None, height=dp(20)
        ))
        root.add_widget(top)

        # ── MIDDLE: photo (keep ratio, centered, ~52% height) ─────────────────
        photo_wrap = FloatLayout(size_hint=(1, 0.52))
        photo_wrap.add_widget(Image(
            source=PHOTO_PATH,
            allow_stretch=True, keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        ))
        root.add_widget(photo_wrap)

        # ── BOTTOM: login buttons (~26% height) ───────────────────────────────
        bottom = MDBoxLayout(
            orientation='vertical', spacing=dp(10),
            padding=[dp(32), dp(12), dp(32), dp(24)],
            size_hint=(1, 0.26)
        )

        # Divider label
        bottom.add_widget(MDLabel(
            text='Sign in to book appointments',
            halign='center', font_style='Caption',
            theme_text_color='Custom', text_color=GRAY,
            size_hint_y=None, height=dp(18)
        ))

        # Google button
        bottom.add_widget(MDRaisedButton(
            text='  G   Continue with Google',
            md_bg_color=[1, 1, 1, 1],
            theme_text_color='Custom', text_color=[0.2, 0.2, 0.2, 1],
            size_hint=(1, None), height=dp(46),
            elevation=2,
            on_release=self.login_google
        ))

        # Facebook button
        bottom.add_widget(MDRaisedButton(
            text='  f   Continue with Facebook',
            md_bg_color=[0.23, 0.35, 0.70, 1],
            theme_text_color='Custom', text_color=WHITE,
            size_hint=(1, None), height=dp(46),
            elevation=2,
            on_release=self.login_facebook
        ))

        # Demo link
        demo_row = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(32)
        )
        demo_row.add_widget(MDFlatButton(
            text='Skip — Quick Demo Login',
            theme_text_color='Custom', text_color=PURPLE,
            size_hint_x=1, on_release=self.login_demo
        ))
        bottom.add_widget(demo_row)

        self.status_label = MDLabel(
            text='', halign='center', font_style='Caption',
            theme_text_color='Custom', text_color=[0.85, 0.20, 0.20, 1],
            size_hint_y=None, height=dp(16)
        )
        bottom.add_widget(self.status_label)

        root.add_widget(bottom)
        self.add_widget(root)

    # ── Auth ──────────────────────────────────────────────────────────────────

    def login_demo(self, *args):
        import requests as req
        base = os.getenv('BACKEND_URL', 'http://localhost:8000')
        self.status_label.text = 'Signing in...'
        def _fetch():
            try:
                r = req.get(f'{base}/api/dev/token', params={'user_id': 1}, timeout=5)
                r.raise_for_status()
                d = r.json()
                save_tokens(d['access_token'], d['refresh_token'])
                api.set_tokens(d['access_token'], d['refresh_token'])
                Clock.schedule_once(lambda dt: self._ok())
            except Exception as e:
                Clock.schedule_once(lambda dt, err=str(e): self._err(err))
        threading.Thread(target=_fetch, daemon=True).start()

    def login_google(self, *args):
        try:
            webbrowser.open(api.get_google_auth_url('drpooja://auth/google'))
            self.status_label.text = 'Complete sign-in in browser...'
        except Exception as e:
            self._err(str(e))

    def login_facebook(self, *args):
        try:
            webbrowser.open(api.get_facebook_auth_url('drpooja://auth/facebook'))
            self.status_label.text = 'Complete sign-in in browser...'
        except Exception as e:
            self._err(str(e))

    def _ok(self):
        self.status_label.text = ''
        self.manager.current = 'home'

    def _err(self, e):
        self.status_label.text = f'Error: {e}'