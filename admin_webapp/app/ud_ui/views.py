import json
import re
from datetime import datetime

import requests
from flask import current_app, flash, redirect, render_template, request, url_for

from ..auth import auth
from ..data_models import RulesModel
from ..database_sqlalchemy import db
from . import ud_ui
from .form_models import AddRuleForm, CheckRulesForm

##############################################################################
# URGENCY DETECTION ENDPOINTS
##############################################################################


def refresh_rules_core():
    """
    Calls the core app's /internal/refresh-rules endpoint
    """
    refresh_rules_endpoint = "%s://%s:%s/internal/refresh-rules" % (
        current_app.UD_PROTOCOL,
        current_app.UD_HOST,
        current_app.UD_PORT,
    )
    headers = {"Authorization": "Bearer %s" % current_app.UD_INBOUND_CHECK_TOKEN}
    response = requests.get(refresh_rules_endpoint, headers=headers)

    if response.status_code != 200:
        message = (
            f"Request to refresh urgency reuls in the core app failed: {response.text}"
        )
        flash(message, "warning")
    else:
        message = f"{response.text} in the core app."
        flash(message, "info")


@ud_ui.route("/check-new-urgency-rules", methods=["GET", "POST"])
@auth.login_required
def check_new_urgency_rules():
    """
    Hosts and accepts CheckTagsForm

    On submission, sends POST with form content to
    MODEL_HOST:MODEL_PORT/tools/check-new-urgency-rules, formatted per API.

    Prints results of checking new tags
    """
    form = CheckRulesForm()
    query_results = []
    preprocessed_include_kws = []
    preprocessed_exclude_kws = []

    if form.validate_on_submit():
        include_kw_list = get_form_data(form, "^include_[1-9]+$")
        exclude_kw_list = get_form_data(form, "^exclude_[1-9]+$")

        queries = [
            form.query_1.data,
            form.query_2.data,
            form.query_3.data,
            form.query_4.data,
            form.query_5.data,
        ]
        queries = list(filter(None, queries))

        api_call_body = {
            "include_keywords": include_kw_list,
            "exclude_keywords": exclude_kw_list,
            "queries_to_check": queries,
        }
        headers = {"Authorization": "Bearer %s" % current_app.UD_INBOUND_CHECK_TOKEN}

        endpoint = "%s://%s:%s/tools/check-new-rules" % (
            current_app.UD_PROTOCOL,
            current_app.UD_HOST,
            current_app.UD_PORT,
        )
        response = requests.post(endpoint, json=api_call_body, headers=headers)
        response_json = response.json()
        query_results = list(
            zip(response_json["preprocessed_queries"], response_json["urgency_scores"])
        )
        preprocessed_include_kws = response_json["preprocessed_include_kws"]
        preprocessed_exclude_kws = response_json["preprocessed_exclude_kws"]

    return render_template(
        "check_new_urgency_rules.html",
        form=form,
        results=query_results,
        include=preprocessed_include_kws,
        exclude=preprocessed_exclude_kws,
    )


@ud_ui.route("/ud-rules/view", methods=["GET"])
@auth.login_required(role="read")
def view_rules():
    """
    Displays all rules from database
    """
    rules = RulesModel.query.all()
    rules.sort(key=lambda x: x.urgency_rule_id)

    return render_template("view_urgency_rules.html", rules=rules)


@ud_ui.route("/ud-rules/add", methods=["GET", "POST"])
@auth.login_required(role="add")
def add_rule():
    """
    Handles form and POST to add an rule
    """
    form = AddRuleForm()
    include_data_prefill = None
    exclude_data_prefill = None

    if request.form is not None:
        post_form_dict = request.form.to_dict()

        include_str = post_form_dict.get("include", None)
        if include_str is not None:
            include_data_prefill = json.loads(include_str.replace("'", '"'))

        exclude_str = post_form_dict.get("exclude", None)
        if exclude_str is not None:
            exclude_data_prefill = json.loads(exclude_str.replace("'", '"'))
    if form.validate_on_submit():
        if ud_upsert_rule(form, None):
            refresh_rules_core()
            return redirect(url_for(".view_rules"))

    return render_template(
        "add_urgency_rule.html",
        form=form,
        include_data_prefill=include_data_prefill,
        exclude_data_prefill=exclude_data_prefill,
    )


