import os
import time
import random
from tkinter import *
from tkinter import messagebox, scrolledtext, ttk
from src.constants import BG, CARD, TEXT, ACCENT, GREEN, RED, MUTED, OUTPUT_DIR_CHAR
from src.ui.components.base import UIBase

class CreateVideoTab(Frame, UIBase):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        # Hướng dẫn
        guide = self._card(self, "📋 Hướng dẫn")
        guide.pack(fill=X, padx=12, pady=(10,4))
        Label(guide, text=(
            "1. Nhap danh sach prompt (moi dong 1 canh)\n"
            "2. Bam START -> Tool tu dong upload anh nhan vat + generate tung video\n"
            "Luu y: Prompt co ten nhan vat -> chen dung anh do | Khong co ten -> upload tat ca"
        ), bg=CARD, fg=TEXT, font=("Segoe UI", 9), justify=LEFT
        ).pack(anchor=W, padx=10, pady=6)

        # Hiển thị nhân vật đã setup
        cv_char = self._card(self, "👤 Nhân vật đã thiết lập")
        cv_char.pack(fill=X, padx=12, pady=4)
        self.cv_char_display = Label(cv_char,
                                     text="Chưa có nhân vật. Vào tab 'Nhân Vật' để thiết lập trước.",
                                     font=("Segoe UI", 9), bg=CARD, fg=MUTED)
        self.cv_char_display.pack(anchor=W, padx=10, pady=6)

        # Prompts
        lf = self._card(self, "📝 Danh sách Prompt  (mỗi dòng 1 cảnh)")
        lf.pack(fill=BOTH, expand=True, padx=12, pady=4)
        mode_f = Frame(lf, bg=CARD); mode_f.pack(anchor=W, pady=(4,2))
        Label(mode_f, text="Định dạng: ", bg=CARD, fg=MUTED,
              font=("Segoe UI", 9)).pack(side=LEFT)
        self.cv_mode = StringVar(value="normal")
        for txt, val in [("Thông thường", "normal"),
                          ("JSON nâng cao (scene_1, scene_2...)", "json")]:
            Radiobutton(mode_f, text=txt, variable=self.cv_mode, value=val,
                        bg=CARD, fg=TEXT, selectcolor=BG,
                        activebackground=CARD, font=("Segoe UI", 9)
                        ).pack(side=LEFT, padx=6)
        self.cv_prompts = scrolledtext.ScrolledText(
            lf, height=7, font=("Consolas", 9),
            bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.cv_prompts.pack(fill=BOTH, expand=True, pady=(2,6))
        self.cv_prompts.insert(END, "Alice và Bob đang đi dạo trong công viên\nCharlie đang chạy trên bãi biển")

        # Settings
        sf = self._card(self, "⚙️ Cài đặt đầu ra")
        sf.pack(fill=X, padx=12, pady=4)
        r1 = Frame(sf, bg=CARD); r1.pack(fill=X, pady=3, padx=8)
        Label(r1, text="Tên file:", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side=LEFT)
        self.cv_base = Entry(r1, width=20, font=("Segoe UI", 9),
                             bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.cv_base.insert(0, "character_video")
        self.cv_base.pack(side=LEFT, padx=6, ipady=3)
        
        r2 = Frame(sf, bg=CARD); r2.pack(fill=X, pady=3, padx=8)
        Label(r2, text="Lưu tại:", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side=LEFT)
        self.cv_out = Entry(r2, width=55, font=("Segoe UI", 9),
                            bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.cv_out.insert(0, OUTPUT_DIR_CHAR)
        self.cv_out.pack(side=LEFT, padx=6, ipady=3)
        self._btn(r2, "📂", lambda: self.app._browse(self.cv_out),
                  color="#21262D").pack(side=LEFT, ipady=3, ipadx=4)

        # Delay
        df = self._card(self, "⏱ Độ trễ giữa các prompt")
        df.pack(fill=X, padx=12, pady=4)
        df_r = Frame(df, bg=CARD); df_r.pack(anchor=W, padx=8, pady=4)
        self.cv_delay = StringVar(value="normal")
        for txt, val in [("Bình thường (5s)", "normal"),
                          ("Gấp đôi (10s)", "double"),
                          ("Ngẫu nhiên (6-15s)", "random")]:
            Radiobutton(df_r, text=txt, variable=self.cv_delay, value=val,
                        bg=CARD, fg=TEXT, selectcolor=BG,
                        activebackground=CARD, font=("Segoe UI", 9)
                        ).pack(side=LEFT, padx=8)

        # Timeout
        tf = self._card(self, "⬇️ Tự động chờ video xong → Tải về ngay")
        tf.pack(fill=X, padx=12, pady=4)
        self.cv_timeout = StringVar(value="600")
        Label(tf, text="  ⏳  Chờ đến khi video xong, tối đa 10 phút  →  Tải xuống ngay khi phát hiện hoàn tất",
              font=("Segoe UI", 9, "bold"), bg=CARD, fg=GREEN).pack(anchor=W, padx=12, pady=6)

        self.cv_progress = ttk.Progressbar(self, mode="indeterminate", style="TProgressbar")
        self.cv_progress.pack(fill=X, padx=12, pady=(6,2))
        self.cv_status_lbl = Label(self, text="", font=("Segoe UI", 8), bg=BG, fg=MUTED)
        self.cv_status_lbl.pack()

        btn_f = Frame(self, bg=BG); btn_f.pack(fill=X, padx=12, pady=8)
        self._btn(btn_f, "  ▶  START — Tạo video + Tự động tải",
                  self._start_create_video, color=GREEN
                  ).pack(side=LEFT, fill=X, expand=True, ipady=9, padx=(0,4))
        self._btn(btn_f, "🧪 TEST: Chỉ chọn ảnh (không submit)",
                  self._test_char_select, color="#1B4721"
                  ).pack(side=LEFT, ipady=9, padx=(0,4))
        self._btn(btn_f, "⏹ STOP", self.app._stop, color=RED
                  ).pack(side=LEFT, ipady=9, ipadx=6)

    def refresh_char_display(self):
        if self.app.characters:
            names = ", ".join(self.app.characters.keys())
            self.cv_char_display.config(
                text=f"✅ {len(self.app.characters)} nhân vật: {names}\n"
                     f"   → TẤT CẢ ảnh sẽ được upload vào mỗi video",
                fg="green"
            )
        else:
            self.cv_char_display.config(
                text="Chưa có nhân vật. Setup trong tab 'Nhân Vật' để thiết lập trước.", fg="gray"
            )

    def _start_create_video(self):
        raw = self.cv_prompts.get("1.0", END).strip()
        prompts = [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]
        if not prompts:
            messagebox.showerror("Lỗi", "Chưa nhập prompt!")
            return
        if not self.app.bc.is_alive():
            messagebox.showerror("Lỗi", "Chưa mở Chrome!")
            return
        out_dir = self.cv_out.get()
        os.makedirs(out_dir, exist_ok=True)
        self.app.log(f"🚀 Create Video: {len(prompts)} prompt(s), {len(self.app.characters)} nhân vật")
        self.app.nb.select(6)
        self.app._run_bg(lambda: self._create_video_worker(prompts, out_dir))

    def _create_video_worker(self, prompts, out_dir):
        self.app.running = True
        self.app.root.after(0, self.cv_progress.start)
        delay_map = {"normal": 5, "double": 10, "random": None}
        chars = list(self.app.characters.items())
        results = []
        submitted = []

        try:
            total = len(prompts)
            self.app.log(f"\n{'═'*60}")
            self.app.log(f"📤  PHASE 1 — Submit {total} prompt(s) + upload nhân vật")
            self.app.log(f"{'═'*60}")

            d_val = delay_map.get(self.cv_delay.get(), 5)

            for i, prompt in enumerate(prompts, 1):
                if not self.app.running:
                    results.append((i, prompt[:50], '⏹ Dừng', ''))
                    break
                short = prompt[:50]
                fname = f"{self.cv_base.get()}_{i:02d}.mp4"
                self.app.log(f"\n📤 [{i}/{total}] {short}...")
                self.app.root.after(0, lambda ii=i, t=total:
                    self.cv_status_lbl.config(text=f"📤 Submit [{ii}/{t}]..."))

                detected = [(n, p) for n, p in chars if n.lower() in prompt.lower()]
                to_upload = detected if detected else chars
                if to_upload: self.app.log(f"   👤 Nhân vật: {[n for n,_ in to_upload]}")

                if i == 1:
                    self.app.bc.new_project()
                    time.sleep(2)
                else:
                    ready = self.app.bc.wait_for_prompt_ready(timeout=60)
                    if not ready: self.app.bc.new_project(); time.sleep(2)

                for name, img_path in to_upload:
                    self.app.log(f"   📤 Upload ảnh {name}...")
                    self.app.bc.upload_image(img_path)
                    time.sleep(0.5)

                from selenium.webdriver.common.by import By
                try:
                    from selenium.webdriver.common.keys import Keys
                    self.app.bc.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(0.5)
                except: pass

                if self.app.bc.set_prompt(prompt):
                    if self.app.bc.click_generate():
                        proj_url = self.app.bc.driver.current_url
                        submitted.append((i, short, fname, proj_url))
                        self.app.log(f"   ✅ Đã submit #{i}")

                if i < total and self.app.running:
                    delay = d_val if d_val is not None else random.randint(6, 15)
                    self.app.log(f"   ⏳ Chờ {delay}s...")
                    time.sleep(delay)

            self.app.log(f"\n📤 Phase 1 xong: {len(submitted)}/{total} prompt đã submit")
            if not submitted: return

            self.app.log(f"\n{'═'*60}")
            self.app.log(f"⬇️  PHASE 2 — Tải {len(submitted)} video theo thứ tự")
            self.app.log(f"{'═'*60}")

            for idx, (i, short, fname, proj_url) in enumerate(submitted, 1):
                if not self.app.running: break
                self.app.log(f"\n⬇️ [{idx}/{len(submitted)}] Quay lại: {short}...")
                self.app.root.after(0, lambda ii=idx, t=len(submitted), fn=fname:
                    self.cv_status_lbl.config(text=f"⬇️ Tải [{ii}/{t}] {fn}..."))

                try:
                    self.app.bc.driver.get(proj_url)
                    time.sleep(3)
                except: continue

                dl_ok = self.app.bc.wait_and_download(out_dir, fname, timeout=int(self.cv_timeout.get()))
                if dl_ok:
                    results.append((i, short, '✅ Thành công', fname))
                    self.app.root.after(0, lambda fn=fname: self.cv_status_lbl.config(text=f"✅ Tải xong: {fn}"))
                else:
                    results.append((i, short, '⚠ Không tải được', fname))
        except Exception as e:
            self.app.log(f"❌ Lỗi: {e}")
        finally:
            self.app.running = False
            self.app.root.after(0, self.cv_progress.stop)
            self.app.root.after(0, lambda: self.cv_status_lbl.config(text=""))
            self.app._log_summary("Tạo Video Nhân Vật", results, out_dir)

    def _test_char_select(self):
        if not self.app.characters:
            messagebox.showinfo("Test", "Chưa có nhân vật trong Character Setup!")
            return
        raw = self.cv_prompts.get("1.0", END)
        for name, path in self.app.characters.items():
            if name.lower() in raw.lower():
                self.app.log(f"🧪 TEST: Sẽ upload ảnh '{name}' từ {path}")
        messagebox.showinfo("Test OK", f"Detect {len(self.app.characters)} nhân vật. Xem log để biết chi tiết.")
