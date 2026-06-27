import os
import shiny

print("RUNNING:", os.path.abspath(__file__))
print("CURRENT DIR:", os.getcwd())
print("WWW EXISTS:", os.path.isdir("www"))
print("WWW FILES:", os.listdir("www") if os.path.isdir("www") else "NOT FOUND")
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
import os
import shiny

print("RUNNING:", os.path.abspath(__file__))
print("CURRENT DIR:", os.getcwd())
print("WWW EXISTS:", os.path.isdir("www"))
print("WWW FILES:", os.listdir("www") if os.path.isdir("www") else "NOT FOUND")
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
