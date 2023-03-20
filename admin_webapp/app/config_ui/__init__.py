from flask import Blueprint

config_ui = Blueprint(
    "config_ui",
    __name__,
    template_folder="templates",
    static_url_path="/landing/static",
    static_folder="./static",
    url_prefix="/config",
)

from .. import auth
from . import views
