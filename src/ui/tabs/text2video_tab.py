import os
import time
import random
from tkinter import *
from tkinter import messagebox, scrolledtext, ttk
from src.constants import BG, CARD, TEXT, ACCENT, GREEN, ORANGE, RED, MUTED, OUTPUT_DIR_TEXT
from src.ui.components.base import UIBase
from src.utils.helpers import parse_line

class Text2VideoTab(Frame, UIBase):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        # Prompts
        lf = self._card(self, "📝 Danh sách Prompt  (mỗi dòng 1 lệnh — hỗ trợ JSON)")
        lf.pack(fill=BOTH, expand=True, padx=12, pady=(10,4))

        mode_f = Frame(lf, bg=CARD); mode_f.pack(anchor=W, pady=(4,2))
        Label(mode_f, text="Định dạng nhập:  ", bg=CARD, fg=MUTED,
              font=("Segoe UI", 9)).pack(side=LEFT)
        self.tv_mode = StringVar(value="normal")
        for txt, val in [("Thông thường (mỗi dòng 1 prompt)", "normal"),
                          ("JSON nâng cao (scene_1, scene_2...)", "json")]:
            Radiobutton(mode_f, text=txt, variable=self.tv_mode, value=val,
                        bg=CARD, fg=TEXT, selectcolor=BG,
                        activebackground=CARD, font=("Segoe UI", 9)
                        ).pack(side=LEFT, padx=6)

        self.tv_prompts = scrolledtext.ScrolledText(
            lf, height=10, font=("Consolas", 9),
            bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.tv_prompts.pack(fill=BOTH, expand=True, pady=(2,6))
        self.tv_prompts.insert(END, "A cinematic sunset over the ocean, 8K, dramatic lighting\n"
                                    "A futuristic city at night, neon lights, rain, blade runner style")

        # Settings
        sf = self._card(self, "⚙️ Cài đặt đầu ra")
        sf.pack(fill=X, padx=12, pady=4)
        r1 = Frame(sf, bg=CARD); r1.pack(fill=X, pady=3, padx=8)
        Label(r1, text="Tên file:", bg=CARD, fg=MUTED,
              font=("Segoe UI", 9)).pack(side=LEFT)
        self.tv_base = Entry(r1, width=20, font=("Segoe UI", 9),
                             bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.tv_base.insert(0, "video")
        self.tv_base.pack(side=LEFT, padx=6, ipady=3)
        Label(r1, text="→  video_01.mp4, video_02.mp4, ...",
              bg=CARD, fg=MUTED, font=("Segoe UI", 8)).pack(side=LEFT)

        r2 = Frame(sf, bg=CARD); r2.pack(fill=X, pady=3, padx=8)
        Label(r2, text="Lưu tại:", bg=CARD, fg=MUTED,
              font=("Segoe UI", 9)).pack(side=LEFT)
        self.tv_out = Entry(r2, width=55, font=("Segoe UI", 9),
                            bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.tv_out.insert(0, OUTPUT_DIR_TEXT)
        self.tv_out.pack(side=LEFT, padx=6, ipady=3)
        self._btn(r2, "📂", lambda: self.app._browse(self.tv_out),
                  color="#21262D").pack(side=LEFT, ipady=3, ipadx=4)

        # Delay
        df = self._card(self, "⏱ Độ trễ giữa các prompt")
        df.pack(fill=X, padx=12, pady=4)
        df_r = Frame(df, bg=CARD); df_r.pack(anchor=W, padx=8, pady=4)
        self.tv_delay = StringVar(value="normal")
        for txt, val in [("Bình thường (5s)", "normal"),
                          ("Gấp đôi (10s)", "double"),
                          ("Ngẫu nhiên (6-15s)", "random")]:
            Radiobutton(df_r, text=txt, variable=self.tv_delay, value=val,
                        bg=CARD, fg=TEXT, selectcolor=BG,
                        activebackground=CARD, font=("Segoe UI", 9)
                        ).pack(side=LEFT, padx=8)

        # Timeout
        tf = self._card(self, "⬇️ Tự động chờ video xong → Tải về ngay")
        tf.pack(fill=X, padx=12, pady=4)
        self.tv_timeout = StringVar(value="600")
        Label(tf, text="  ⏳  Chờ đến khi video xong, tối đa 10 phút  →  Tải xuống ngay khi phát hiện hoàn tất",
              font=("Segoe UI", 9, "bold"), bg=CARD, fg=GREEN).pack(anchor=W, padx=12, pady=6)
        Label(tf, text="  ℹ️  Tool phát hiện video xong sẽ tải ngay, không cần chờ hết 10 phút!",
              font=("Segoe UI", 8), bg=CARD, fg=MUTED).pack(anchor=W, padx=20, pady=(0,4))

        # Progress
        self.tv_progress = ttk.Progressbar(self, mode="indeterminate", style="TProgressbar")
        self.tv_progress.pack(fill=X, padx=12, pady=(6,2))
        self.tv_status_lbl = Label(self, text="", font=("Segoe UI", 8), bg=BG, fg=MUTED)
        self.tv_status_lbl.pack()

        btn_row = Frame(self, bg=BG); btn_row.pack(fill=X, padx=12, pady=8)
        self._btn(btn_row, "  ▶  START — Tuần tự + Tải về",
                  self._start_text2video, color=GREEN
                  ).pack(side=LEFT, fill=X, expand=True, ipady=9, padx=(0,4))
        self._btn(btn_row, "  ⚡  RAPID — Submit nhanh, render song song",
                  self._start_rapid, color=ORANGE
                  ).pack(side=LEFT, fill=X, expand=True, ipady=9, padx=(0,4))
        self._btn(btn_row, "  ⏹  STOP",
                  self.app._stop, color=RED
                  ).pack(side=LEFT, ipady=9, ipadx=8)

    def _start_text2video(self):
        raw = self.tv_prompts.get("1.0", END).strip()
        lines = [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]
        if not lines:
            messagebox.showerror("Lỗi", "Chưa nhập prompt!")
            return
        if not self.app.bc.is_alive():
            messagebox.showerror("Lỗi", "Chưa mở Chrome! Vào tab Kết Nối trước.")
            return
        out_dir = self.tv_out.get()
        os.makedirs(out_dir, exist_ok=True)
        self.app.log(f"🚀 Bắt đầu Text→Video (Tuần tự): {len(lines)} prompt(s)")
        self.app.nb.select(6)
        self.app._run_bg(lambda: self._t2v_worker(lines, out_dir))

    def _t2v_worker(self, lines, out_dir):
        self.app.running = True
        self.app.root.after(0, self.tv_progress.start)
        results = []
        try:
            for i, line in enumerate(lines, 1):
                if not self.app.running:
                    results.append((i, line[:50], '⏹ Dừng', ''))
                    break

                prompt, aspect, dur, extra = parse_line(line)
                short = prompt[:60]
                self.app.log(f"\n══ 🎬 [{i}/{len(lines)}] {short}...")
                self.app.root.after(0, lambda ii=i, t=len(lines), p=short:
                    self.tv_status_lbl.config(text=f"🎬 [{ii}/{t}] {p}..."))

                delay_map = {"normal": 5, "double": 10, "random": None}
                d_val = delay_map.get(self.tv_delay.get(), 5)
                delay = d_val if d_val is not None else random.randint(6, 15)

                if i == 1:
                    self.app.bc.new_project()
                    time.sleep(2)
                else:
                    ready = self.app.bc.wait_for_prompt_ready(timeout=60)
                    if not ready:
                        self.app.bc.new_project()
                        time.sleep(2)

                self.app.bc.set_aspect_ratio(aspect)
                ok = self.app.bc.set_prompt(prompt)
                if not ok:
                    results.append((i, short, '❌ Lỗi dán prompt', ''))
                    continue
                time.sleep(0.8)

                ok = self.app.bc.click_generate()
                if not ok:
                    results.append((i, short, '❌ Lỗi nút Tạo', ''))
                    continue

                fname = f"{self.tv_base.get()}_{i:02d}.mp4"
                dl_ok = self.app.bc.wait_and_download(out_dir, fname,
                    timeout=int(self.tv_timeout.get()))
                
                if dl_ok:
                    results.append((i, short, '✅ Thành công', fname))
                else:
                    results.append((i, short, '⚠ Không tải được', fname))

                if i < len(lines):
                    self.app.log(f"⏳ Chờ {delay}s rồi prompt tiếp...")
                    time.sleep(delay)

        except Exception as e:
            self.app.log(f"❌ Lỗi ngoài dự kiến: {e}")
        finally:
            self.app.running = False
            self.app.root.after(0, self.tv_progress.stop)
            self.app.root.after(0, lambda: self.tv_status_lbl.config(text=""))
            self.app._log_summary("Text→Video (Tuần tự)", results, out_dir)

    def _start_rapid(self):
        raw = self.tv_prompts.get("1.0", END).strip()
        lines = [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]
        if not lines:
            messagebox.showerror("Lỗi", "Chưa nhập prompt!")
            return
        if not self.app.bc.is_alive():
            messagebox.showerror("Lỗi", "Chưa mở Chrome!")
            return
        out_dir = self.tv_out.get()
        os.makedirs(out_dir, exist_ok=True)
        self.app.log(f"⚡ RAPID MODE: {len(lines)} prompt(s) → {out_dir}")
        self.app.nb.select(6)
        self.app._run_bg(lambda: self._rapid_worker(lines, out_dir))

    def _rapid_worker(self, lines, out_dir):
        import shutil
        self.app.running = True
        self.app.root.after(0, self.tv_progress.start)
        snap = set(os.listdir(out_dir))
        base = self.tv_base.get()
        submitted = 0
        video_counter = 1

        try:
            for i, line in enumerate(lines, 1):
                if not self.app.running: break
                prompt, aspect, _, _ = parse_line(line)
                self.app.log(f"⚡ Submit [{i}/{len(lines)}]: {prompt[:50]}...")
                self.app.root.after(0, lambda ii=i, t=len(lines):
                    self.tv_status_lbl.config(text=f"⚡ Submit {ii}/{t}..."))

                if i == 1: self.app.bc.new_project()
                else:
                    if not self.app.bc.wait_for_prompt_ready(30):
                        self.app.bc.new_project()
                
                self.app.bc.set_aspect_ratio(aspect)
                if self.app.bc.set_prompt(prompt):
                    if self.app.bc.click_generate():
                        submitted += 1
                        time.sleep(2) # Chờ nhỏ để UI cloud nhận lệnh
                
                if i < len(lines):
                    time.sleep(15) # Delay an toàn cho rapid

            self.app.log(f"\n📥 Đang monitor thư mục để nhận {submitted} video...")
            deadline = time.time() + submitted * 600
            found = 0
            prev_size_map = {}

            while time.time() < deadline and found < submitted and self.app.running:
                time.sleep(3)
                try:
                    current = set(os.listdir(out_dir))
                    added = current - snap
                    new_mp4s = sorted([f for f in added if f.endswith(".mp4") and not f.endswith(".crdownload")])
                    for fname in new_mp4s:
                        src = os.path.join(out_dir, fname)
                        sz = os.path.getsize(src) if os.path.exists(src) else 0
                        if prev_size_map.get(fname) == sz and sz > 0:
                            dst_name = f"{base}_{video_counter:02d}.mp4"
                            dst = os.path.join(out_dir, dst_name)
                            if not os.path.exists(dst):
                                shutil.move(src, dst)
                                self.app.log(f"✅ Tải về #{video_counter}: {dst_name}")
                                snap.add(dst_name)
                                video_counter += 1
                                found += 1
                                self.app.root.after(0, lambda f=found, s=submitted:
                                    self.tv_status_lbl.config(text=f"📥 Đã nhận {f}/{s} video"))
                        else:
                            prev_size_map[fname] = sz
                except Exception as e:
                    self.app.log(f"⚠ Monitor: {e}")
        except Exception as e:
            self.app.log(f"❌ Rapid lỗi: {e}")
        finally:
            self.app.running = False
            self.app.root.after(0, self.tv_progress.stop)
            self.app.root.after(0, lambda: self.tv_status_lbl.config(text=""))
            self.app.log(f"✅ RAPID xong! Nhận {found}/{submitted} video")
