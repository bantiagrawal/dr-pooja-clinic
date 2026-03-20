import os, threading
from datetime import datetime
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from mobile.services.api_client import api
from mobile.services.storage import clear_tokens

ASSETS   = os.path.join(os.path.dirname(__file__), '..', 'assets')
PHOTO_SM = os.path.join(ASSETS, 'dr_pooja_circle.png')
PURPLE    = [0.43, 0.29, 0.89, 1]
PURPLE_BG = [0.93, 0.90, 0.99, 1]
PEACH_BG  = [1.00, 0.93, 0.88, 1]
GREEN_BG  = [0.88, 0.96, 0.88, 1]
DARK      = [0.08, 0.08, 0.18, 1]
GRAY      = [0.50, 0.50, 0.60, 1]
WHITE     = [1, 1, 1, 1]
PAGE_BG   = [0.97, 0.97, 0.99, 1]
DEMO_APPTS = [
    {'day':'23','month':'Mar','time':'10:00 AM','duration':'30 min','type':'General Checkup'},
    {'day':'25','month':'Mar','time':'02:30 PM','duration':'15 min','type':'Follow-up Consult'},
]

def mdc(bg=None, radius=16, padding=12, **kw):
    return MDCard(md_bg_color=bg or WHITE, radius=[dp(radius)],
                  elevation=0, padding=dp(padding), **kw)

class HomeScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = 'home'
        self._build()

    def _build(self):
        root = FloatLayout()
        with root.canvas.before:
            Color(*PAGE_BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg,'pos',root.pos),
                  size=lambda *a: setattr(self._bg,'size',root.size))
        sv = ScrollView(size_hint=(1,1), do_scroll_x=False)
        col = MDBoxLayout(orientation='vertical', adaptive_height=True,
                          spacing=dp(14), padding=[dp(18),dp(50),dp(18),dp(24)])

        # Header
        hdr = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(64), spacing=dp(8))
        txt = MDBoxLayout(orientation='vertical', size_hint_x=1, size_hint_y=None, height=dp(64))
        self.greet_lbl = MDLabel(text='Good morning!', font_style='Caption',
                                 theme_text_color='Custom', text_color=GRAY,
                                 size_hint_y=None, height=dp(22))
        self.name_lbl  = MDLabel(text='Welcome Back', font_style='H6', bold=True,
                                 theme_text_color='Custom', text_color=DARK,
                                 size_hint_y=None, height=dp(34))
        txt.add_widget(self.greet_lbl); txt.add_widget(self.name_lbl)
        av = MDCard(md_bg_color=WHITE, radius=[dp(24)], elevation=1, padding=dp(3),
                    size_hint=(None,None), size=(dp(48),dp(48)))
        av.add_widget(Image(source=PHOTO_SM, allow_stretch=True, keep_ratio=True))
        hdr.add_widget(txt); hdr.add_widget(av)
        hdr.add_widget(MDFlatButton(text='Logout', size_hint=(None,1), width=dp(60),
                                    theme_text_color='Custom', text_color=GRAY,
                                    on_release=self.logout))
        col.add_widget(hdr)

        # Stats
        stats = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(74), spacing=dp(10))
        for v,l,bg in [('2','Upcoming',PURPLE_BG),('5','Completed',GREEN_BG),('15+','Yrs Exp.',PEACH_BG)]:
            c = mdc(bg=bg, radius=14, padding=8, size_hint=(1,1))
            b = MDBoxLayout(orientation='vertical')
            b.add_widget(MDLabel(text=v, font_style='H5', bold=True, halign='center',
                                 theme_text_color='Custom', text_color=DARK))
            b.add_widget(MDLabel(text=l, font_style='Caption', halign='center',
                                 theme_text_color='Custom', text_color=GRAY))
            c.add_widget(b); stats.add_widget(c)
        col.add_widget(stats)

        # Quick Actions
        col.add_widget(MDLabel(text='Quick Actions', font_style='Subtitle1', bold=True,
                               theme_text_color='Custom', text_color=DARK,
                               size_hint_y=None, height=dp(28)))
        chips = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(46), spacing=dp(10))
        for emoji,label,bg,dest in [('📅','Book Slot',PURPLE_BG,'book'),
                                     ('🩺','Checkup',PEACH_BG,None),
                                     ('💬','Consult',GREEN_BG,None)]:
            chip = mdc(bg=bg, radius=22, padding=0, size_hint=(None,None), size=(dp(108),dp(42)))
            r = MDBoxLayout(spacing=dp(4), padding=[dp(10),0,dp(8),0])
            r.add_widget(MDLabel(text=emoji, font_size=dp(16), size_hint=(None,1), width=dp(22)))
            r.add_widget(MDLabel(text=label, font_style='Caption', bold=True,
                                 theme_text_color='Custom', text_color=DARK))
            chip.add_widget(r)
            if dest:
                chip.add_widget(MDFlatButton(size_hint=(1,1), md_bg_color=(0,0,0,0),
                    on_release=lambda *a,d=dest: setattr(self.manager,'current',d)))
            chips.add_widget(chip)
        col.add_widget(chips)

        # Doctor card — height=152, padding=12 → content area=128dp, photo=104dp
        doc = mdc(radius=20, padding=12, size_hint_y=None, height=dp(152))
        doc_row = MDBoxLayout(orientation='horizontal', spacing=dp(12))
        ph = MDCard(md_bg_color=WHITE, radius=[dp(14)], elevation=0, padding=dp(2),
                    size_hint=(None,None), size=(dp(90),dp(128)))
        ph.add_widget(Image(source=PHOTO_SM, allow_stretch=True, keep_ratio=True))
        doc_row.add_widget(ph)
        info = MDBoxLayout(orientation='vertical', spacing=dp(4), size_hint_x=1,
                           padding=[dp(4),dp(4),0,dp(4)])
        info.add_widget(MDLabel(text='Dr. Pooja Agrawal', font_style='Subtitle1', bold=True,
                                theme_text_color='Custom', text_color=DARK,
                                size_hint_y=None, height=dp(24)))
        info.add_widget(MDLabel(text='MBBS  •  General Physician',
                                font_style='Caption', theme_text_color='Custom', text_color=GRAY,
                                size_hint_y=None, height=dp(16)))
        info.add_widget(MDLabel(text='15+ Yrs  •  Apollo  •  BGS',
                                font_style='Caption', theme_text_color='Custom',
                                text_color=[0.55,0.40,0.85,1], size_hint_y=None, height=dp(16)))
        info.add_widget(MDLabel(text='⭐⭐⭐⭐⭐  NIMHANS  •  Railways',
                                font_style='Caption', theme_text_color='Custom',
                                text_color=[0.55,0.40,0.85,1], size_hint_y=None, height=dp(16)))
        info.add_widget(MDRaisedButton(text='Book Appointment', md_bg_color=PURPLE,
                                       size_hint=(1,None), height=dp(32),
                                       on_release=lambda *a: setattr(self.manager,'current','book')))
        doc_row.add_widget(info); doc.add_widget(doc_row); col.add_widget(doc)

        # Appointments header
        ah = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        ah.add_widget(MDLabel(text='Upcoming Appointments', font_style='Subtitle1', bold=True,
                              theme_text_color='Custom', text_color=DARK))
        ah.add_widget(MDFlatButton(text='View All', size_hint=(None,1), width=dp(72),
                                   theme_text_color='Custom', text_color=PURPLE,
                                   on_release=lambda *a: setattr(self.manager,'current','appointments')))
        col.add_widget(ah)
        self.appt_col = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing=dp(10))
        col.add_widget(self.appt_col)

        # Fees
        col.add_widget(MDLabel(text='Consultation Fees', font_style='Subtitle1', bold=True,
                               theme_text_color='Custom', text_color=DARK,
                               size_hint_y=None, height=dp(28)))
        fees = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(82), spacing=dp(12))
        for dur,price,bg in [('15 min','$30',PURPLE_BG),('30 min','$50',PEACH_BG)]:
            fc = mdc(bg=bg, radius=16, padding=14, size_hint=(1,1))
            fb = MDBoxLayout(orientation='vertical', spacing=dp(2))
            fb.add_widget(MDLabel(text=price, font_style='H5', bold=True,
                                  theme_text_color='Custom', text_color=DARK,
                                  size_hint_y=None, height=dp(36)))
            fb.add_widget(MDLabel(text=f'In-person  •  {dur}', font_style='Caption',
                                  theme_text_color='Custom', text_color=GRAY,
                                  size_hint_y=None, height=dp(18)))
            fc.add_widget(fb); fees.add_widget(fc)
        col.add_widget(fees)

        sv.add_widget(col); root.add_widget(sv); self.add_widget(root)
        Clock.schedule_once(lambda dt: self._load_demo(), 0.2)

    def _appt_card(self, a):
        # height=96, padding=10 → content area=76dp — fits all content
        card = mdc(radius=16, padding=10, size_hint_y=None, height=dp(96))
        row = MDBoxLayout(orientation='horizontal', spacing=dp(10))
        db = MDCard(md_bg_color=PURPLE_BG, radius=[dp(10)], elevation=0, padding=dp(6),
                    size_hint=(None,None), size=(dp(56),dp(76)))
        dc = MDBoxLayout(orientation='vertical')
        dc.add_widget(MDLabel(text=a['day'], font_style='H6', bold=True, halign='center',
                              theme_text_color='Custom', text_color=PURPLE))
        dc.add_widget(MDLabel(text=a['month'], font_style='Caption', halign='center',
                              theme_text_color='Custom', text_color=GRAY))
        db.add_widget(dc); row.add_widget(db)
        det = MDBoxLayout(orientation='vertical', spacing=dp(3), size_hint_x=1,
                          padding=[0,dp(6),0,0])
        det.add_widget(MDLabel(text=a['type'], font_style='Body2', bold=True,
                               theme_text_color='Custom', text_color=DARK,
                               size_hint_y=None, height=dp(20)))
        det.add_widget(MDLabel(text=f"{a['time']}  •  {a['duration']}",
                               font_style='Caption', theme_text_color='Custom', text_color=GRAY,
                               size_hint_y=None, height=dp(16)))
        det.add_widget(MDLabel(text='Dr. Pooja Agrawal', font_style='Caption',
                               theme_text_color='Custom', text_color=[0.55,0.40,0.85,1],
                               size_hint_y=None, height=dp(16)))
        badge = MDCard(md_bg_color=GREEN_BG, radius=[dp(10)], elevation=0,
                       size_hint=(None,None), size=(dp(68),dp(22)), padding=dp(2))
        badge.add_widget(MDLabel(text='Confirmed', halign='center', font_style='Caption',
                                 theme_text_color='Custom', text_color=[0.15,0.55,0.25,1]))
        det.add_widget(badge)
        row.add_widget(det)
        card.add_widget(row)
        return card
        row.add_widget(badge); card.add_widget(row)
        return card

    def _load_demo(self):
        for a in DEMO_APPTS:
            self.appt_col.add_widget(self._appt_card(a))

    def on_enter(self):
        h = datetime.now().hour
        self.greet_lbl.text = ('Good morning! ☀️' if h<12 else
                               'Good afternoon! 👋' if h<17 else 'Good evening! 🌙')
        threading.Thread(target=self._load_api, daemon=True).start()

    def _load_api(self):
        try:
            user = api.get_my_profile()
            Clock.schedule_once(lambda dt,u=user: self._set_name(u))
        except Exception:
            pass

    def _set_name(self, user):
        first = (user.get('full_name') or '').split()[0] or 'there'
        self.name_lbl.text = f'Hello, {first}!'

    def logout(self, *args):
        clear_tokens(); api.clear_tokens()
        self.manager.current = 'login'
