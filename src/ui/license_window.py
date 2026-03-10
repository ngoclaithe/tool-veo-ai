from tkinter import *
from tkinter import messagebox
from src.constants import BG, CARD, TEXT, ACCENT, GREEN, RED, MUTED
from src.ui.components.base import UIBase
from src.utils.license_manager import get_hwid, validate_key, save_license

class LicenseWindow(Toplevel, UIBase):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("KÍCH HOẠT BẢN QUYỀN VEO 3 FLOW")
        self.geometry("450x320")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        
        self.update_idletasks()
        w, h = 450, 320
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth() - w)//2}+{(self.winfo_screenheight() - h)//2}")

        self._build()

    def _build(self):
        Label(self, text="🛡️ KIỂM TRA BẢN QUYỀN", 
              font=("Segoe UI", 12, "bold"), bg=BG, fg=ACCENT).pack(pady=(15, 5))
        
        info = self._card(self, "Trạng thái")
        info.pack(fill=X, padx=20, pady=10)
        
        self.hwid = get_hwid()
        Label(info, text="Mã máy (Machine ID):", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor=W, padx=10, pady=(5,0))
        
        hw_f = Frame(info, bg=CARD)
        hw_f.pack(fill=X, padx=10, pady=(2, 10))
        
        self.hwid_entry = Entry(hw_f, width=30, font=("Consolas", 10, "bold"), 
                                bg="#0D1117", fg=GREEN, bd=0)
        self.hwid_entry.insert(0, self.hwid)
        self.hwid_entry.config(state="readonly") 
        self.hwid_entry.pack(side=LEFT, ipady=3)
        
        def copy_id():
            self.clipboard_clear()
            self.clipboard_append(self.hwid)
            messagebox.showinfo("Xong", "Đã copy Mã máy. Hãy gửi cho Admin để nhận Key!")
            
        self._btn(hw_f, "Copy", copy_id, color="#30363D").pack(side=LEFT, padx=5)

        key_f = self._card(self, "Nhập License Key")
        key_f.pack(fill=X, padx=20, pady=5)
        
        self.key_entry = Entry(key_f, width=45, font=("Consolas", 9),
                               bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.key_entry.pack(padx=10, pady=10, ipady=5)

        btn_f = Frame(self, bg=BG)
        btn_f.pack(fill=X, padx=20, pady=15)
        
        self._btn(btn_f, " KÍCH HOẠT ", self._activate, color=GREEN).pack(side=LEFT, fill=X, expand=True, ipady=8, padx=(0,5))
        self._btn(btn_f, " THOÁT ", self.destroy, color="#444C56").pack(side=LEFT, ipady=8, ipadx=10)

    def _activate(self):
        key = self.key_entry.get().strip()
        if not key:
            messagebox.showerror("Lỗi", "Vui lòng nhập Key!")
            return
            
        is_ok, msg = validate_key(key)
        if is_ok:
            save_license(key)
            messagebox.showinfo("Thành công", f"Bạn đã kích hoạt thành công!\nThời hạn đến: {msg}")
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Thất bại", msg)
