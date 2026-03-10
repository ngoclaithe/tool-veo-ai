from tkinter import *
from tkinter import scrolledtext, filedialog
from pathlib import Path
from src.constants import BG, CARD, TEXT, ACCENT, RED
from src.ui.components.base import UIBase

class LogsTab(Frame, UIBase):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        btn_f = Frame(self, bg=BG); btn_f.pack(fill=X, padx=10, pady=6)
        self._btn(btn_f, "🗑 Xóa log", lambda: (
            self.log_text.config(state=NORMAL),
            self.log_text.delete("1.0", END),
            self.log_text.config(state=DISABLED)
        ), color="#21262D").pack(side=LEFT, ipady=5, padx=(0,4))
        self._btn(btn_f, "⏹ Dừng tiến trình",
                  lambda: setattr(self.app, "running", False),
                  color=RED).pack(side=LEFT, ipady=5, padx=(0,4))
        self._btn(btn_f, "💾 Lưu log ra file TXT",
                  self._save_log, color="#21262D").pack(side=LEFT, ipady=5)

        self.log_text = scrolledtext.ScrolledText(
            self, font=("Consolas", 9), state=DISABLED,
            bg="#0D1117", fg="#C9D1D9",
            insertbackground=TEXT, relief="flat",
            selectbackground=ACCENT)
        self.log_text.pack(fill=BOTH, expand=True, padx=10, pady=(0,10))

    def _save_log(self):
        p = filedialog.asksaveasfilename(defaultextension=".txt",
                                          filetypes=[("Text", "*.txt")])
        if p:
            self.log_text.config(state=NORMAL)
            content = self.log_text.get("1.0", END)
            self.log_text.config(state=DISABLED)
            Path(p).write_text(content, encoding="utf-8")
            self.app.log(f"✅ Đã lưu log: {p}")

    def log(self, msg):
        def _do():
            self.log_text.config(state=NORMAL)
            self.log_text.insert(END, msg + "\n")
            self.log_text.see(END)
            self.log_text.config(state=DISABLED)
        self.app.root.after(0, _do)
