import os
import time
import threading
import subprocess
from pathlib import Path
from tkinter import *
from tkinter import messagebox, scrolledtext, ttk, filedialog
from src.constants import BG, CARD, TEXT, ACCENT, GREEN, MUTED, BORDER
from src.ui.components.base import UIBase

class MergeTab(Frame, UIBase):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        hf = Frame(self, bg="#0A0F1A"); hf.pack(fill=X)
        Label(hf, text="🎬  Ghép nhiều video thành 1 file",
              font=("Segoe UI", 12, "bold"), bg="#0A0F1A", fg=ACCENT
              ).pack(anchor=W, padx=16, pady=10)
        Label(hf, text="Yêu cầu: FFmpeg đã cài trong PATH  |  Tải tại: ffmpeg.org",
              font=("Segoe UI", 9), bg="#0A0F1A", fg=MUTED).pack(anchor=W, padx=16, pady=(0,10))

        info = self._card(self, "ℹ️ Thông tin công cụ")
        info.pack(fill=X, padx=12, pady=(10,5))
        Label(info, text=(
            "• Ghép các file MP4 trong một thư mục thành 1 video duy nhất\n"
            "• Sắp xếp theo tên file (video_01, video_02, ...)\n"
            "• Sử dụng FFmpeg concat — giữ nguyên chất lượng gốc (không re-encode)"
        ), bg=CARD, fg=TEXT, font=("Segoe UI", 9), justify=LEFT).pack(anchor=W, padx=10, pady=8)

        self._btn(self, "  ▶  MỞ CÔNG CỤ GHÉP VIDEO",
                  self._open_merger_window, color=GREEN
                  ).pack(pady=16, ipady=10, ipadx=30)

    def _open_merger_window(self):
        win = Toplevel(self.app.root)
        win.title("Video Merger Tool")
        win.geometry("560x480")
        win.resizable(False, False)
        win.configure(bg=BG)

        Label(win, text="🎬 GHÉP VIDEO TOOL", bg=BG, fg=ACCENT, font=("Segoe UI", 13, "bold")).pack(pady=10)

        f1 = LabelFrame(win, text="Chọn Folder Chứa Video", padx=8, pady=5)
        f1.pack(fill=X, padx=15, pady=6)
        folder_var = StringVar()
        fr = Frame(f1); fr.pack(fill=X)
        Entry(fr, textvariable=folder_var, width=40).pack(side=LEFT, padx=4)
        
        def browse_folder():
            d = filedialog.askdirectory()
            if d:
                folder_var.set(d)
                vids = sorted(Path(d).glob("*.mp4"))
                vid_list.config(state=NORMAL)
                vid_list.delete("1.0", END)
                for v in vids: vid_list.insert(END, f"{v.name}\n")
                vid_list.config(state=DISABLED)
        
        Button(fr, text="Chọn Folder", bg=ACCENT, fg="white", command=browse_folder).pack(side=LEFT)

        f2 = LabelFrame(win, text="Danh Sách Video", padx=8, pady=5)
        f2.pack(fill=BOTH, expand=True, padx=15, pady=4)
        vid_list = scrolledtext.ScrolledText(f2, height=8, font=("Consolas", 9), state=DISABLED)
        vid_list.pack(fill=BOTH, expand=True)

        f3 = LabelFrame(win, text="Nơi Lưu File & Tên Output", padx=8, pady=5)
        f3.pack(fill=X, padx=15, pady=4)
        r = Frame(f3); r.pack(fill=X)
        Label(r, text="Lưu vào:").pack(side=LEFT)
        out_dir_var = StringVar()
        Entry(r, textvariable=out_dir_var, width=36).pack(side=LEFT, padx=4)
        Button(r, text="Chọn", command=lambda: out_dir_var.set(filedialog.askdirectory() or out_dir_var.get())).pack(side=LEFT, bg=ACCENT, fg="white")
        
        r2 = Frame(f3); r2.pack(fill=X, pady=3)
        Label(r2, text="Tên file:").pack(side=LEFT)
        fname_var = StringVar(value="video_ghep.mp4")
        Entry(r2, textvariable=fname_var, width=30).pack(side=LEFT, padx=4)

        m_prog = ttk.Progressbar(win, mode="indeterminate")
        m_prog.pack(fill=X, padx=15, pady=4)
        m_status = Label(win, text="Vui lòng chọn folder chứa video")
        m_status.pack()

        def do_merge():
            folder = folder_var.get()
            if not folder: messagebox.showerror("Lỗi", "Chưa chọn folder!"); return
            out_d = out_dir_var.get() or folder
            fname = fname_var.get() or "video_ghep.mp4"
            out_path = str(Path(out_d) / fname)
            vids = sorted(Path(folder).glob("*.mp4"))
            if not vids: messagebox.showerror("Lỗi", "Không có file MP4 trong folder!"); return
            list_file = str(Path(folder) / "_merge_list.txt")
            with open(list_file, "w", encoding="utf-8") as lf:
                for v in vids: lf.write(f"file '{v}'\n")
            m_prog.start()
            m_status.config(text=f"Đang ghép {len(vids)} video...")
            def run():
                try:
                    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", out_path]
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                    if res.returncode == 0:
                        win.after(0, lambda: m_prog.stop())
                        win.after(0, lambda: m_status.config(text=f"✅ Xong! → {out_path}"))
                        win.after(0, lambda: messagebox.showinfo("✅ Done", f"Ghép xong!\n{out_path}"))
                    else:
                        win.after(0, lambda: m_prog.stop())
                        win.after(0, lambda: messagebox.showerror("Lỗi", f"FFmpeg error:\n{res.stderr[:500]}"))
                except FileNotFoundError:
                    win.after(0, lambda: m_prog.stop())
                    win.after(0, lambda: messagebox.showerror("Lỗi", "FFmpeg chưa được cài!\nTải tại: https://ffmpeg.org"))
                except Exception as e:
                    win.after(0, lambda: m_prog.stop())
                    win.after(0, lambda: m_status.config(text=f"❌ {str(e)}"))
            threading.Thread(target=run, daemon=True).start()

        Button(win, text="▶ GHÉP VIDEO", bg=GREEN, fg="white", font=("Segoe UI", 11, "bold"), command=do_merge).pack(fill=X, padx=15, pady=8, ipady=8)
