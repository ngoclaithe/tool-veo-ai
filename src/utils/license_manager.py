import os
import subprocess
import hashlib
import base64
import json
from datetime import datetime, timedelta

_S1 = "V3oF1ow_"
_S2 = "Adm1n_Pr0_"
_S3 = "2024_Secur1ty_"
_S4 = "T3chV1et_#"
_SIGN_SALT = "SiGn_V3o_2024" 

def _get_salt():
    return f"{_S1}{_S2}{_S3}{_S4}"

def get_hwid():
    """Lấy Hardware ID bằng MAC Address (Phương thức an toàn, tránh bị AV quét)"""
    try:
        node = uuid.getnode()
        raw_id = str(node)
        raw_id += os.getenv('COMPUTERNAME', 'VEO-USER')
        
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()
    except:
        return "USER-VEO-DEFAULT"

def transform_data(data, key):
    """Hàm biến đổi dữ liệu XOR nâng cao"""
    out = []
    k = key * (len(data) // len(key) + 1)
    for i in range(len(data)):
        out.append(chr(ord(data[i]) ^ ord(k[i])))
    return "".join(out)

def generate_license_key(machine_id, days=30):
    """Admin dùng hàm này để tạo Key với Chữ Ký bảo mật"""
    expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    sig_raw = f"{machine_id}|{expiry_date}|{_SIGN_SALT}"
    signature = hashlib.sha256(sig_raw.encode()).hexdigest()[:12]
    
    payload = {
        "mid": machine_id,
        "exp": expiry_date,
        "sig": signature
    }
    
    json_str = json.dumps(payload)
    encrypted = transform_data(json_str, _get_salt())
    return base64.b64encode(encrypted.encode()).decode()

def validate_key(key_str):
    """Kiểm tra Key có hợp lệ, khớp máy và đúng chữ ký không"""
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
            
        # 2. Kiểm tra Machine ID
        if mid != get_hwid():
            return False, "Key này không dành cho máy này!"
            
        # 3. Kiểm tra ngày hết hạn
        exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
        if datetime.now() > exp_date:
            return False, f"Key đã hết hạn vào ngày {exp_str}"
            
        return True, exp_str
    except:
        return False, "License Key không hợp lệ!"

def get_license_file_path():
    """Lưu file license trong AppData/Roaming/... để tránh bị xóa khi đổi thư mục tool"""
    appdata = os.getenv('APPDATA')
    path = os.path.join(appdata, "TechVietAI", "Veo3Flow")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "license.dat")

def save_license(key_str):
    with open(get_license_file_path(), "w") as f:
        f.write(key_str)

def check_local_license():
    """Kiểm tra xem máy đã có license còn hạn chưa"""
    path = get_license_file_path()
    if not os.path.exists(path):
        return False, "Chưa kích hoạt bản quyền"
    
    with open(path, "r") as f:
        key_str = f.read().strip()
    
    return validate_key(key_str)
