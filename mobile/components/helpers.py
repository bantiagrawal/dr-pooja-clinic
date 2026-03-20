"""Shared UI helpers."""
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel


def show_snackbar(text: str, duration: float = 3):
    """Show a simple one-line snackbar — compatible with KivyMD 1.2.0."""
    MDSnackbar(
        MDLabel(text=text, theme_text_color="Custom", text_color="white"),
        duration=duration,
    ).open()