@ud_ui.route("/ud-rules/edit/<edit_rule_id>", methods=["GET", "POST"])
@auth.login_required(role="add")
def edit_rule(edit_rule_id):
    """
    Handles displaying form and POST to edit existing rule

    Parameter edit_rule_id must be provided and valid
    """
    if not edit_rule_id.isdigit():
        return "rule ID must be a positive integer. You entered: %s" % edit_rule_id, 404

    rule_to_edit = RulesModel.query.get(edit_rule_id)
    if rule_to_edit is None:
        return "No rule with ID: %s" % edit_rule_id, 404

    form = AddRuleForm(obj=rule_to_edit)

    if form.validate_on_submit():
        if ud_upsert_rule(form, rule_to_edit):
            refresh_rules_core()
            return redirect(url_for(".view_rules"))

    return render_template(
        "edit_urgency_rule.html",
        rule_to_edit=rule_to_edit,
        form=form,
    )


@ud_ui.route("/ud-rules/delete/<delete_rule_id>", methods=["GET", "POST"])
@auth.login_required(role="add")
def delete_rule(delete_rule_id):
    """
    Handles displaying form and POST to delete existing urgency rule

    Parameter delete_rule_id must be provided and valid
    """
    if not delete_rule_id.isdigit():
        return "Invalid Urgency Rule ID: %s" % delete_rule_id, 404

    rule_to_delete = RulesModel.query.get(delete_rule_id)
    if rule_to_delete is None:
        return "No Urgency Rule with ID: %s" % delete_rule_id, 404

    # If POST (so user confirmed by clicking button on this page),
    # then delete rule
    if request.method == "POST":
        db.session.delete(rule_to_delete)
        db.session.commit()

        flash(
            "Successfully deleted Urgency Rule with ID: %s" % delete_rule_id, "warning"
        )

        refresh_rules_core()

        return redirect(url_for(".view_rules"))

    # Otherwise load form
    else:
        return render_template(
            "delete_urgency_rule.html",
            rule_to_delete=rule_to_delete,
        )


def ud_upsert_rule(form, rule_to_edit):
    """
    Create or edit a rule based on form data

    """

    include_data = get_form_data(form, "^include_[1-9]+$")
    exclude_data = get_form_data(form, "^exclude_[1-9]+$")

    rule_id = rule_to_edit.urgency_rule_id if rule_to_edit is not None else None

    is_duplicate = is_rule_title_already_used(form.rule_title.data, rule_id)
    if is_duplicate:
        flash(
            "The following urgency rule already exists: %s.\nPlease correct and resubmit."
            % str(form.rule_title.data),
            "danger",
        )
        return False
    if rule_to_edit is None:
        current_ts = datetime.utcnow()
        new_rule = RulesModel(
            urgency_rule_added_utc=current_ts,
            urgency_rule_author=form.rule_author.data,
            urgency_rule_title=form.rule_title.data,
            urgency_rule_tags_include=include_data,
            urgency_rule_tags_exclude=exclude_data,
        )

        db.session.add(new_rule)
        db.session.commit()

        rule_id = new_rule.urgency_rule_id
        action = "added new"

    else:
        rule_to_edit.urgency_rule_author = form.rule_author.data
        rule_to_edit.urgency_rule_title = form.rule_title.data
        rule_to_edit.urgency_rule_tags_include = include_data
        rule_to_edit.urgency_rule_tags_exclude = exclude_data
        rule_id = rule_to_edit.urgency_rule_id

        db.session.commit()
        action = "edited"

    flash(f"Successfully {action} rule with ID: %s" % rule_id, "info")

    return True


def is_rule_title_already_used(title, rule_id):
    """Check if title has duplicates in database"""

    rules = (
        db.session.query(RulesModel.urgency_rule_title, RulesModel.urgency_rule_id)
        .filter(RulesModel.urgency_rule_title == title)
        .all()
    )

    titles_dict = dict(rules)
    if len(titles_dict) == 0:
        return False
    elif (rule_id is None) or (titles_dict.get(title) != rule_id):
        return True


def get_form_data(form, field_regex):
    """
    Returns form data as a list
    """

    attributes = form.__class__.__dict__.keys()
    form_data = [
        getattr(form, attr).data for attr in attributes if re.search(field_regex, attr)
    ]
    form_data_no_nulls = list(filter(None, form_data))
    return form_data_no_nulls
