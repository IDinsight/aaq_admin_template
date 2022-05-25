from flask import Blueprint

db_ui = Blueprint(
    "main",
    __name__,
    template_folder="templates",
    static_url_path="/landing/static",
    static_folder="./static",
)

from .. import auth
from . import views
