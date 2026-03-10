import json
import uuid
import hashlib
import base64
import urllib.request
from datetime import datetime, timedelta, timezone
import os
import sys
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
    load_dotenv(os.path.join(bundle_dir, ".env"))
else:
    load_dotenv()

_S1 = os.getenv("LICENSE_SECRET_SALT", "V3oF1ow_Adm1n_Pr0_2024_Secur1ty_T3chV1et_#")
_SIGN_SALT = os.getenv("LICENSE_SIGN_SALT", "SiGn_V3o_2024")

def _get_salt():
    return _S1

def _get_network_time():
    try:
        res = urllib.request.urlopen('http://www.google.com', timeout=3)
        date_str = res.headers['Date']
        net_dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=timezone.utc)
        return net_dt
    except:
        return datetime.now(timezone.utc)

def get_hwid():
    try:
        node = uuid.getnode()
        raw_id = str(node)
        raw_id += os.getenv('COMPUTERNAME', 'VEO-USER')
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()
    except:
        return "USER-VEO-DEFAULT"

def transform_data(data, key):
    out = []
    k = key * (len(data) // len(key) + 1)
    for i in range(len(data)):
        out.append(chr(ord(data[i]) ^ ord(k[i])))
    return "".join(out)

def generate_license_key(machine_id, days=30, hours=0):
    now_utc = _get_network_time()
    expiry_dt = now_utc + timedelta(days=days, hours=hours)
    expiry_str = expiry_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    sig_raw = f"{machine_id}|{expiry_str}|{_SIGN_SALT}"
    signature = hashlib.sha256(sig_raw.encode()).hexdigest()[:12]
    
    payload = {
        "mid": machine_id,
        "exp": expiry_str,
        "sig": signature
    }
    
    json_str = json.dumps(payload)
    encrypted = transform_data(json_str, _get_salt())
    return base64.b64encode(encrypted.encode()).decode()

def validate_key(key_str):
    try:
        decoded = base64.b64decode(key_str).decode()
        decrypted_str = transform_data(decoded, _get_salt())
        data = json.loads(decrypted_str)
        
        mid = data.get("mid")
        exp_str = data.get("exp")
        sig = data.get("sig")
        
        sig_check_raw = f"{mid}|{exp_str}|{_SIGN_SALT}"
        expected_sig = hashlib.sha256(sig_check_raw.encode()).hexdigest()[:12]
        
        if sig != expected_sig:
            return False, "Key đã bị chỉnh sửa hoặc giả mạo!"
            
        if mid != get_hwid():
            return False, "Key này không dành cho máy này!"
            
        exp_date_utc = datetime.strptime(exp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        now_utc = _get_network_time()
        
        if now_utc > exp_date_utc:
            return False, f"Key đã hết hạn vào lúc {exp_str} (Giờ UTC)"
            
        return True, exp_str
    except:
        return False, "License Key không hợp lệ!"

def get_license_file_path():
    appdata = os.getenv('APPDATA')
    path = os.path.join(appdata, "TechVietAI", "Veo3Flow")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "license.dat")

def save_license(key_str):
    with open(get_license_file_path(), "w") as f:
        f.write(key_str)

def check_local_license():
    path = get_license_file_path()
    if not os.path.exists(path):
        return False, "Chưa kích hoạt bản quyền"
    
    with open(path, "r") as f:
        key_str = f.read().strip()
    
    return validate_key(key_str)
