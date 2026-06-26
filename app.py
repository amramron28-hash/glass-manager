import os
import shiny

print("RUNNING:", os.path.abspath(__file__))
print("Shiny version:", shiny.__version__)

from shiny import App

from ui_components import app_ui
from server import server

print("BEFORE APP CREATE")

app = App(
    app_ui,
    server
)

print("APP CREATED")
