import json
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
        include_kw_list = [
            form.include_1.data,
            form.include_2.data,
            form.include_3.data,
            form.include_4.data,
            form.include_5.data,
            form.include_6.data,
            form.include_7.data,
            form.include_8.data,
            form.include_9.data,
            form.include_10.data,
        ]
        include_kw_list = list(filter(None, include_kw_list))

        exclude_kw_list = [
            form.exclude_1.data,
            form.exclude_2.data,
            form.exclude_3.data,
            form.exclude_4.data,
            form.exclude_5.data,
            form.exclude_6.data,
            form.exclude_7.data,
            form.exclude_8.data,
            form.exclude_9.data,
            form.exclude_10.data,
        ]
        exclude_kw_list = list(filter(None, exclude_kw_list))

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


@ud_ui.route("/view", methods=["GET"])
@auth.login_required(role="read")
def view_rules():
    """
    Displays all rules from database
    """
    rules = RulesModel.query.all()
    rules.sort(key=lambda x: x.urgency_rule_id)

    return render_template("view_urgency_rules.html", rules=rules)


@ud_ui.route("/add", methods=["GET", "POST"])
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
        added_ts = datetime.utcnow()

        include_data = [
            form.include_1.data,
            form.include_2.data,
            form.include_3.data,
            form.include_4.data,
            form.include_5.data,
            form.include_6.data,
            form.include_7.data,
            form.include_8.data,
            form.include_9.data,
            form.include_10.data,
        ]
        include_data = list(filter(None, include_data))

        exclude_data = [
            form.exclude_1.data,
            form.exclude_2.data,
            form.exclude_3.data,
            form.exclude_4.data,
            form.exclude_5.data,
            form.exclude_6.data,
            form.exclude_7.data,
            form.exclude_8.data,
            form.exclude_9.data,
            form.exclude_10.data,
        ]
        exclude_data = list(filter(None, exclude_data))

        new_rule = RulesModel(
            urgency_rule_added_utc=added_ts,
            urgency_rule_author=form.rule_author.data,
            urgency_rule_title=form.rule_title.data,
            urgency_rule_tags_include=include_data,
            urgency_rule_tags_exclude=exclude_data,
        )

        db.session.add(new_rule)
        db.session.commit()

        # Flash message, and return to view_rules
        flash(
            "Successfully added new rule with ID: %d" % new_rule.urgency_rule_id,
            "success",
        )
        return redirect(url_for(".view_rules"))

    return render_template(
        "add_urgency_rule.html",
        form=form,
        include_data_prefill=include_data_prefill,
        exclude_data_prefill=exclude_data_prefill,
    )


@ud_ui.route("/edit/<edit_rule_id>", methods=["GET", "POST"])
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
        include_data = [
            form.include_1.data,
            form.include_2.data,
            form.include_3.data,
            form.include_4.data,
            form.include_5.data,
            form.include_6.data,
            form.include_7.data,
            form.include_8.data,
            form.include_9.data,
            form.include_10.data,
        ]
        include_data = list(filter(None, include_data))

        exclude_data = [
            form.exclude_1.data,
            form.exclude_2.data,
            form.exclude_3.data,
            form.exclude_4.data,
            form.exclude_5.data,
            form.exclude_6.data,
            form.exclude_7.data,
            form.exclude_8.data,
            form.exclude_9.data,
            form.exclude_10.data,
        ]
        exclude_data = list(filter(None, exclude_data))

        rule_to_edit.urgency_rule_author = form.rule_author.data
        rule_to_edit.urgency_rule_title = form.rule_title.data
        rule_to_edit.urgency_rule_tags_include = include_data
        rule_to_edit.urgency_rule_tags_exclude = exclude_data

        db.session.commit()

        # Flash message, and return to view_rules
        flash("Successfully edited rule with ID: %s" % edit_rule_id, "info")
        return redirect(url_for(".view_rules"))

    return render_template(
        "edit_urgency_rule.html",
        rule_to_edit=rule_to_edit,
        form=form,
    )


@ud_ui.route("/delete/<delete_rule_id>", methods=["GET", "POST"])
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

        # Flash message, and return to view_rules
        flash(
            "Successfully deleted Urgency Rule with ID: %s" % delete_rule_id, "warning"
        )
        return redirect(url_for(".view_rules"))

    # Otherwise load form
    else:
        return render_template(
            "delete_urgency_rule.html",
            rule_to_delete=rule_to_delete,
        )
