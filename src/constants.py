import os
from pathlib import Path

FLOW_URL = "https://labs.google/fx/vi/tools/flow"
CHROME_PROFILE = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data")
OUTPUT_DIR_TEXT = str(Path.home() / "Downloads" / "VEO3_OUTPUT" / "text_to_video")
OUTPUT_DIR_CHAR = str(Path.home() / "Downloads" / "VEO3_OUTPUT" / "character_video")
OUTPUT_DIR_IMAGE = str(Path.home() / "Downloads" / "VEO3_OUTPUT" / "images")

# ─── Colors (Dark Theme) ───
BG      = "#0D1117"   # nền chính
CARD    = "#161B22"   # card/frame
BORDER  = "#30363D"   # viền
TEXT    = "#E6EDF3"   # chữ sáng
MUTED   = "#8B949E"   # chữ mờ
ACCENT  = "#58A6FF"   # xanh dương
GREEN   = "#3FB950"   # xanh lá
RED     = "#F85149"   # đỏ
ORANGE  = "#D29922"   # cam/vàng
PURPLE  = "#BC8CFF"   # tím
