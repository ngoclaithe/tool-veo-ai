from tkinter import *
from src.constants import CARD, ACCENT, TEXT

class UIBase:
    def _card(self, parent, title, **kw):
        return LabelFrame(parent, text=f"  {title}  ",
                          font=("Segoe UI", 9, "bold"),
                          bg=CARD, fg=ACCENT, bd=1, relief="groove",
                          labelanchor="nw", **kw)

    def _btn(self, parent, text, cmd, color=None, **kw):
        clr = color or ACCENT
        return Button(parent, text=text, command=cmd,
                      bg=clr, fg="white", font=("Segoe UI", 9, "bold"),
                      relief="flat", cursor="hand2",
                      activebackground=clr, activeforeground="white",
                      bd=0, **kw)

    def _lbl(self, parent, text, size=9, bold=False, color=None, **kw):
        return Label(parent, text=text,
                     font=("Segoe UI", size, "bold" if bold else "normal"),
                     bg=CARD, fg=color or TEXT, **kw)
