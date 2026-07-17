import os
from pathlib import Path
from PIL import Image

import shiny
from shiny import App

from ui_main import app_ui
from server import server

# =====================================================
# PATHS
# =====================================================

APP_DIR = Path(__file__).resolve().parent
WWW_DIR = APP_DIR / "www"

# =====================================================
# GENERATE PWA ICON
# =====================================================

try:

    jpg_path = WWW_DIR / "AMMAR.jpg"
    png_path = WWW_DIR / "AMMAR.png"

    if jpg_path.exists():

        with Image.open(jpg_path) as img:

            img = img.convert("RGBA")

            # إنشاء أيقونة عالية الجودة
            icon = img.resize(
                (512, 512),
                Image.LANCZOS
            )

            icon.save(
                png_path,
                format="PNG",
                optimize=True
            )

        print("✅ SUCCESS: PWA icon regenerated successfully!")

    else:

        print("⚠️ AMMAR.jpg not found.")

except Exception as e:

    print("⚠️ PWA Image Conversion Error:", e)

# =====================================================
# INFORMATION
# =====================================================

print("RUNNING:", Path(__file__).resolve())
print("CURRENT DIR:", os.getcwd())
print("WWW PATH:", WWW_DIR)
print("WWW EXISTS:", WWW_DIR.exists())

if WWW_DIR.exists():

    print("WWW FILES:", os.listdir(WWW_DIR))

print("Shiny version:", shiny.__version__)

# =====================================================
# CREATE APP
# =====================================================

app = App(

    ui=app_ui,

    server=server,

    static_assets=WWW_DIR,

    debug=True,

)

print("APP CREATED SUCCESSFULLY")
