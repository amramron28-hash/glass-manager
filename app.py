import os
from pathlib import Path

import shiny
from shiny import App

from ui_main import app_ui
from server import server

# =====================================================
# PATHS
# =====================================================

APP_DIR = Path(__file__).resolve().parent
WWW_DIR = APP_DIR / "www"

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
    debug=False,
)

print("APP CREATED SUCCESSFULLY")
