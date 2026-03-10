from tkinter import *
from tkinter import scrolledtext
from src.constants import BG, CARD, TEXT, ACCENT
from src.ui.components.base import UIBase

class NoteTab(Frame, UIBase):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        hf = Frame(self, bg="#0A0F1A")
        hf.pack(fill=X)
        Label(hf, text="📌  Hướng dẫn sử dụng VEO 3 FLOW PRO",
              font=("Segoe UI", 12, "bold"), bg="#0A0F1A", fg=ACCENT
              ).pack(anchor=W, padx=16, pady=10)
        
        txt = scrolledtext.ScrolledText(self, wrap=WORD, font=("Segoe UI", 10),
                                        bg=CARD, fg=TEXT, insertbackground=TEXT,
                                        relief="flat", bd=0, padx=8, pady=8)
        txt.pack(fill=BOTH, expand=True, padx=12, pady=(0, 10))
        txt.insert(END, """
  ⚠️  YÊU CẦU BẮT BUỘC:
  ─────────────────────────────────────────────
  1. Cài Google Chrome + đăng nhập Google AI Pro tại: labs.google/fx
  2. Cài Python packages:  pip install selenium webdriver-manager pillow

  ─────────────────────────────────────────────
  🌐  BROWSER & KẾT NỐI
      → Mở Chrome vào Google Flow (Thường / Ẩn danh / Chrome mới)
      → Kết nối Chrome đang mở sẵn qua remote debug port 9222

  📝  TEXT TO VIDEO  (Tab chính)
      → Dán danh sách prompt — mỗi dòng một lệnh
      → Hỗ trợ JSON: {"prompt":"...","style":"...","aspect_ratio":"9:16"}
      → [START]  — Tuần tự: tạo xong rồi tải, sang prompt tiếp
      → [RAPID]  — Submit nhanh tất cả, render SONG SONG trên cloud
      → [STOP]   — Dừng tiến trình đang chạy

  👤  NHÂN VẬT (Character Setup)
      → Chọn ảnh nhân vật → Đặt tên ngắn (Alice, Bob, NhanVat1...)
      → Upload lên Flow → Tool tự chèn ảnh khi tạo video

  🎞️  TẠO VIDEO NHÂN VẬT (Create Video)
      → Nhập prompt cho từng cảnh
      → Tool tự upload ảnh + generate theo thứ tự

  📋  LOGS   — Xem toàn bộ hoạt động, lưu log ra file TXT

  🎬  GHÉP VIDEO — Ghép nhiều MP4 thành 1 file (cần FFmpeg)
      → Tải FFmpeg: https://ffmpeg.org/download.html

  💡  MẸO: Dùng thư mục output RIÊNG cho mỗi phiên/máy
           để tránh lẫn file khi chạy song song.
""")
        txt.config(state=DISABLED)
