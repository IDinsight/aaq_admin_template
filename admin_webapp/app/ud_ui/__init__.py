from flask import Blueprint

ud_ui = Blueprint(
    "ud_ui",
    __name__,
    template_folder="templates",
    static_url_path="/landing/static",
    static_folder="./static",
    url_prefix="/ud",
)

from .. import auth
from . import views
