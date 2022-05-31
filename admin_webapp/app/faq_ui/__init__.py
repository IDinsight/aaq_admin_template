from flask import Blueprint

faq_ui = Blueprint(
    "faq_ui",
    __name__,
    template_folder="templates",
    static_url_path="/landing/static",
    static_folder="./static",
    url_prefix="/faqs",
)

from .. import auth
from . import views
