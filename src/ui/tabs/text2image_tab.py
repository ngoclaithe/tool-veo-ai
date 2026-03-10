import os
import time
import random
from tkinter import *
from tkinter import messagebox, scrolledtext, ttk
from src.constants import BG, CARD, TEXT, ACCENT, GREEN, RED, MUTED, OUTPUT_DIR_IMAGE
from src.ui.components.base import UIBase

class Text2ImageTab(Frame, UIBase):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        # Header
        hf = Frame(self, bg="#0A0F1A"); hf.pack(fill=X)
        Label(hf, text="🖼️  Text → Image  (Nano Banana 2 trên Flow)",
              font=("Segoe UI", 12, "bold"), bg="#0A0F1A", fg=ACCENT
              ).pack(anchor=W, padx=16, pady=10)

        # Prompt box
        lf = self._card(self, "📝 Danh sách Prompt  (mỗi dòng 1 ảnh)")
        lf.pack(fill=BOTH, expand=True, padx=12, pady=6)
        self.ti_prompts = scrolledtext.ScrolledText(
            lf, height=8, font=("Consolas", 9),
            bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.ti_prompts.pack(fill=BOTH, expand=True, padx=4, pady=4)
        self.ti_prompts.insert(END,
            "A cute cat sitting on a rainbow cloud, digital art\n"
            "A futuristic cityscape at sunset, cyberpunk style\n"
            "Portrait of a samurai warrior, watercolor painting")

        # Settings
        sf = self._card(self, "⚙️ Cài đặt")
        sf.pack(fill=X, padx=12, pady=4)
        r1 = Frame(sf, bg=CARD); r1.pack(fill=X, pady=3, padx=8)
        Label(r1, text="Tên file:", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side=LEFT)
        self.ti_base = Entry(r1, width=20, font=("Segoe UI", 9),
                             bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.ti_base.insert(0, "image")
        self.ti_base.pack(side=LEFT, padx=6, ipady=3)
        
        r2 = Frame(sf, bg=CARD); r2.pack(fill=X, pady=3, padx=8)
        Label(r2, text="Lưu tại:", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side=LEFT)
        self.ti_out = Entry(r2, width=55, font=("Segoe UI", 9),
                            bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.ti_out.insert(0, OUTPUT_DIR_IMAGE)
        self.ti_out.pack(side=LEFT, padx=6, ipady=3)
        self._btn(r2, "📂", lambda: self.app._browse(self.ti_out),
                  color="#21262D").pack(side=LEFT, ipady=3, ipadx=4)

        # Delay
        df = self._card(self, "⏱ Độ trễ giữa các prompt")
        df.pack(fill=X, padx=12, pady=4)
        df_r = Frame(df, bg=CARD); df_r.pack(anchor=W, padx=8, pady=4)
        self.ti_delay = StringVar(value="normal")
        for txt, val in [("Bình thường (5s)", "normal"),
                          ("Gấp đôi (10s)", "double"),
                          ("Ngẫu nhiên (6-15s)", "random")]:
            Radiobutton(df_r, text=txt, variable=self.ti_delay, value=val,
                        bg=CARD, fg=TEXT, selectcolor=BG,
                        activebackground=CARD, font=("Segoe UI", 9)
                        ).pack(side=LEFT, padx=8)

        # Timeout
        tf = self._card(self, "⬇️ Tự động chờ ảnh xong → Tải về ngay")
        tf.pack(fill=X, padx=12, pady=4)
        self.ti_timeout = StringVar(value="300")
        Label(tf, text="  ⏳  Chờ đến khi ảnh xong, tối đa 5 phút  →  Tải xuống ngay khi phát hiện hoàn tất",
              font=("Segoe UI", 9, "bold"), bg=CARD, fg=GREEN).pack(anchor=W, padx=12, pady=6)

        # Progress
        self.ti_progress = ttk.Progressbar(self, mode="indeterminate", style="TProgressbar")
        self.ti_progress.pack(fill=X, padx=12, pady=(6, 2))
        self.ti_status_lbl = Label(self, text="", font=("Segoe UI", 8), bg=BG, fg=MUTED)
        self.ti_status_lbl.pack()

        # Buttons
        btn_row = Frame(self, bg=BG); btn_row.pack(fill=X, padx=12, pady=8)
        self._btn(btn_row, "  ▶  START — Tạo ảnh tuần tự + Tải về",
                  self._start_text2image, color=GREEN
                  ).pack(side=LEFT, fill=X, expand=True, ipady=9, padx=(0, 4))
        self._btn(btn_row, "  ⏹  STOP",
                  self.app._stop, color=RED
                  ).pack(side=LEFT, ipady=9, ipadx=8)

    def _start_text2image(self):
        raw = self.ti_prompts.get("1.0", END).strip()
        lines = [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]
        if not lines:
            messagebox.showerror("Lỗi", "Chưa nhập prompt!")
            return
        if not self.app.bc.is_alive():
            messagebox.showerror("Lỗi", "Chưa mở Chrome!")
            return
        out_dir = self.ti_out.get()
        os.makedirs(out_dir, exist_ok=True)
        self.app.log(f"🖼️ Bắt đầu Text→Image: {len(lines)} prompt(s)")
        self.app.nb.select(6)
        self.app._run_bg(lambda: self._t2i_worker(lines, out_dir))

    def _t2i_worker(self, lines, out_dir):
        self.app.running = True
        self.app.root.after(0, self.ti_progress.start)
        results = []
        try:
            for i, prompt in enumerate(lines, 1):
                if not self.app.running:
                    results.append((i, prompt[:50], '⏹ Dừng', ''))
                    break

                short = prompt[:60]
                self.app.log(f"\n══ 🖼️ [{i}/{len(lines)}] {short}...")
                self.app.root.after(0, lambda ii=i, t=len(lines), p=short:
                    self.ti_status_lbl.config(text=f"🖼️ [{ii}/{t}] {p}..."))

                delay_map = {"normal": 5, "double": 10, "random": None}
                d_val = delay_map.get(self.ti_delay.get(), 5)
                delay = d_val if d_val is not None else random.randint(6, 15)

                if i == 1:
                    self.app.bc.new_project()
                    time.sleep(2)
                else:
                    ready = self.app.bc.wait_for_prompt_ready(timeout=60)
                    if not ready:
                        self.app.bc.new_project()
                        time.sleep(2)

                ok = self.app.bc.set_prompt(prompt)
                if ok:
                    self.app.bc.click_generate()
                    fname = f"{self.ti_base.get()}_{i:02d}.png"
                    dl_ok = self.app.bc.wait_and_download_image(out_dir, fname, timeout=int(self.ti_timeout.get()))
                    if dl_ok: results.append((i, short, '✅ Thành công', fname))
                    else: results.append((i, short, '⚠ Không tải được', fname))

                if i < len(lines):
                    time.sleep(delay)
        except Exception as e:
            self.app.log(f"❌ Lỗi: {e}")
        finally:
            self.app.running = False
            self.app.root.after(0, self.ti_progress.stop)
            self.app.root.after(0, lambda: self.ti_status_lbl.config(text=""))
            self.app._log_summary("Text→Image", results, out_dir)
