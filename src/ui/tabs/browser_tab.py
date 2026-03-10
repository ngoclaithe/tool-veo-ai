from tkinter import *
from tkinter import messagebox
from src.constants import BG, CARD, TEXT, ACCENT, PURPLE, ORANGE, GREEN, BORDER, OUTPUT_DIR_TEXT
from src.ui.components.base import UIBase

class BrowserTab(Frame, UIBase):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        # Hướng dẫn nhanh
        top = self._card(self, "📋 Quy trình kết nối")
        top.pack(fill=X, padx=14, pady=(12, 5))
        Label(top, text=(
            "1️⃣  Bấm nút MỞ CHROME bên dưới  →  Đăng nhập Google nếu cần\n"
            "2️⃣  Sau khi đăng nhập xong        →  Bấm '✔ Xác nhận đăng nhập'\n"
            "3️⃣  Sang tab 'Text to Video'       →  Nhập prompt  →  Bấm START"
        ), bg=CARD, fg=TEXT, font=("Segoe UI", 9), justify=LEFT
        ).pack(anchor=W, padx=10, pady=8)

        # Nút điều khiển Chrome
        ctrl = self._card(self, "⚙️ Điều khiển Chrome")
        ctrl.pack(fill=X, padx=14, pady=5)

        row1 = Frame(ctrl, bg=CARD); row1.pack(fill=X, padx=8, pady=(8, 3))
        self._btn(row1, "  🖥  Mở Chrome (Thường)  ",
                  lambda: self.app._run_bg(lambda: self.app.bc.open("normal", download_dir=OUTPUT_DIR_TEXT)),
                  color=ACCENT).pack(side=LEFT, fill=X, expand=True, padx=(0,4), ipady=8)
        self._btn(row1, "  🔒  Mở Chrome Ẩn Danh  ",
                  lambda: self.app._run_bg(lambda: self.app.bc.open("incognito", download_dir=OUTPUT_DIR_TEXT)),
                  color="#444C56").pack(side=LEFT, fill=X, expand=True, padx=(4,0), ipady=8)

        row2 = Frame(ctrl, bg=CARD); row2.pack(fill=X, padx=8, pady=3)
        self._btn(row2, "  ✨  Chrome Hoàn Toàn Mới (Fresh)  ",
                  lambda: self.app._run_bg(lambda: self.app.bc.open("fresh", download_dir=OUTPUT_DIR_TEXT)),
                  color=PURPLE).pack(side=LEFT, fill=X, expand=True, padx=(0,4), ipady=8)
        self._btn(row2, "  🔗  Kết Nối Chrome Đang Mở  ",
                  lambda: self.app._run_bg(self._connect_existing_chrome),
                  color=ORANGE).pack(side=LEFT, fill=X, expand=True, padx=(4,0), ipady=8)

        Frame(ctrl, bg=BORDER, height=1).pack(fill=X, padx=8, pady=8)

        self._btn(ctrl, "  ✔  Xác nhận đăng nhập xong → Bắt đầu sử dụng  ",
                  self._confirm_login, color=GREEN
                  ).pack(fill=X, padx=8, pady=(0,5), ipady=10)

        row3 = Frame(ctrl, bg=CARD); row3.pack(fill=X, padx=8, pady=(0,8))
        def refresh_status():
            s = self.app.bc.get_status()
            self.app.status_var.set(f"◉  {s}")
        self._btn(row3, "🔄 Cập nhật trạng thái", refresh_status,
                  color="#21262D").pack(side=LEFT, padx=(0,4), ipady=5)

        self._btn(row3, "🧪 TEST: Dán prompt mẫu", self._test_paste,
                  color="#1B4721").pack(side=LEFT, ipady=5)

    def _confirm_login(self):
        self.app.log("✅ Đã xác nhận đăng nhập!")
        self.app.set_status("Trạng thái: ✅ Đã đăng nhập")
        messagebox.showinfo("OK", "Đã xác nhận đăng nhập!\nBây giờ chuyển sang tab Text to Video để bắt đầu.")

    def _connect_existing_chrome(self):
        """Kết nối tới Chrome đang mở qua remote debugging port"""
        ok = self.app.bc.connect_existing()
        if ok:
            self.app.set_status("Trạng thái: ✅ Kết nối Chrome thành công")
            self.app.root.after(0, lambda: messagebox.showinfo(
                "✅ Kết nối OK",
                f"Đã kết nối Chrome thành công!\n{self.app.bc.get_status()}\n\nBây giờ sang tab Text to Video để tạo video."
            ))
        else:
            self.app.root.after(0, lambda: messagebox.showerror(
                "❌ Kết nối thất bại",
                "Không kết nối được Chrome!\n\n"
                "Giải pháp:\n"
                "1. ĐÓNG Chrome đang mở\n"
                "2. Bấm 'MỞ CHROME' trong tool\n"
                "3. Đăng nhập Google trên Chrome đó\n"
                "4. Bấm 'GỬI ĐĂNG NHẬP'\n"
                "5. Sang tab Text to Video → START"
            ))

    def _test_paste(self):
        if not self.app.bc.is_alive():
            messagebox.showerror("Lỗi", "Chưa mở Chrome!")
            return
        sample = "A beautiful sunset over the ocean, cinematic lighting, 8K"
        self.app.log("🧪 TEST: Mở project mới + dán prompt mẫu...")
        self.app.nb.select(6)
        def _run():
            ok = self.app.bc.new_project()
            if ok:
                self.app.bc.set_prompt(sample)
                self.app.log("✅ TEST xong — kiểm tra Chrome xem prompt đã hiện chưa!")
            else:
                self.app.log("❌ TEST thất bại")
        self.app._run_bg(_run)
