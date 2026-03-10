import os
import time
from pathlib import Path
from tkinter import *
from tkinter import messagebox, scrolledtext, ttk, filedialog
from src.constants import BG, CARD, TEXT, ACCENT, GREEN, MUTED
from src.ui.components.base import UIBase

class CharSetupTab(Frame, UIBase):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        # Hướng dẫn
        guide = self._card(self, "📋 Hướng dẫn")
        guide.pack(fill=X, padx=12, pady=(10,5))
        Label(guide, text=(
            "1. Chon anh nhan vat -> chon nhieu anh (khong gioi han)\n"
            "2. Dat ten ngan gon cho tung nhan vat  (VD: Alice, Bob, NhanVat1)\n"
            "3. Bam Upload tat ca len Flow - tool tu upload theo thu tu\n"
            "4. Sang tab Tao Video de generate video co nhan vat"
        ), bg=CARD, fg=TEXT, font=("Segoe UI", 9), justify=LEFT
        ).pack(anchor=W, padx=10, pady=8)

        # Danh sách nhân vật
        list_lf = self._card(self, "📂 Danh sách nhân vật  (tên: đường dẫn ảnh)")
        list_lf.pack(fill=BOTH, expand=True, padx=12, pady=5)
        self.char_list = scrolledtext.ScrolledText(
            list_lf, height=9, font=("Consolas", 9), state=DISABLED,
            bg="#0D1117", fg=TEXT, relief="flat")
        self.char_list.pack(fill=BOTH, expand=True, padx=4, pady=4)

        # Nút thao tác
        btn_f = Frame(self, bg=BG); btn_f.pack(fill=X, padx=12, pady=6)
        self._btn(btn_f, "  📁  Chọn ảnh nhân vật (nhiều ảnh)",
                  self._choose_char_images, color=ACCENT
                  ).pack(side=LEFT, fill=X, expand=True, ipady=8, padx=(0,4))
        self._btn(btn_f, "  ⬆️  Upload tất cả lên Flow",
                  self._upload_chars, color=GREEN
                  ).pack(side=LEFT, fill=X, expand=True, ipady=8, padx=(0,4))
        self._btn(btn_f, "  🗑  Xóa hết",
                  self._clear_chars, color="#444C56"
                  ).pack(side=LEFT, ipady=8, ipadx=6)

        # Progress upload
        up_f = self._card(self, "📤 Tiến độ upload")
        up_f.pack(fill=X, padx=12, pady=5)
        self.char_progress = ttk.Progressbar(up_f, mode="determinate", style="TProgressbar")
        self.char_progress.pack(fill=X, padx=8, pady=(6,2))
        self.char_status_lbl = Label(up_f, text="Chưa upload",
                                     font=("Segoe UI", 9), bg=CARD, fg=MUTED)
        self.char_status_lbl.pack(pady=(0,6))

    def _choose_char_images(self):
        paths = filedialog.askopenfilenames(
            title="Chọn ảnh nhân vật",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.jfif"), ("All", "*.*")]
        )
        if not paths: return
        self.app.characters.clear()
        for idx, p in enumerate(paths, 1):
            stem = Path(p).stem
            if len(stem) > 20 or '-' in stem:
                default_name = f"Nhan_vat_{idx}"
            else:
                default_name = stem
            name = self._ask_name(default_name)
            if name:
                self.app.characters[name] = p

        self.char_list.config(state=NORMAL)
        self.char_list.delete("1.0", END)
        for n, pth in self.app.characters.items():
            self.char_list.insert(END, f"{n}: {pth}\n")
        self.char_list.config(state=DISABLED)
        self.app.log(f"✅ Đã chọn {len(self.app.characters)} nhân vật: {', '.join(self.app.characters.keys())}")
        # Notify other tabs
        self.app._refresh_char_display()

    def _ask_name(self, default=""):
        dlg = Toplevel(self.app.root)
        dlg.title("Đặt tên nhân vật")
        dlg.geometry("360x150")
        dlg.configure(bg=BG)
        dlg.grab_set()
        Label(dlg, text=f"  Đặt tên nhân vật cho ảnh: {default[:40]}",
              font=("Segoe UI", 9), bg=BG, fg=TEXT).pack(pady=8, anchor=W, padx=10)
        var = StringVar(value=default)
        Entry(dlg, textvariable=var, width=32, font=("Segoe UI", 11), bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat").pack(pady=4, ipady=4)
        result = [None]
        def ok():
            v = var.get().strip()
            result[0] = v if v else None
            dlg.destroy()
        def on_close():
            result[0] = None; dlg.destroy()
        dlg.protocol("WM_DELETE_WINDOW", on_close)
        Button(dlg, text="OK", command=ok, bg=GREEN, fg="white", width=10).pack(pady=6)
        dlg.wait_window()
        return result[0]

    def _clear_chars(self):
        self.app.characters.clear()
        self.char_list.config(state=NORMAL)
        self.char_list.delete("1.0", END)
        self.char_list.config(state=DISABLED)
        self.app._refresh_char_display()

    def _upload_chars(self):
        if not self.app.characters:
            messagebox.showerror("Lỗi", "Chưa chọn ảnh nhân vật!")
            return
        if not self.app.bc.is_alive():
            messagebox.showerror("Lỗi", "Chưa mở Chrome!")
            return
        self.app._run_bg(self._upload_chars_worker)

    def _upload_chars_worker(self):
        names = list(self.app.characters.keys())
        total = len(names)
        self.app.root.after(0, lambda: self.char_progress.config(maximum=total, value=0))
        self.app.log(f"📤 Bắt đầu upload {total} ảnh nhân vật...")
        ok_count = 0
        for i, name in enumerate(names, 1):
            path = self.app.characters[name]
            self.app.log(f"📤 Upload [{i}/{total}]: {name} ({Path(path).name})")
            self.app.root.after(0, lambda l=f"Uploading {name}... ({i}/{total})": self.char_status_lbl.config(text=l))
            ok = self.app.bc.upload_image(path)
            if ok: ok_count += 1
            self.app.root.after(0, lambda v=i: self.char_progress.config(value=v))
            time.sleep(1.5)
        msg = f"✅ Upload xong {ok_count}/{total} nhân vật!"
        self.app.root.after(0, lambda: self.char_status_lbl.config(text=msg))
        self.app.log(msg)
