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

            # تحويل إلى RGBA (شفافية)
            img = img.convert("RGBA")

            # الحصول على الأبعاد الأصلية
            width, height = img.size

            # إنشاء صورة مربعة (Crop من المنتصف إذا لزم الأمر)
            if width != height:
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                right = left + size
                bottom = top + size
                img = img.crop((left, top, right, bottom))

            # إنشاء أيقونة عالية الجودة 512x512
            icon = img.resize(
                (512, 512),
                Image.LANCZOS
            )

            # حفظ كـ PNG
            icon.save(
                png_path,
                format="PNG",
                optimize=True,
                quality=95
            )

        print("✅ SUCCESS: PWA icon regenerated successfully!")
        print(f"   Source: {jpg_path}")
        print(f"   Output: {png_path}")

    else:

        print("⚠️ AMMAR.jpg not found in www folder.")
        print(f"   Expected path: {jpg_path}")
        print(f"   WWW folder exists: {WWW_DIR.exists()}")
        if WWW_DIR.exists():
            print(f"   WWW files: {os.listdir(WWW_DIR)}")

except Exception as e:

    print("❌ PWA Image Conversion Error:", e)
    import traceback
    traceback.print_exc()

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
