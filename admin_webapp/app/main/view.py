import requests
import sqlalchemy as sa
from flask import current_app, render_template
from sqlalchemy.exc import SQLAlchemyError

from ..database_sqlalchemy import db
from . import main

##############################################################################
# INTERNAL ENDPOINTS
##############################################################################


@main.route("/healthcheck", methods=["GET"])
def healthcheck():
    """
    Check if app can connect to model
    Check that FAQ DB exists
    """
    model_connection_string = (
        f"{current_app.MODEL_PROTOCOL}://{current_app.MODEL_HOST}:"
        "9902/auth-healthcheck"
    )

    try:
        headers = {"Authorization": "Bearer %s" % current_app.INBOUND_CHECK_TOKEN}
        response = requests.get(
            model_connection_string,
            headers=headers,
            timeout=10,
        )
        if response.status_code == 401:
            return (
                (
                    "Failed health check - can't connect to model"
                    " - INBOUND_CHECK_TOKEN unauthorized"
                ),
                response.status_code,
            )
        elif response.status_code != 200:
            return (
                (
                    "Failed health check - can't connect to model"
                    " - model's own health check failed"
                ),
                response.status_code,
            )
    except requests.ConnectionError:
        return (
            (
                "Failed health check - cannot connect to model at "
                f"{model_connection_string}"
            ),
            500,
        )

    try:
        db.session.execute("SELECT 1;")
    except SQLAlchemyError:
        return "Failed database connection", 500

    engine = sa.create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    insp = sa.inspect(engine)
    if not insp.has_table("praekelt_idinsight_vaccinefaq_faqmatches"):
        return "FAQ table doesn't exist", 500

    return "Healthy - all checks complete", 200


@main.route("/")
@main.route("/home")
def home():
    """
    Home page
    """
    return render_template("home.html")
