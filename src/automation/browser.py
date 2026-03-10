import os
import time
import shutil
import random
import subprocess
import tempfile
import base64
import urllib.request as _ur
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

from src.constants import CHROME_PROFILE, OUTPUT_DIR_TEXT, FLOW_URL

class BrowserController:
    def __init__(self, log_fn=None):
        self.driver = None
        self.log = log_fn or print
        self.wait = None
        self._download_dir = OUTPUT_DIR_TEXT

    def _opts(self, incognito=False, fresh=False, download_dir=None):
        opts = Options()
        opts.add_argument("--remote-debugging-port=9222")
        if fresh:
            opts.add_argument("--no-first-run")
            opts.add_argument("--no-default-browser-check")
        elif incognito:
            opts.add_argument("--incognito")
        else:
            opts.add_argument(f"--user-data-dir={CHROME_PROFILE}")
            opts.add_argument("--profile-directory=Default")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        
        dl_dir = download_dir or OUTPUT_DIR_TEXT
        os.makedirs(dl_dir, exist_ok=True)
        prefs = {
            "download.default_directory": dl_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        opts.add_experimental_option("prefs", prefs)
        self._download_dir = dl_dir
        return opts

    def connect_existing(self):
        if not HAS_SELENIUM: return False
        try:
            self.log("🔗 Đang kết nối Chrome đang mở (port 9222)...")
            opts = Options()
            opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            svc = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=svc, options=opts)
            self.wait = WebDriverWait(self.driver, 30)
            url = self.driver.current_url
            self.log(f"✅ Kết nối thành công! Đang ở: {url[:60]}")
            return True
        except Exception as e:
            self.log(f"❌ Kết nối thất bại: {e}")
            self.log("💡 Hãy mở Chrome bằng nút 'MỞ CHROME' trong tool thay vì mở thủ công!")
            return False

    def open(self, mode="normal", download_dir=None):
        if not HAS_SELENIUM:
            import tkinter.messagebox as _mb
            try: _mb.showerror("Lỗi", "Chưa cài selenium!\nChạy: pip install selenium webdriver-manager")
            except: pass
            return False
        try:
            self.log("🌐 Đang mở Chrome...")
            opts = self._opts(incognito=(mode == "incognito"), fresh=(mode == "fresh"), download_dir=download_dir)
            svc = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=svc, options=opts)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 30)
            self.driver.get(FLOW_URL)
            self.driver.execute_script("document.body.style.zoom='100%'")
            self.log(f"✅ Chrome mở | Tải về: {self._download_dir}")
            return True
        except Exception as e:
            self.log(f"❌ Lỗi mở Chrome: {e}")
            return False

    def is_alive(self):
        try:
            _ = self.driver.title
            return True
        except:
            return False

    def get_status(self):
        if not self.driver: return "Chưa mở"
        try:
            url = self.driver.current_url
            if "flow" in url: return "✅ Đã mở Flow"
            return f"Đang ở: {url[:50]}"
        except: return "❌ Mất kết nối"

    def new_project(self):
        try:
            self.driver.get(FLOW_URL)
            time.sleep(3)
            try:
                btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jsIRVP")))
                btn.click()
                time.sleep(2.5)
                self.log("✅ Đã tạo dự án mới")
            except TimeoutException:
                try:
                    btn = self.driver.find_element(By.XPATH, "//button[contains(.,'Dự án mới') or contains(.,'New project')]")
                    btn.click()
                    time.sleep(2.5)
                    self.log("✅ Đã tạo dự án mới (fallback)")
                except:
                    self.log("ℹ️ Không thấy nút Dự án mới — tiếp tục")
            return True
        except Exception as e:
            self.log(f"❌ Lỗi tạo dự án: {e}")
            return False

    def set_prompt(self, text):
        def _copy_to_clipboard(t):
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
            tmp.write(t); tmp.close()
            subprocess.run(["powershell", "-Command", f"Get-Content '{tmp.name}' -Raw | Set-Clipboard"], capture_output=True, timeout=5)
            try: os.unlink(tmp.name)
            except: pass

        try:
            box = None
            for sel in ["div.fyuIsy[role='textbox']", "div[role='textbox']", "div[contenteditable='true']"]:
                try:
                    box = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                    if box and box.is_displayed(): break
                    box = None
                except: continue

            if not box:
                self.log("❌ Không tìm thấy ô prompt (15s timeout)")
                return False

            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", box)
            time.sleep(0.4)

            try:
                _copy_to_clipboard(text)
                box.click(); time.sleep(0.3)
                box.send_keys(Keys.CONTROL + "a")
                time.sleep(0.1)
                box.send_keys(Keys.DELETE)
                time.sleep(0.2)
                box.send_keys(Keys.CONTROL + "v")
                time.sleep(0.6)
                actual = self.driver.execute_script("return arguments[0].innerText;", box)
                if actual and actual.strip():
                    self.log(f"✅ Đã dán prompt (Ctrl+V): {text[:60]}...")
                    return True
            except: pass

            try:
                box.click(); time.sleep(0.2)
                self.driver.execute_script("""
                    arguments[0].focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, arguments[1]);
                """, box, text)
                time.sleep(0.5)
                actual = self.driver.execute_script("return arguments[0].innerText;", box)
                if actual and actual.strip():
                    self.log(f"✅ Đã dán prompt (execCommand): {text[:60]}...")
                    return True
            except: pass

            try:
                box.click(); time.sleep(0.3)
                box.send_keys(Keys.CONTROL + "a")
                box.send_keys(Keys.DELETE)
                time.sleep(0.2)
                for chunk in [text[i:i+60] for i in range(0, len(text), 60)]:
                    box.send_keys(chunk)
                    time.sleep(0.08)
                self.log(f"✅ Đã nhập prompt (send_keys): {text[:60]}...")
                return True
            except: pass

            return False
        except Exception as e:
            self.log(f"❌ set_prompt: {e}")
            return False

    def click_generate(self):
        try:
            time.sleep(1.5)
            btn_selectors = [
                (By.CSS_SELECTOR, "button.bMhrec"),
                (By.XPATH, "//button[.//span[normalize-space()='arrow_forward']]"),
                (By.XPATH, "//button[contains(@class,'bMhrec')]"),
            ]
            btn = None
            for by, sel in btn_selectors:
                try:
                    el = self.driver.find_element(by, sel)
                    if el and el.is_displayed():
                        btn = el; break
                except: continue

            if btn:
                disabled = btn.get_attribute("disabled") or btn.get_attribute("aria-disabled")
                if disabled and str(disabled).lower() in ("true", "disabled"):
                    self.log("⚠ Nút Tạo đang disabled — thử Enter key...")
                else:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                    time.sleep(0.3)
                    ActionChains(self.driver).move_to_element(btn).click().perform()
                    self.log("✅ Đã click nút Tạo (ActionChains)")
                    time.sleep(0.5)
                    url_before = self.driver.current_url
                    time.sleep(2)
                    url_after = self.driver.current_url
                    if url_after != url_before or "/edit/" in url_after:
                        self.log("✅ Xác nhận: trang đổi URL — generate đang chạy!")
                        return True

            try:
                box = self.driver.find_element(By.CSS_SELECTOR, "div[role='textbox']")
                box.click(); time.sleep(0.3)
                box.send_keys(Keys.RETURN)
                self.log("⌨️ Sent Enter key → generate")
                return True
            except: pass

            return False
        except Exception as e:
            self.log(f"❌ click_generate: {e}")
            return False

    def wait_for_video(self, timeout=300):
        self.log(f"⏳ Chờ video hoàn thành (tối đa {timeout}s)...")
        start = time.time()
        last_log = 0
        DL_XPATHS = [
            "//button[normalize-space(.)='Tải xuống']", "//button[normalize-space(.)='Download']",
            "//button[@aria-label='Tải xuống' or @aria-label='Download']",
            "//button[contains(.,'Tải xuống') or contains(.,'Download')]",
            "//a[contains(@href,'.mp4') and @download]",
            "//button[.//mat-icon[contains(.,'download')] or .//span[contains(.,'download')]]",
        ]
        while time.time() - start < timeout:
            time.sleep(8)
            elapsed = int(time.time() - start)
            try:
                for xpath in DL_XPATHS:
                    try:
                        btns = self.driver.find_elements(By.XPATH, xpath)
                        if [b for b in btns if b.is_displayed()]:
                            self.log(f"✅ Video xong sau {elapsed}s!")
                            return True
                    except: continue
                vids = self.driver.find_elements(By.TAG_NAME, "video")
                for v in vids:
                    src = v.get_attribute("src") or ""
                    if src and not src.startswith("data:") and len(src) > 10:
                        self.log(f"✅ Video element sẵn sàng sau {elapsed}s!")
                        return True
                if elapsed - last_log >= 30:
                    pct = min(95, int(elapsed / timeout * 100))
                    self.log(f"   ⏳ {elapsed}s/{timeout}s (~{pct}%) — Flow đang render...")
                    last_log = elapsed
            except: pass
        return False

    def wait_and_download(self, save_dir, filename, timeout=300):
        self.log(f"⏳ Chờ video + tự động tải ngay (tối đa {timeout}s)...")
        os.makedirs(save_dir, exist_ok=True)
        start = time.time(); last_log = 0
        try: self.driver.execute_cdp_cmd("Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": save_dir})
        except: pass
        chrome_dl = str(Path.home() / "Downloads")
        watch_dirs = list({save_dir, chrome_dl})
        snap = {d: set(os.listdir(d)) if os.path.exists(d) else set() for d in watch_dirs}
        DL_XPATHS = [
            "//button[normalize-space(.)='Tải xuống']", "//button[normalize-space(.)='Download']",
            "//button[@aria-label='Tải xuống' or @aria-label='Download']",
            "//button[contains(.,'Tải xuống') or contains(.,'Download')]",
            "//a[contains(@href,'.mp4') and @download]",
            "//button[.//mat-icon[contains(.,'download')]]",
        ]
        dl_btn = None
        while time.time() - start < timeout:
            time.sleep(6); elapsed = int(time.time() - start)
            try:
                for xpath in DL_XPATHS:
                    try:
                        btns = self.driver.find_elements(By.XPATH, xpath)
                        vis = [b for b in btns if b.is_displayed()]
                        if vis: dl_btn = vis[0]; break
                    except: continue
                if dl_btn: self.log(f"🎉 Video xong sau {elapsed}s! Click tải ngay..."); break
                vids = self.driver.find_elements(By.TAG_NAME, "video")
                for v in vids:
                    src = v.get_attribute("src") or ""
                    if src and not src.startswith("data:") and len(src) > 10:
                        self.log(f"📹 Video ready ({elapsed}s) — thử JS download...")
                        if self._js_download_fallback(save_dir, filename): return True
                        break
                if elapsed - last_log >= 30:
                    pct = min(95, int(elapsed / timeout * 100))
                    self.log(f"   ⏳ {elapsed}s/{timeout}s (~{pct}%) — đang render...")
                    last_log = elapsed
            except: pass

        if not dl_btn: return self._js_download_fallback(save_dir, filename)

        clicked = False
        for attempt in range(3):
            try:
                if attempt == 0: ActionChains(self.driver).move_to_element(dl_btn).click().perform()
                elif attempt == 1: self.driver.execute_script("arguments[0].click();", dl_btn)
                else: dl_btn.click()
                self.log(f"⬇️ Đã click tải xuống (cách {attempt+1})"); clicked = True; break
            except: time.sleep(0.5)

        if not clicked: return self._js_download_fallback(save_dir, filename)

        deadline = time.time() + 180; new_file = None; new_dir = save_dir; last_sz_log = time.time()
        while time.time() < deadline:
            time.sleep(2)
            for d in watch_dirs:
                if not os.path.exists(d): continue
                current = set(os.listdir(d))
                added = current - snap[d]
                done = [f for f in added if f.lower().endswith(".mp4") and not f.endswith(".crdownload")]
                if done: new_file = done[0]; new_dir = d; break
                partial = [f for f in added if f.endswith(".crdownload")]
                if partial and time.time() - last_sz_log > 8:
                    try: self.log(f"   ⬇️ Đang tải: {os.path.getsize(os.path.join(d, partial[0]))//1024//1024} MB...")
                    except: pass
                    last_sz_log = time.time()
            if new_file: break

        if not new_file: return False
        src = os.path.join(new_dir, new_file); prev = -1; stable = 0
        for _ in range(20):
            time.sleep(1)
            try:
                sz = os.path.getsize(src)
                if sz == prev and sz > 0: stable += 1
                if stable >= 2: break
                else: stable = 0
                prev = sz
            except: break

        dst = os.path.join(save_dir, filename)
        if os.path.exists(dst): dst = dst.replace(".mp4", f"_{time.strftime('%H%M%S')}.mp4")
        try:
            shutil.move(src, dst)
            self.log(f"✅ Đã lưu: {os.path.basename(dst)} ({os.path.getsize(dst)/1024/1024:.1f} MB)")
            return True
        except: return False

    def wait_for_prompt_ready(self, timeout=60):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                for sel in ["div[role='textbox']", "div[contenteditable='true']", "textarea"]:
                    els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    for el in els:
                        if el.is_displayed():
                            if len((el.get_attribute("innerText") or "").strip()) < 20:
                                self.log("✅ Ô prompt sẵn sàng!"); return True
            except: pass
            time.sleep(3)
        return False

    def set_aspect_ratio(self, ratio):
        try:
            ratio_map = {"16:9": ["Ngang", "16:9", "Landscape"], "9:16": ["Dọc", "9:16", "Portrait"], "1:1": ["Vuông", "1:1", "Square"]}
            labels = ratio_map.get(ratio, [])
            for label in labels:
                try:
                    btn = self.driver.find_element(By.XPATH, f"//button[@role='tab' and (contains(.,'{label}') or @aria-label='{label}')]")
                    if btn: btn.click(); time.sleep(0.5); self.log(f"✅ Tỷ lệ: {ratio}"); return True
                except: continue
            return False
        except: return False

    def _js_download_fallback(self, save_dir, filename):
        try:
            video_urls = self.driver.execute_script("""
                var urls = [];
                document.querySelectorAll('video[src]').forEach(v => { if (v.src && v.src.length > 10) urls.push(v.src); });
                document.querySelectorAll('source[src]').forEach(s => { if (s.src && s.src.includes('mp4')) urls.push(s.src); });
                document.querySelectorAll('a[href]').forEach(a => { if (a.href && a.href.includes('.mp4')) urls.push(a.href); });
                return urls;
            """)
            if not video_urls: return False
            url = video_urls[0]
            if url.startswith("blob:"):
                b64 = self.driver.execute_script("""
                    var xhr = new XMLHttpRequest(); xhr.open('GET', arguments[0], false); xhr.responseType = 'arraybuffer'; xhr.send();
                    if (xhr.status !== 200) return null;
                    var arr = new Uint8Array(xhr.response), bin = '';
                    for (var i = 0; i < arr.length; i++) bin += String.fromCharCode(arr[i]);
                    return btoa(bin);
                """, url)
                if b64:
                    dst = os.path.join(save_dir, filename)
                    with open(dst, 'wb') as f: f.write(base64.b64decode(b64))
                    self.log(f"✅ JS blob download: {filename} ({os.path.getsize(dst)/1024/1024:.1f} MB)")
                    return True
            else:
                try:
                    cookies = self.driver.get_cookies(); cookie_str = '; '.join(f"{c['name']}={c['value']}" for c in cookies)
                    req = _ur.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cookie': cookie_str, 'Referer': self.driver.current_url})
                    dst = os.path.join(save_dir, filename)
                    with _ur.urlopen(req, timeout=120) as resp, open(dst, 'wb') as f: f.write(resp.read())
                    self.log(f"✅ URL download: {filename} ({os.path.getsize(dst)/1024/1024:.1f} MB)")
                    return True
                except: pass
        except: pass
        return False

    def upload_image(self, image_path):
        try:
            image_path = str(Path(image_path).resolve())
            plus_btn = None
            for xp in ["//button[.//span[normalize-space()='add_2']]", "//button[@aria-label='Add' or @aria-label='Thêm']", "//button[contains(@class,'add')]"]:
                try:
                    el = WebDriverWait(self.driver, 8).until(EC.element_to_be_clickable((By.XPATH, xp)))
                    if el: plus_btn = el; break
                except: continue
            if plus_btn: ActionChains(self.driver).move_to_element(plus_btn).click().perform(); time.sleep(1.5)
            self.driver.execute_script("""
                document.querySelectorAll("input[type='file']").forEach(function(el) { el.style.cssText = 'display:block!important;opacity:1!important;visibility:visible!important;width:1px!important;height:1px!important;'; });
            """)
            time.sleep(0.4)
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            file_input = None
            for inp in inputs:
                accept = inp.get_attribute("accept") or ""
                if "image" in accept or "video" in accept or "*" in accept: file_input = inp; break
            if not file_input and inputs: file_input = inputs[-1]
            if not file_input: return False
            file_input.send_keys(image_path)
            deadline = time.time() + 25
            while time.time() < deadline:
                time.sleep(2)
                try:
                    if self.driver.find_elements(By.XPATH, "//img[contains(@src,'blob:') or contains(@src,'googleusercontent')]"): return True
                except: pass
            return True
        except: return False

    def wait_and_download_image(self, save_dir, filename, timeout=180):
        os.makedirs(save_dir, exist_ok=True); start = time.time(); last_log = 0
        try: self.driver.execute_cdp_cmd("Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": save_dir})
        except: pass
        chrome_dl = str(Path.home() / "Downloads"); watch_dirs = list({save_dir, chrome_dl})
        snap = {d: set(os.listdir(d)) if os.path.exists(d) else set() for d in watch_dirs}
        DL_XPATHS = ["//button[normalize-space(.)='Tải xuống']", "//button[normalize-space(.)='Download']", "//button[@aria-label='Tải xuống' or @aria-label='Download']", "//button[contains(.,'Tải xuống') or contains(.,'Download')]", "//a[contains(@href,'.png') or contains(@href,'.jpg') or contains(@href,'.webp')]"]
        dl_btn = None
        while time.time() - start < timeout:
            time.sleep(5); elapsed = int(time.time() - start)
            try:
                for xpath in DL_XPATHS:
                    try:
                        btns = self.driver.find_elements(By.XPATH, xpath)
                        vis = [b for b in btns if b.is_displayed()]
                        if vis: dl_btn = vis[0]; break
                    except: continue
                if dl_btn: break
                img_ready = self.driver.execute_script("""
                    var imgs = document.querySelectorAll('img[src]');
                    for (var i = 0; i < imgs.length; i++) {
                        var src = imgs[i].src, w = imgs[i].naturalWidth || 0;
                        if (w > 200 && (src.includes('blob:') || src.includes('googleusercontent') || src.includes('generated'))) return src;
                    }
                    return null;
                """)
                if img_ready:
                    if self._download_image_js(img_ready, save_dir, filename): return True
                if elapsed - last_log >= 30: self.log(f"   ⏳ {elapsed}s/{timeout}s (~{int(elapsed/timeout*100)}%) — đang tạo ảnh..."); last_log = elapsed
            except: pass
        if not dl_btn: return self._download_largest_image(save_dir, filename)
        clicked = False
        for attempt in range(3):
            try:
                if attempt == 0: ActionChains(self.driver).move_to_element(dl_btn).click().perform()
                elif attempt == 1: self.driver.execute_script("arguments[0].click();", dl_btn)
                else: dl_btn.click()
                clicked = True; break
            except: time.sleep(0.5)
        if not clicked: return self._download_largest_image(save_dir, filename)
        deadline = time.time() + 60; new_file = None; img_exts = (".png", ".jpg", ".jpeg", ".webp")
        while time.time() < deadline:
            time.sleep(2)
            for d in watch_dirs:
                if not os.path.exists(d): continue
                current = set(os.listdir(d))
                added = current - snap[d]
                done = [f for f in added if any(f.lower().endswith(e) for e in img_exts) and not f.endswith(".crdownload")]
                if done: new_file = done[0]; break
            if new_file: break
        if not new_file: return self._download_largest_image(save_dir, filename)
        dst = os.path.join(save_dir, filename.rsplit('.', 1)[0] + Path(new_file).suffix)
        try: shutil.move(os.path.join(save_dir if new_file in snap.get(save_dir, set()) else chrome_dl, new_file), dst); return True
        except: return False

    def _download_image_js(self, img_url, save_dir, filename):
        try:
            if img_url.startswith("blob:"):
                b64 = self.driver.execute_script("""
                    var xhr = new XMLHttpRequest(); xhr.open('GET', arguments[0], false); xhr.responseType = 'arraybuffer'; xhr.send();
                    if (xhr.status !== 200) return null;
                    var arr = new Uint8Array(xhr.response), bin = '';
                    for (var i = 0; i < arr.length; i++) bin += String.fromCharCode(arr[i]);
                    return btoa(bin);
                """, img_url)
                if b64:
                    dst = os.path.join(save_dir, filename.rsplit('.', 1)[0] + ".png")
                    with open(dst, 'wb') as f: f.write(base64.b64decode(b64))
                    return True
            else:
                cookies = self.driver.get_cookies(); cookie_str = '; '.join(f"{c['name']}={c['value']}" for c in cookies)
                req = _ur.Request(img_url, headers={'User-Agent': 'Mozilla/5.0', 'Cookie': cookie_str, 'Referer': self.driver.current_url})
                dst = os.path.join(save_dir, filename.rsplit('.', 1)[0] + ".png")
                with _ur.urlopen(req, timeout=30) as resp, open(dst, 'wb') as f: f.write(resp.read())
                return True
        except: return False

    def _download_largest_image(self, save_dir, filename):
        try:
            result = self.driver.execute_script("""
                var best = null, maxW = 0;
                document.querySelectorAll('img[src]').forEach(function(img) { var w = img.naturalWidth || 0; if (w > maxW && w > 200) { maxW = w; best = img.src; } });
                return best;
            """)
            if result: return self._download_image_js(result, save_dir, filename)
        except: pass
        return False
