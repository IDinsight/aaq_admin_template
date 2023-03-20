<<<<<<< HEAD
from datetime import datetime
import json
import secrets
from flask import (
    flash,
    redirect,
    render_template,
    url_for,
)
=======
from flask import render_template
>>>>>>> fe7bca902291b4b55c1331f17977e5cb903f0c6e

from ..auth import auth
from ..data_models import ContextualizationModel
from ..database_sqlalchemy import db
from . import config_ui
<<<<<<< HEAD
from .form_models import AddContextualizationForm
=======
from .form_models import AddLangCtxForm
>>>>>>> fe7bca902291b4b55c1331f17977e5cb903f0c6e

##############################################################################
# Contextualization management endpoints
##############################################################################


@config_ui.route("/edit-contextualization", methods=["GET", "POST"])
@auth.login_required(role="add")
<<<<<<< HEAD
def edit_contextualization_config():
    """
    Handles form and POST to edit contextualization config
=======
def edit_lang_ctx_config():
    """
    Handles form and POST to add an FAQ
>>>>>>> fe7bca902291b4b55c1331f17977e5cb903f0c6e
    """
    contextualization = (
        db.session.query(ContextualizationModel)
        .filter(ContextualizationModel.active == True)
        .first()
    )
<<<<<<< HEAD
    form = AddContextualizationForm(obj=contextualization)
    if form.is_submitted():
        if validate_and_save_contextualization_config(form, contextualization):
            return redirect(url_for("main.home"))

    return render_template(
        "edit_contextualization.html",
=======
    form = AddLangCtxForm(obj=contextualization)

    return render_template(
        "edit_lang_ctx.html",
>>>>>>> fe7bca902291b4b55c1331f17977e5cb903f0c6e
        version_id=contextualization.version_id,
        custom_wvs=contextualization.custom_wvs,
        pairwise_triplewise_entities=contextualization.pairwise_triplewise_entities,
        tag_guiding_typos=contextualization.tag_guiding_typos,
        form=form,
    )
<<<<<<< HEAD


def is_custom_wvs_value_valid(value_dic):
    """Check if custom wvs fields are valid """
    all_values_float = all([isinstance(value, float) or isinstance(value,int) for value in value_dic.values()])
    all_keys_str = all([isinstance(value, str) for value in value_dic.keys()])

    if all_values_float and all_keys_str and sum(value_dic.values()) == 1:
        return True
   
    return False


def validate_custom_wvs(custom_wvs):
    """Validate Custom WVS JSON object"""

    custom_wvs = json.loads(custom_wvs)
    invalid_fields = [value for value in custom_wvs.values() if type(value) is not dict]
    invalid_fields += [value for value in custom_wvs.values() if not is_custom_wvs_value_valid(value)]
    invalid_fields = [dict(t) for t in {tuple(d.items()) for d in invalid_fields}]
    return invalid_fields, custom_wvs


def is_valid_pairwise_key(key):
    """"Check if key  is the string representation of a tuple with 2 values """
    entities = []
    try:
        entities = key.strip("()").split(",")
    except ValueError as e:
        return False
    if len(entities) <= 3:
        return True
    return False


def validate_pairwise_triplewise_entities(pairwise):
    """Check if pairwise triplewise entities JSON object is valid . """
    pairwise = json.loads(pairwise)
    invalid_keys = [
        value for value in pairwise.keys() if not is_valid_pairwise_key(value)
    ]
    invalid_values = [
        pairwise[value] for value in pairwise.values() if not isinstance(value, str)
    ]
    return invalid_keys, invalid_values, pairwise


def validate_tag_guiding_typos(tags):
    """" Validate tag guiding typos JSON object is valid  """

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
=======
>>>>>>> fe7bca902291b4b55c1331f17977e5cb903f0c6e
