import os
import sys
from tkinter import Tk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import VeoApp
from src.utils.license_manager import check_local_license
from src.ui.license_window import LicenseWindow

def start_app():
    root = Tk()
    app = VeoApp(root)
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()

def check_and_run():
    is_ok, msg = check_local_license()
    
    if is_ok:
        start_app()
    else:
        license_root = Tk()
        license_root.withdraw() 
        
        def on_success():
            license_root.after(100, start_app)
            
        lw = LicenseWindow(license_root, on_success)
        license_root.mainloop()

try:
    from selenium import webdriver
except ImportError:
    from tkinter import messagebox
    root = Tk()
    root.withdraw()
    messagebox.showerror("Lỗi Môi Trường", 
        "Hệ thống thiếu thư viện Selenium.\n"
        "Đã có lỗi xảy ra trong quá trình đóng gói phần mềm.")
    sys.exit(1)

if __name__ == "__main__":
    check_and_run()
