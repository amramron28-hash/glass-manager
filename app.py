import os
from pathlib import Path
import inspect
import shiny

print("RUNNING:", os.path.abspath(__file__))
print("CURRENT DIR:", os.getcwd())

print("APP FILE:", Path(__file__).resolve())
print("WWW ABS:", Path("www").resolve())
print("WWW EXISTS:", Path("www").is_dir())
print("SERVICE EXISTS:", Path("www/service-worker.js").exists())

if Path("www").is_dir():
    print("WWW FILES:", os.listdir("www"))
else:
    print("WWW FILES: NOT FOUND")

print("Shiny version:", shiny.__version__)

from shiny import App

print("APP SIGNATURE:", inspect.signature(App))

from ui_components import app_ui
from server import server

print("BEFORE APP CREATE")

app = App(
    app_ui,
    server,
    static_assets="www"
)

print("APP CREATED")
