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
        
        self.update_idletasks()
        w, h = 500, 480
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth() - w)//2}+{(self.winfo_screenheight() - h)//2}")

        self._build()

    def _build(self):
        Label(self, text="🔑 ADMIN LICENSE GENERATOR", 
              font=("Segoe UI", 14, "bold"), bg=BG, fg=ACCENT).pack(pady=20)
        
        mid_f = self._card(self, "Bước 1: Nhập Machine ID của khách")
        mid_f.pack(fill=X, padx=25, pady=5)
        
        self.mid_entry = Entry(mid_f, font=("Consolas", 10),
                               bg="#0D1117", fg=GREEN, insertbackground=TEXT, relief="flat")
        self.mid_entry.pack(fill=X, padx=15, pady=15, ipady=5)
        self.mid_entry.focus()

        time_f = self._card(self, "Bước 2: Thời hạn")
        time_f.pack(fill=X, padx=25, pady=5)
        
        r1 = Frame(time_f, bg=CARD)
        r1.pack(fill=X, padx=15, pady=5)
        Label(r1, text="Số ngày:", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side=LEFT)
        self.days_entry = Entry(r1, font=("Segoe UI", 10), width=10,
                                bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.days_entry.insert(0, "30")
        self.days_entry.pack(side=LEFT, padx=10, ipady=3)
        
        Label(r1, text="Số giờ:", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side=LEFT, padx=(20, 0))
        self.hours_entry = Entry(r1, font=("Segoe UI", 10), width=10,
                                 bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.hours_entry.insert(0, "0")
        self.hours_entry.pack(side=LEFT, padx=10, ipady=3)

        res_f = self._card(self, "Bước 3: License Key tạo được")
        res_f.pack(fill=X, padx=25, pady=5)
        
        self.res_entry = Entry(res_f, font=("Consolas", 9),
                               bg="#0D1117", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.res_entry.pack(fill=X, padx=15, pady=15, ipady=5)

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
            days = float(self.days_entry.get().strip() or 0)
            hours = float(self.hours_entry.get().strip() or 0)
            
            if days <= 0 and hours <= 0:
                messagebox.showerror("Lỗi", "Vui lòng nhập số ngày hoặc số giờ lớn hơn 0!")
                return
                
            key = generate_license_key(mid, days, hours)
            
            self.res_entry.delete(0, END)
            self.res_entry.insert(0, key)
            msg = f"Đã tạo Key thời hạn: {days} ngày, {hours} giờ!"
            messagebox.showinfo("Thành công", msg)
        except ValueError:
            messagebox.showerror("Lỗi", "Số ngày/giờ phải là số (ví dụ: 1 hoặc 0.5)!")
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
