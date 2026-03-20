"""Appointments screen — view and cancel upcoming appointments."""
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
import threading

from mobile.services.api_client import api
from mobile.components.helpers import show_snackbar

STATUS_COLORS = {
    "confirmed": (0.2, 0.78, 0.35, 1),
    "pending":   (0.96, 0.62, 0.04, 1),
    "cancelled": (0.6, 0.6, 0.6, 1),
    "completed": (0.26, 0.52, 0.96, 1),
}


class AppointmentsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "appointments"
        self._cancel_dialog = None
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="My Appointments",
            left_action_items=[["arrow-left", lambda x: setattr(self.manager, "current", "home")]],
            right_action_items=[["refresh", self.on_enter]],
            md_bg_color=(0.96, 0.26, 0.45, 1),
        )
        root.add_widget(toolbar)

        scroll = ScrollView()
        self.list_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(16),
            adaptive_height=True,
        )
        scroll.add_widget(self.list_container)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self, *args):
        self.list_container.clear_widgets()
        self.list_container.add_widget(MDLabel(
            text="Loading…",
            halign="center",
            font_style="Body2",
            theme_text_color="Hint",
        ))
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        try:
            appts = api.get_my_appointments()
            Clock.schedule_once(lambda dt: self._render(appts))
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._show_error(err))

    def _render(self, appts: list):
        self.list_container.clear_widgets()
        if not appts:
            self.list_container.add_widget(MDLabel(
                text="No appointments yet.\nBook one now!",
                halign="center",
                font_style="Body1",
            ))
            return
        for appt in appts:
            self.list_container.add_widget(self._appt_card(appt))

    def _appt_card(self, appt: dict) -> MDCard:
        status = appt["status"]
        color = STATUS_COLORS.get(status, (0.8, 0.8, 0.8, 1))
        slot = appt["slot"]

        card = MDCard(
            padding=dp(16),
            size_hint_y=None,
            height=dp(140),
            elevation=3,
            radius=[dp(12)],
        )
        inner = MDBoxLayout(orientation="vertical", spacing=dp(4))
        inner.add_widget(MDLabel(
            text=f"{slot['slot_date']}  •  {slot['start_time'][:5]}–{slot['end_time'][:5]}",
            font_style="Subtitle1",
        ))
        inner.add_widget(MDLabel(
            text=f"{slot['duration_minutes']} min  •  ${slot['price_usd']}",
            font_style="Body2",
            theme_text_color="Secondary",
        ))
        status_label = MDLabel(
            text=f"● {status.upper()}",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=color,
        )
        inner.add_widget(status_label)

        if appt.get("reason"):
            inner.add_widget(MDLabel(
                text=f"Reason: {appt['reason']}",
                font_style="Caption",
                theme_text_color="Hint",
            ))

        if status == "confirmed":
            cancel_btn = MDFlatButton(
                text="CANCEL",
                theme_text_color="Custom",
                text_color=(0.9, 0.2, 0.2, 1),
                on_release=lambda *a, ap=appt: self._ask_cancel(ap),
            )
            inner.add_widget(cancel_btn)

        card.add_widget(inner)
        return card

    def _ask_cancel(self, appt: dict):
        slot = appt["slot"]
        self._cancel_dialog = MDDialog(
            title="Cancel Appointment?",
            text=f"Cancel your appointment on {slot['slot_date']} at {slot['start_time'][:5]}?",
            buttons=[
                MDFlatButton(text="NO", on_release=lambda *a: self._cancel_dialog.dismiss()),
                MDRaisedButton(
                    text="YES, CANCEL",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda *a, ap=appt: self._do_cancel(ap),
                ),
            ],
        )
        self._cancel_dialog.open()

    def _do_cancel(self, appt: dict):
        if self._cancel_dialog:
            self._cancel_dialog.dismiss()
        threading.Thread(target=self._cancel_request, args=(appt["id"],), daemon=True).start()

    def _cancel_request(self, appt_id: int):
        try:
            api.cancel_appointment(appt_id)
            Clock.schedule_once(lambda dt: (show_snackbar("Appointment cancelled."), self.on_enter()))
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._show_error(err))

    def _show_error(self, msg: str):
        show_snackbar(f"Error: {msg}")
