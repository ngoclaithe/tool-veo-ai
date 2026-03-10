from tkinter import ttk
from src.constants import BG, CARD, MUTED, ACCENT

def setup_style():
    """Thiết lập ttk.Style cho dark theme"""
    s = ttk.Style()
    s.theme_use("clam")
    # Notebook
    s.configure("TNotebook", background=BG, borderwidth=0)
    s.configure("TNotebook.Tab", background=CARD, foreground=MUTED,
                padding=[14, 6], font=("Segoe UI", 9, "bold"))
    s.map("TNotebook.Tab",
          background=[("selected", ACCENT)],
          foreground=[("selected", "white")])
    # Progressbar
    s.configure("TProgressbar", troughcolor=CARD, background=ACCENT,
                borderwidth=0, thickness=6)
    # Frame/LabelFrame
    s.configure("Dark.TFrame", background=BG)
    s.configure("Card.TFrame", background=CARD)
