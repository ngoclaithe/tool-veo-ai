"""
Veo 3 Flow Automation Tool
Entry Point
"""
import os
import sys
from tkinter import Tk

# Thêm src vào path nếu cần
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import VeoApp

if __name__ == "__main__":
    # Kiểm tra Selenium
    try:
        from selenium import webdriver
    except ImportError:
        print("📦 Cài selenium + webdriver-manager...")
        os.system("pip install selenium webdriver-manager -q")
        print("✅ Xong! Vui lòng chạy lại.")
        sys.exit(0)

    root = Tk()
    app = VeoApp(root)
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
