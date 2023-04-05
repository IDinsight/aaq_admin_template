import json
import secrets
from datetime import datetime

from flask import flash, jsonify, redirect, render_template, url_for
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from ..auth import auth
from ..data_models import ContextualizationModel
from ..database_sqlalchemy import db
from . import config_ui
from .form_models import AddLangCtxForm

##############################################################################
# Contextualization management endpoints
##############################################################################


@config_ui.route("/edit-language-context", methods=["GET", "POST"])
@auth.login_required(role="add")
def edit_lang_ctx_config():
    """
    Handles form and POST to add an FAQ
    """
    contextualization = (
        db.session.query(ContextualizationModel)
        .filter(ContextualizationModel.active)
        .first()
    )

    form = AddLangCtxForm(obj=contextualization)
    if form.is_submitted():
        if validate_and_save_contextualization_config(form, contextualization):
            return jsonify({"success": True, "redirect": url_for("main.home")})

    return render_template(
        "edit_lang_ctx.html",
        version_id=contextualization.version_id,
        custom_wvs=contextualization.custom_wvs,
        pairwise_triplewise_entities=contextualization.pairwise_triplewise_entities,
        tag_guiding_typos=contextualization.tag_guiding_typos,
        form=form,
    )


def is_json_valid(json_string):
    """Check if the value is a valid JSON string"""
    try:
        json.loads(json_string)
    except json.decoder.JSONDecodeError as e:
        return False, e.msg
    return True, None


def flash_error(field, error_message):
    """Return a flash error"""
    flash(
        f"Failed to save {field}  :  {error_message} ",
        "danger",
    )


def is_custom_wvs_valid(custom_wvs):
    """Validate Custom WVS JSON object"""
    schema = {
        "type": "object",
        "patternProperties": {
            "^[a-zA-Z0-9_]+$": {
                "type": "object",
                "patternProperties": {"^[a-zA-Z0-9_]+$": {"type": "number"}},
                "additionalProperties": False,
            }
        },
        "additionalProperties": False,
    }
    try:
        validate(custom_wvs, schema=schema)
    except ValidationError as e:
        return False, e.message

    return True, None


def is_pairwise_triplewise_entities_valid(pairwise):
    """Check if pairwise triplewise entities JSON object is valid ."""
    schema = {
        "type": "object",
        "patternProperties": {r"^\(\w+(,\s\w+){1,2}\)$": {"type": "string"}},
        "additionalProperties": False,
    }

    try:
        validate(pairwise, schema=schema)
    except ValidationError as e:
        return False, e.message

    return True, None


def is_tag_guiding_typos_valid(tags):
    """Validate tag guiding typos JSON object is valid"""

    schema = {"type": "array", "items": {"type": "string"}}

    try:
        validate(tags, schema=schema)
    except ValidationError as e:
        return False, e.message

    return True, None


def validate_and_save_contextualization_config(form, old_config):
    """
    Check fields in the contextualization  form and save new config to DB.

    Parameters
    ----------
    form : AddLangCtxForm
        A WTForm. Defined in app/config_ui/form_models.py
    old_config: ContextualizationModel
        The old Contextualization config that is being replaced

    Returns
    -------
    Boolean
        True is record was created
        False if there was an error

    Notes
    -----
    It also flashes the result on the next page that is rendered
    """
    is_valid, error_message = is_json_valid(form.custom_wvs.data)
    if not is_valid:
        flash_error("Custom word mapping", error_message)
        return False

    is_valid, error_message = is_json_valid(form.pairwise_triplewise_entities.data)
    if not is_valid:
        flash_error("Pairwise entities", error_message)
        return False

    is_valid, error_message = is_json_valid(form.tag_guiding_typos.data)
    if not is_valid:
        flash_error("Tag guiding typos", error_message)
        return False

    custom_wvs = json.loads(form.custom_wvs.data)
    pairwise = json.loads(form.pairwise_triplewise_entities.data)
    tag_guiding_typos = json.loads(form.tag_guiding_typos.data)

    is_valid, error_message = is_custom_wvs_valid(custom_wvs)
    if not is_valid:
        flash_error("Custom word mapping", error_message)
        return False

    is_valid, error_message = is_pairwise_triplewise_entities_valid(pairwise)
    if not is_valid:
        flash_error("Pairwise entities", error_message)
        return False

    is_valid, error_message = is_tag_guiding_typos_valid(tag_guiding_typos)
    if not is_valid:
        flash_error("Tag guiding typos", error_message)
        return False

    version_id = secrets.token_hex(8)
    config_added_utc = datetime.utcnow()
    old_config.active = False
    new_config = ContextualizationModel(
        version_id=version_id,
        custom_wvs=custom_wvs,
        pairwise_triplewise_entities=pairwise,
        tag_guiding_typos=tag_guiding_typos,
        config_added_utc=config_added_utc,
        active=True,
    )
    db.session.add(new_config)
    db.session.commit()
    flash(
        "Successfully updated contextualization config to config "
        f"version: {str(version_id)}",
        "success",
    )
    return True
