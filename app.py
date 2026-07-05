import os
from pathlib import Path
import inspect
import shiny

from shiny import App
from ui_components import app_ui
from server import server

# =========================
# PATH SETUP
# =========================
APP_DIR = Path(__file__).parent.resolve()
WWW_DIR = APP_DIR / "www"

print("RUNNING:", os.path.abspath(__file__))
print("CURRENT DIR:", os.getcwd())
print("APP FILE:", Path(__file__).resolve())
print("WWW ABS:", WWW_DIR)
print("WWW EXISTS:", WWW_DIR.is_dir())
print("SERVICE EXISTS:", (WWW_DIR / "service-worker.js").exists())

if WWW_DIR.is_dir():
    print("WWW FILES:", os.listdir(WWW_DIR))

print("Shiny version:", shiny.__version__)
print("APP SIGNATURE:", inspect.signature(App))
print("BEFORE APP CREATE")

# =========================
# APP (FIXED STATIC ROUTING)
# =========================
app = App(
    app_ui,
    server,
    static_assets={
        "/": WWW_DIR,
        "/www": WWW_DIR
    },
    debug=False
)

print("APP CREATED")
