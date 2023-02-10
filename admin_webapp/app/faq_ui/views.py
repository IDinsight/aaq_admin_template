from datetime import datetime

import requests
from flask import (
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from ..auth import auth
from ..data_models import FAQModel
from ..database_sqlalchemy import db
from ..utils import load_parameters
from . import faq_ui
from .form_models import AddFAQForm

##############################################################################
# Database management endpoints
##############################################################################


@faq_ui.route("/view", defaults={"page_num": 1}, methods=["GET"])
@faq_ui.route("/view/<page_num>", methods=["GET"])
@faq_ui.route("/", defaults={"page_num": 1}, methods=["GET"])
@faq_ui.route("/<page_num>", methods=["GET"])
@auth.login_required(role="read")
def view_faqs(page_num):
    """
    Displays all FAQs from database
    """
    faqs_page = FAQModel.query.order_by(FAQModel.faq_id).paginate(
        page=int(page_num), per_page=current_app.config["NUM_FAQS_PER_PAGE"]
    )
    # faqs.sort(key=lambda x: x.faq_id)

    for faq in faqs_page.items:
        faq.faq_content_to_send = faq.faq_content_to_send.split("\n")

    return render_template("view_faqs.html", faqs_page=faqs_page)


def validate_tags(tag_list):
    """
    Validate the tags being added. See /validate-tags endpoint in
    core app for more details on validation
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


def validate_contexts(context_list):
    """
    Validate the contexts being added. See /check-contexts endpoint in
    core app for more details on validation
    """
    api_call_body = {"contexts_to_check": context_list}
    bad_contexts_endpoint = "%s://%s:%s/tools/check-contexts" % (
        current_app.MODEL_PROTOCOL,
        current_app.MODEL_HOST,
        current_app.MODEL_PORT,
    )
    headers = {"Authorization": "Bearer %s" % current_app.INBOUND_CHECK_TOKEN}
    response = requests.post(bad_contexts_endpoint, json=api_call_body, headers=headers)
    bad_contexts = response.json()

    return bad_contexts


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
    question_data = faq_to_edit.faq_questions
    context_data = faq_to_edit.faq_contexts
    if form.validate_on_submit():
        if faq_validate_save_and_refresh(form, None, faq_to_edit):
            return redirect(url_for(".view_faqs"))

    return render_template(
        "edit_faq.html",
        faq_to_edit=faq_to_edit,
        form=form,
        tag_data=tag_data,
        question_data=question_data,
        context_data=context_data,
    )


def faq_validate_save_and_refresh(form, thresholds, faq_to_edit):
    """
    Check fields in the FAQ form and save edit to FAQ or new FAQ.

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
    bad_tags, tag_data = check_bad_tags(form)
    bad_contexts, context_data = check_bad_contexts(form)

    question_data = [
        form.question_1.data,
        form.question_2.data,
        form.question_3.data,
        form.question_4.data,
        form.question_5.data,
        form.question_6.data,
        form.question_7.data,
        form.question_8.data,
        form.question_9.data,
        form.question_10.data,
    ]
    question_data = list(filter(None, question_data))

    if len(bad_tags) > 0:
        flash(
            "The following tags are invalid: %s.\nPlease correct and resubmit."
            % str(bad_tags),
            "danger",
        )

        return False

    if len(bad_contexts) > 0:
        flash(
            "The following contexts are invalid: %s.\nPlease correct and resubmit."
            % str(bad_contexts),
            "danger",
        )

        return False

    faq_id = faq_to_edit.faq_id if faq_to_edit is not None else None
    is_duplicate = is_faq_title_already_used(form.faq_title.data, faq_id)

    if is_duplicate:
        flash(
            "The following faq title already exists: %s.\nPlease correct and resubmit."
            % str(form.faq_title.data),
            "danger",
        )
        return False

    if not is_question_valid(questions_data):
        return False

    faq_id, action = upsert_faq(
        form, thresholds, faq_to_edit, tag_data, question_data, context_data
    )
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


def is_question_valid(questions):
    """Make sure each question is valid before adding to DB (not empty )"""
    bad_questions = [question for question in questions if not question.strip()]

    if len(bad_questions) > 0:
        flash(
            "The following questions are invalid: %s.\nPlease correct and resubmit."
            % str(bad_questions),
            "danger",
        )
        return False
    return True


def check_bad_tags(form):
    """
    Check if there are bad tags
    Parameters
    ----------
    form : AddFAQForm
        A WTForm. Defined in app/faq_ui/form_models.py
    Returns
    -------

    bad_tags: List[str]
        list of bad_tags
    tag_data: List[str]
        list of all tags


    """

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

    # check if all tags are valid
    bad_tags = validate_tags(tag_data)
    return bad_tags, tag_data


def check_bad_contexts(form):
    """
    Check if there are bad contexts (contexts not existing in the app context list)
    Parameters
    ----------
    form : AddFAQForm
        A WTForm. Defined in app/faq_ui/form_models.py
    Returns
    -------

    bad_contexts: List[str]
        list of bad contexts
    context_data: List[str]
        list of all contexts


    """

    context_data = [
        form.context_1.data,
        form.context_2.data,
        form.context_3.data,
        form.context_4.data,
        form.context_5.data,
        form.context_6.data,
        form.context_7.data,
        form.context_8.data,
        form.context_9.data,
        form.context_10.data,
    ]
    context_data = list(filter(None, context_data))

    # check if all contexts are valid
    bad_contexts = validate_contexts(context_data)
    return bad_contexts, context_data


def upsert_faq(form, thresholds, faq_to_edit, tag_data, question_data, context_data):
    """
    save edit to FAQ or create new FAQ.

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
    tag_data: list[str]
            List of faq tags
    question_data: list[str]
            List of faq questions
    context_data: list[str]
            List of faq context

    Returns
    -------
    (faq_id, action)
        faq_id:
            id of the new/modified faq
        action: str
            upsert mode ("added new" if new faq added or "edited" if edited faq)


    """

    current_ts = datetime.utcnow()

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
            faq_questions=question_data,
            faq_contexts=context_data,
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
        faq_to_edit.faq_questions = question_data
        faq_to_edit.faq_contexts = context_data
        faq_to_edit.faq_updated_utc = current_ts

        faq_id = faq_to_edit.faq_id
        action = "edited"

        db.session.commit()
    return faq_id, action


def is_faq_title_already_used(title, faq_id):
    """Check if title has duplicates in database"""

    faqs = (
        db.session.query(FAQModel.faq_title, FAQModel.faq_id)
        .filter(FAQModel.faq_title == title)
        .all()
    )

    titles_dict = dict(faqs)

    if len(titles_dict) == 0:
        return False
    elif (faq_id is None) or (titles_dict.get(title) != faq_id):
        return True
    else:
        return False
