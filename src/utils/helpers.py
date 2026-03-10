import json
import threading

def parse_line(line):
    """Parse 1 dòng: JSON object hoặc plain text.
    Trả về: (prompt_text, aspect_ratio, duration, extra_info)"""
    line = line.strip()
    if line.startswith("{"):
        try:
            obj = json.loads(line)
            prompt = obj.get("prompt", "")
            style = obj.get("style", "")
            camera = obj.get("camera_motion", "")
            aspect = obj.get("aspect_ratio", "16:9")
            duration = obj.get("duration", 8)
            # Ghép style + camera vào cuối prompt để hướng dẫn cảnh
            extra_parts = []
            if style: extra_parts.append(style)
            if camera: extra_parts.append(camera)
            full_prompt = prompt
            if extra_parts:
                full_prompt = f"{prompt}. Style: {', '.join(extra_parts)}"
            return full_prompt, aspect, duration, obj
        except json.JSONDecodeError:
            pass
    # Plain text
    return line, "16:9", 8, {}

def run_in_background(fn, app_instance):
    """Chạy fn trong background thread, bảo vệ double-start"""
    if getattr(app_instance, "running", False):
        app_instance.log("⚠ Đang chạy rồi — chờ hoàn tất trước!")
        return
    threading.Thread(target=fn, daemon=True).start()
