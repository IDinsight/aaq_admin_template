from datetime import datetime

import requests
from flask import current_app, flash, redirect, render_template, request, url_for

from ..auth import auth
from ..data_models import FAQModel
from ..database_sqlalchemy import db
from ..utils import load_parameters
from . import faq_ui
from .form_models import AddFAQForm

##############################################################################
# Database management endpoints
##############################################################################


@faq_ui.route("/", methods=["GET"])
@faq_ui.route("/view", methods=["GET"])
@auth.login_required(role="read")
def view_faqs():
    """
    Displays all FAQs from database
    """
    faqs = FAQModel.query.all()
    faqs.sort(key=lambda x: x.faq_id)

    for faq in faqs:
        faq.faq_content_to_send = faq.faq_content_to_send.split("\n")

    return render_template("view_faqs.html", faqs=faqs)


def validate_tags(tag_list):
    """
    Validate the tags being added. See /validate-tags endpoint in
    core all for more details on validation
    """
    api_call_body = {"tags_to_check": tag_list}
    bad_tags_endpoint = "%s://%s:%s/tools/validate-tags" % (
        current_app.MODEL_PROTOCOL,
        current_app.MODEL_HOST,
        current_app.MODEL_PORT,
    )
    headers = {"Authorization": "Bearer %s" % current_app.INBOUND_CHECK_TOKEN}
    bad_tags = requests.post(
        bad_tags_endpoint, json=api_call_body, headers=headers
    ).json()

    return bad_tags


def refresh_faqs_core():
    """
    Calls the core app's /internal/refresh-faqs endpoint
    """
    refresh_faqs_endpoint = "%s://%s:%s/internal/refresh-faqs" % (
        current_app.MODEL_PROTOCOL,
        current_app.MODEL_HOST,
        current_app.MODEL_PORT,
    )
    headers = {"Authorization": "Bearer %s" % current_app.INBOUND_CHECK_TOKEN}
    response = requests.get(refresh_faqs_endpoint, headers=headers)

    if response.status_code != 200:
        message = f"Request to refresh FAQs in the core app failed: {response.text}"
        flash(message, "warning")
    else:
        message = f"{response.text} in the core app."
        flash(message, "info")


@faq_ui.route("/add", methods=["GET", "POST"])
@auth.login_required(role="add")
def add_faq():
    """
    Handles form and POST to add an FAQ
    """
    faqs_params = load_parameters("faqs_ui")
    form = AddFAQForm()

    if form.validate_on_submit():
        if faq_validate_save_and_refresh(form, faqs_params["default_threshold"], None):
            return redirect(url_for(".view_faqs"))

    return render_template("add_faq.html", form=form)


@faq_ui.route("/edit/<edit_faq_id>", methods=["GET", "POST"])
@auth.login_required(role="add")
def edit_faq(edit_faq_id):
    """
    Handles displaying form and POST to edit existing FAQ

    Parameter edit_faq_id must be provided and valid
    """
    if not edit_faq_id.isdigit():
        return "FAQ ID must be a positive integer. You entered: %s" % edit_faq_id, 404

    faq_to_edit = FAQModel.query.get(edit_faq_id)
    if faq_to_edit is None:
        return "No FAQ with ID: %s" % edit_faq_id, 404

    form = AddFAQForm(obj=faq_to_edit)
    tag_data = faq_to_edit.faq_tags

    if form.validate_on_submit():
        if faq_validate_save_and_refresh(form, None, faq_to_edit):
            return redirect(url_for(".view_faqs"))

    return render_template(
        "edit_faq.html",
        faq_to_edit=faq_to_edit,
        form=form,
        tag_data=tag_data,
    )


def faq_validate_save_and_refresh(form, thresholds, faq_to_edit):
    """
    Check field in the FAQ form and save edit to FAQ or new FAQ.

    Parameters
    ----------
    form : AddFAQForm
        A WTForm. Defined in app/faq_ui/form_models.py
    thresholds: {float, List}
        The thresholds to apply to each token.
        NOTE: Not currently in use
    faq_to_edit: {FAQModel, None}
        If editing an FAQ then the FAQModel ORM object.
        If creating a new none

    Returns
    -------
    Boolean
        True is record was created / updated
        False if there was an error

    Notes
    -----
    It also flashes the result on the next page that is rendered
    """

    current_ts = datetime.utcnow()

    tag_data = [
        form.tag_1.data,
        form.tag_2.data,
        form.tag_3.data,
        form.tag_4.data,
        form.tag_5.data,
        form.tag_6.data,
        form.tag_7.data,
        form.tag_8.data,
        form.tag_9.data,
        form.tag_10.data,
    ]
    tag_data = list(filter(None, tag_data))

    # Step 1: check if all tags are valid
    bad_tags = validate_tags(tag_data)

    # If unsuccessful
    if len(bad_tags) > 0:
        flash(
            "The following tags are invalid: %s.\nPlease correct and resubmit."
            % str(bad_tags),
            "danger",
        )

        return False
    else:
        if faq_to_edit is None:
            if not isinstance(thresholds, list):
                thresholds = [thresholds] * len(tag_data)

            new_faq = FAQModel(
                faq_added_utc=current_ts,
                faq_updated_utc=current_ts,
                faq_author=form.faq_author.data,
                faq_title=form.faq_title.data,
                faq_content_to_send=form.faq_content_to_send.data,
                faq_weight=form.faq_weight.data,
                faq_tags=tag_data,
                faq_thresholds=thresholds,
            )
            db.session.add(new_faq)
            db.session.commit()

            faq_id = new_faq.faq_id

            action = "added new"

        else:
            faq_to_edit.faq_author = form.faq_author.data
            faq_to_edit.faq_title = form.faq_title.data
            faq_to_edit.faq_content_to_send = form.faq_content_to_send.data
            faq_to_edit.faq_weight = form.faq_weight.data
            faq_to_edit.faq_tags = tag_data
            faq_to_edit.faq_updated_utc = current_ts

            faq_id = faq_to_edit.faq_id
            action = "edited"

            db.session.commit()

        flash(f"Successfully {action} FAQ with ID: %s" % faq_id, "info")

        refresh_faqs_core()

        return True


@faq_ui.route("/delete/<delete_faq_id>", methods=["GET", "POST"])
@auth.login_required(role="add")
def delete_faq(delete_faq_id):
    """
    Handles displaying form and POST to delete existing FAQ

    Parameter delete_faq_id must be provided and valid
    """
    if not delete_faq_id.isdigit():
        return "Invalid FAQ ID: %s" % delete_faq_id, 404

    faq_to_delete = FAQModel.query.get(delete_faq_id)
    if faq_to_delete is None:
        return "No FAQ with ID: %s" % delete_faq_id, 404

    # If POST (so user confirmed by clicking button on this page),
    # then delete FAQ
    if request.method == "POST":
        db.session.delete(faq_to_delete)
        db.session.commit()

        # Flash message, and return to view_faqs
        flash("Successfully deleted FAQ with ID: %s" % delete_faq_id, "warning")

        refresh_faqs_core()

        return redirect(url_for(".view_faqs"))

    # Otherwise load form
    else:
        return render_template(
            "delete_faq.html",
            faq_to_delete=faq_to_delete,
        )
