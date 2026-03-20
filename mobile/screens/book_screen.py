"""Book appointment screen — browse slots and book."""
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
import threading

from mobile.services.api_client import api
from mobile.components.helpers import show_snackbar


class BookScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "book"
        self.selected_duration = None
        self.selected_slot = None
        self.slots = []
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Book Appointment",
            left_action_items=[["arrow-left", lambda x: setattr(self.manager, "current", "home")]],
            md_bg_color=(0.96, 0.26, 0.45, 1),
        )
        root.add_widget(toolbar)

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(20),
            adaptive_height=True,
        )

        # Duration filter chips
        content.add_widget(MDLabel(text="Select duration:", font_style="Subtitle1", size_hint_y=None, height=dp(36)))
        chip_row = MDBoxLayout(spacing=dp(10), size_hint_y=None, height=dp(40))
        self.chip_15 = MDRaisedButton(
            text="15 min — $30",
            on_release=lambda x: self._filter_duration(15),
        )
        self.chip_30 = MDRaisedButton(
            text="30 min — $50",
            on_release=lambda x: self._filter_duration(30),
        )
        chip_row.add_widget(self.chip_15)
        chip_row.add_widget(self.chip_30)
        content.add_widget(chip_row)

        content.add_widget(MDLabel(text="Available slots:", font_style="Subtitle1", size_hint_y=None, height=dp(36)))

        self.slots_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            adaptive_height=True,
        )
        content.add_widget(self.slots_container)

        self.reason_field = MDTextField(
            hint_text="Reason for visit (optional)",
            size_hint_y=None,
            height=dp(56),
            multiline=False,
        )
        content.add_widget(self.reason_field)

        self.book_btn = MDRaisedButton(
            text="Confirm Booking",
            size_hint_x=1,
            disabled=True,
            md_bg_color=(0.96, 0.26, 0.45, 1),
            on_release=self._confirm_booking,
        )
        content.add_widget(self.book_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self._load_slots()

    def _load_slots(self):
        def _fetch():
            try:
                slots = api.get_slots(duration=self.selected_duration)
                self.slots = slots
                Clock.schedule_once(lambda dt: self._render_slots(slots))
            except Exception as e:
                Clock.schedule_once(lambda dt, err=str(e): self._show_error(err))
        threading.Thread(target=_fetch, daemon=True).start()

    def _filter_duration(self, duration: int):
        self.selected_duration = duration
        self.selected_slot = None
        self.book_btn.disabled = True
        self._load_slots()

    def _render_slots(self, slots: list):
        self.slots_container.clear_widgets()
        if not slots:
            self.slots_container.add_widget(MDLabel(
                text="No available slots. Please check back later.",
                font_style="Body2",
                theme_text_color="Hint",
            ))
            return
        for slot in slots:
            self.slots_container.add_widget(self._slot_card(slot))

    def _slot_card(self, slot: dict) -> MDCard:
        card = MDCard(
            padding=dp(12),
            size_hint_y=None,
            height=dp(80),
            elevation=2,
            radius=[dp(10)],
            ripple_behavior=True,
        )
        inner = MDBoxLayout(orientation="vertical")
        date_str = slot["slot_date"]
        start = slot["start_time"][:5]
        end   = slot["end_time"][:5]
        dur   = slot["duration_minutes"]
        price = slot["price_usd"]
        inner.add_widget(MDLabel(
            text=f"{date_str}  •  {start} – {end}",
            font_style="Subtitle2",
        ))
        inner.add_widget(MDLabel(
            text=f"{dur} min  •  ${price}",
            font_style="Caption",
            theme_text_color="Secondary",
        ))

        def _select(*args, slot=slot):
            self.selected_slot = slot
            self.book_btn.disabled = False
            for child in self.slots_container.children:
                if hasattr(child, "md_bg_color"):
                    child.md_bg_color = (1, 1, 1, 1)
            card.md_bg_color = (0.96, 0.26, 0.45, 0.15)

        card.on_release = _select
        card.add_widget(inner)
        return card

    def _confirm_booking(self, *args):
        if not self.selected_slot:
            return
        slot_id = self.selected_slot["id"]
        reason = self.reason_field.text.strip() or None
        self.book_btn.disabled = True

        def _do_book():
            try:
                api.book_appointment(slot_id, reason)
                Clock.schedule_once(self._on_booked)
            except Exception as e:
                Clock.schedule_once(lambda dt, err=str(e): self._show_error(err))
                Clock.schedule_once(lambda dt: setattr(self.book_btn, "disabled", False))

        threading.Thread(target=_do_book, daemon=True).start()

    def _on_booked(self, dt=None):
        show_snackbar("✓ Appointment booked! Check your email.")
        self.manager.current = "appointments"

    def _show_error(self, msg: str):
        show_snackbar(f"Error: {msg}")
