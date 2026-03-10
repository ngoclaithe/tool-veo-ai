import os
import threading
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from src.constants import BG, CARD, BORDER, TEXT, MUTED, ACCENT, GREEN
from src.automation.browser import BrowserController
from src.ui.styles import setup_style
from src.ui.components.base import UIBase

from src.ui.tabs.note_tab import NoteTab
from src.ui.tabs.browser_tab import BrowserTab
from src.ui.tabs.text2video_tab import Text2VideoTab
from src.ui.tabs.text2image_tab import Text2ImageTab
from src.ui.tabs.char_setup_tab import CharSetupTab
from src.ui.tabs.create_video_tab import CreateVideoTab
from src.ui.tabs.logs_tab import LogsTab
from src.ui.tabs.merge_tab import MergeTab

class VeoApp(UIBase):
    def __init__(self, root):
        self.root = root
        self.root.title("VEO 3 FLOW PRO  —  by TechViet AI")
        self.root.geometry("1060x700")
        self.root.resizable(True, True)
        self.root.configure(bg=BG)

        setup_style()

        # State
        self.bc = BrowserController(log_fn=self.log)
        self.running = False
        self.characters = {} # {name: path}

        self._build_ui()

    def log(self, msg):
        self.logs_tab.log(msg)

    def set_status(self, msg):
        self.status_var.set(msg)

    def _build_ui(self):
        # Header
        header = Frame(self.root, bg="#0A0F1A", height=60)
        header.pack(fill=X)
        header.pack_propagate(False)

        Label(header, text="VEO 3 FLOW PRO", font=("Segoe UI", 16, "bold"),
              bg="#0A0F1A", fg=ACCENT).pack(side=LEFT, padx=20)
        Label(header, text="v3.1.2 Premium Automation", font=("Segoe UI", 9, "italic"),
              bg="#0A0F1A", fg=MUTED).pack(side=LEFT, pady=(5,0))

        # Bottom Bar
        footer = Frame(self.root, bg="#0D1117", bd=1, relief="flat", height=32)
        footer.pack(side=BOTTOM, fill=X)
        self.status_var = StringVar(value="๏  Sẵn sàng")
        Label(footer, textvariable=self.status_var, font=("Segoe UI", 8),
              bg="#0D1117", fg=MUTED).pack(side=LEFT, padx=10)
        Label(footer, text="© 2024 TechViet AI Tool Division", font=("Segoe UI", 8),
              bg="#0D1117", fg="#30363D").pack(side=RIGHT, padx=10)

        # Tabs
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=BOTH, expand=True, padx=2, pady=2)

        self.note_tab = NoteTab(self.nb, self)
        self.browser_tab = BrowserTab(self.nb, self)
        self.t2v_tab = Text2VideoTab(self.nb, self)
        self.t2i_tab = Text2ImageTab(self.nb, self)
        self.char_tab = CharSetupTab(self.nb, self)
        self.cv_tab = CreateVideoTab(self.nb, self)
        self.logs_tab = LogsTab(self.nb, self)
        self.merge_tab = MergeTab(self.nb, self)

        self.nb.add(self.note_tab, text="📌 Hướng Dẫn")
        self.nb.add(self.browser_tab, text="🌐 Kết Nối")
        self.nb.add(self.t2v_tab, text="📝 Text to Video")
        self.nb.add(self.t2i_tab, text="🖼️ Tạo Ảnh")
        self.nb.add(self.char_tab, text="👤 Nhân Vật")
        self.nb.add(self.cv_tab, text="🎞️ Tạo Video")
        self.nb.add(self.logs_tab, text="📋 Logs")
        self.nb.add(self.merge_tab, text="🎬 Ghép Video")

        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, evt):
        idx = self.nb.index(self.nb.select())
        if idx == 5: # Create Video tab
            self.cv_tab.refresh_char_display()

    def _refresh_char_display(self):
        self.cv_tab.refresh_char_display()

    def _browse(self, entry_widget):
        d = filedialog.askdirectory()
        if d:
            entry_widget.delete(0, END)
            entry_widget.insert(0, d)

    def _run_bg(self, fn):
        if self.running:
            self.log("⚠ Đang chạy rồi — chờ hoàn tất trước!")
            return
        threading.Thread(target=fn, daemon=True).start()

    def _stop(self):
        self.running = False
        self.log("⏹ Đang yêu cầu dừng...")

    def _log_summary(self, mode_name, results, out_dir):
        total = len(results)
        ok_list = [r for r in results if '✅' in r[2]]
        fail_list = [r for r in results if '❌' in r[2] or '⚠' in r[2]]
        stop_list = [r for r in results if '⏹' in r[2]]

        self.log(f"\n{'═'*60}")
        self.log(f"📊  TỔNG KẾT — {mode_name}")
        self.log(f"{'═'*60}")
        self.log(f"   Tổng: {total}  |  ✅ Thành công: {len(ok_list)}  |  ❌ Lỗi: {len(fail_list)}  |  ⏹ Dừng: {len(stop_list)}")
        self.log(f"   📂 Thư mục: {out_dir}")

        if ok_list:
            self.log(f"\n   ── ✅ THÀNH CÔNG ({len(ok_list)}) ──")
            for idx, short, status, fname in ok_list:
                self.log(f"   #{idx:02d}  {fname}  ←  {short}")

        if fail_list:
            self.log(f"\n   ── ❌ THẤT BẠI ({len(fail_list)}) ──")
            for idx, short, status, fname in fail_list:
                self.log(f"   #{idx:02d}  {status}  ←  {short}")

        if stop_list:
            self.log(f"\n   ── ⏹ DỪNG ──")
            for idx, short, status, fname in stop_list:
                self.log(f"   #{idx:02d}  {status}  ←  {short}")

        self.log(f"{'═'*60}\n")
