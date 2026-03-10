import os
import sys
from tkinter import *
from tkinter import messagebox
from src.constants import BG, CARD, TEXT, ACCENT, GREEN, RED, MUTED
from src.ui.components.base import UIBase
from src.utils.license_manager import generate_license_key

class AdminGenWindow(Tk, UIBase):
    def __init__(self):
        super().__init__()
        self.title("VEO 3 FLOW - ADMIN KEY GEN")
        self.geometry("500x480")
        self.configure(bg=BG)
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        w, h = 500, 480
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth() - w)//2}+{(self.winfo_screenheight() - h)//2}")

        self._build()

    def _build(self):
        # Header
        Label(self, text="🔑 ADMIN LICENSE GENERATOR", 
              font=("Segoe UI", 14, "bold"), bg=BG, fg=ACCENT).pack(pady=20)
        
        # Input Machine ID
        mid_f = self._card(self, "Bước 1: Nhập Machine ID của khách")
        mid_f.pack(fill=X, padx=25, pady=5)
        
        self.mid_entry = Entry(mid_f, font=("Consolas", 10),
                               bg="#0D1117", fg=GREEN, insertbackground=TEXT, relief="flat")
        self.mid_entry.pack(fill=X, padx=15, pady=15, ipady=5)
        self.mid_entry.focus()

        # Input Days
        days_f = self._card(self, "Bước 2: Thời hạn (số ngày)")
        days_f.pack(fill=X, padx=25, pady=5)
        
        self.days_entry = Entry(days_f, font=("Segoe UI", 10), width=15,
                                bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.days_entry.insert(0, "30")
        self.days_entry.pack(padx=15, pady=15, ipady=5, anchor=W)

        # Result Key
        res_f = self._card(self, "Bước 3: License Key tạo được")
        res_f.pack(fill=X, padx=25, pady=5)
        
        self.res_entry = Entry(res_f, font=("Consolas", 9),
                               bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.res_entry.pack(fill=X, padx=15, pady=15, ipady=5)

        # Action Buttons
        btn_f = Frame(self, bg=BG)
        btn_f.pack(fill=X, padx=25, pady=20)
        
        self._btn(btn_f, " TẠO KEY ", self._generate, color=GREEN).pack(side=LEFT, fill=X, expand=True, ipady=10, padx=(0,5))
        self._btn(btn_f, " COPY KEY ", self._copy, color="#30363D").pack(side=LEFT, fill=X, expand=True, ipady=10)

    def _generate(self):
        mid = self.mid_entry.get().strip()
        if not mid:
            messagebox.showerror("Lỗi", "Chưa nhập Machine ID của khách!")
            return
            
        try:
            days = int(self.days_entry.get().strip() or 30)
            key = generate_license_key(mid, days)
            
            self.res_entry.delete(0, END)
            self.res_entry.insert(0, key)
            messagebox.showinfo("Thành công", f"Đã tạo Key thời hạn {days} ngày!")
        except ValueError:
            messagebox.showerror("Lỗi", "Số ngày phải là số nguyên!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

    def _copy(self):
        key = self.res_entry.get().strip()
        if key:
            self.clipboard_clear()
            self.clipboard_append(key)
            messagebox.showinfo("Xong", "Đã copy Key vào bộ nhớ tạm!")
        else:
            messagebox.showwarning("Lưu ý", "Chưa có Key để copy!")

if __name__ == "__main__":
    app = AdminGenWindow()
    app.mainloop()
