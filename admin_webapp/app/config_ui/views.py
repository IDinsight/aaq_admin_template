from datetime import datetime
import json
import secrets
from flask import (
    flash,
    redirect,
    render_template,
    url_for,
)

from ..auth import auth
from ..data_models import ContextualizationModel
from ..database_sqlalchemy import db
from . import config_ui
from .form_models import AddContextualizationForm

##############################################################################
# Contextualization management endpoints
##############################################################################


@config_ui.route("/edit-contextualization", methods=["GET", "POST"])
@auth.login_required(role="add")
def edit_contextualization_config():
    """
    Handles form and POST to edit contextualization config
    """
    contextualization = (
        db.session.query(ContextualizationModel)
        .filter(ContextualizationModel.active == True)
        .first()
    )
    form = AddContextualizationForm(obj=contextualization)
    if form.is_submitted():
        if validate_and_save_contextualization_config(form, contextualization):
            return redirect(url_for("main.home"))

    return render_template(
        "edit_contextualization.html",
        version_id=contextualization.version_id,
        custom_wvs=contextualization.custom_wvs,
        pairwise_triplewise_entities=contextualization.pairwise_triplewise_entities,
        tag_guiding_typos=contextualization.tag_guiding_typos,
        form=form,
    )


def is_json(myjson):
    "Check if string is a valid JSON object"
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


def validate_custom_wvs(custom_wvs):
    """Validate Custom WVS JSON object"""
    assert is_json(custom_wvs)
    custom_wvs = json.loads(custom_wvs)
    invalid_fields = [value for value in custom_wvs.values() if type(value) is not dict]
    return invalid_fields, custom_wvs


def is_valid_pairwise_key(key):
    """"Check if key  is the string representation of a tuple with 2 values """
    entities = []
    try:
        entities = key.strip("()").split(",")
    except ValueError as e:
        return False
    if len(entities) == 2:
        return True
    return False


def validate_pairwise_triplewise_entities(pairwise):
    """Check if pairwise triplewise entities JSON object is valid . """
    assert is_json(pairwise)
    pairwise = json.loads(pairwise)
    invalid_keys = [
        value for value in pairwise.keys() if not is_valid_pairwise_key(value)
    ]
    invalid_values = [
        pairwise[value] for value in pairwise.values() if not isinstance(value, str)
    ]
    return invalid_keys, invalid_values, pairwise


def validate_tag_guiding_typos(tags):
    """"Validate tag guiding typos JSON object is valid  """
    assert is_json(tags)
    tags = json.loads(tags)

    invalid = [value for value in tags if not isinstance(value, str)]

    return invalid, tags


def validate_and_save_contextualization_config(form, old_config):
    """
    Check fields in the contextualization  form and save new config to DB. 

    Parameters
    ----------
    form : AddContextualizationForm
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
    invalid_custom_wvs, custom_wvs = validate_custom_wvs(form.custom_wvs.data)
    if len(invalid_custom_wvs) > 0:
        flash(
            "The following custom wvs fields  are invalid: %s.\nPlease correct and resubmit."
            % str(invalid_custom_wvs),
            "danger",
        )
        return False
    invalid_keys, invalid_values, pairwise = validate_pairwise_triplewise_entities(
        form.pairwise_triplewise_entities.data
    )

    if len(invalid_keys) > 0:
        flash(
            "The following pairwise keys   are invalid: %s.\nPlease correct and resubmit."
            % str(invalid_keys),
            "danger",
        )
        return False
    if len(invalid_values) > 0:
        flash(
            "The following pairwise values   are invalid: %s.\nPlease correct and resubmit."
            % str(invalid_values),
            "danger",
        )
        return False
    invalid_tag_guiding_typos, tag_guiding_typos = validate_tag_guiding_typos(
        form.tag_guiding_typos.data
    )
    if len(invalid_tag_guiding_typos) > 0:
        flash(
            "The following tag guiding typos are invalid: %s.\nPlease correct and resubmit."
            % str(invalid_tag_guiding_typos),
            "danger",
        )
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
    flash(f"Successfully updated contextualization config to config version:{str(version_id)}")
    return True
