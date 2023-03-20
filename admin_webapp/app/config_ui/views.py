from jsonschema import validate
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
from .form_models import AddLangCtxForm

##############################################################################
# Contextualization management endpoints
##############################################################################


@config_ui.route("/edit-contextualization", methods=["GET", "POST"])
@auth.login_required(role="add")
def edit_lang_ctx_config():
    """
    Handles form and POST to add an FAQ
    """
    contextualization = (
        db.session.query(ContextualizationModel)
        .filter(ContextualizationModel.active == True)
        .first()
    )

    form = AddLangCtxForm(obj=contextualization)
    if form.is_submitted():
        if validate_and_save_contextualization_config(form, contextualization):
            return redirect(url_for("main.home"))

    return render_template(
        "edit_lang_ctx.html",
        version_id=contextualization.version_id,
        custom_wvs=contextualization.custom_wvs,
        pairwise_triplewise_entities=contextualization.pairwise_triplewise_entities,
        tag_guiding_typos=contextualization.tag_guiding_typos,
        form=form,
    )


def validate_custom_wvs(custom_wvs):
    """Validate Custom WVS JSON object"""
    schema = {
        "type": "object",
        "patternProperties": {
            "^[a-zA-Z0-9_]+$": {
                "type": "object",
                "patternProperties":{
                    "^[a-zA-Z0-9_]+$":{
                    "type":"number"
                        
                    }
                },
                "additionalProperties": False

            }
            },
            "additionalProperties": False
        }   
    custom_wvs = json.loads(custom_wvs)
    try:
        validate(custom_wvs, schema = schema)
    except Exception as e:
        flash(f" Failed to save custom word mapping :  {e.message}","danger")
        return False

    return custom_wvs


def validate_pairwise_triplewise_entities(pairwise):
    """Check if pairwise triplewise entities JSON object is valid . """
    schema = schema = {
        "type": "object",
        "patternProperties": {
            "^\(\w+(,\s\w+){1,2}\)$": {
                "type": "string",
                
            }
        },
        "additionalProperties": False
    }   
    pairwise = json.loads(pairwise)
    try:
        validate(pairwise, schema = schema)
    except Exception as e:
        flash(f" Failed to save Pairwise or triple-wise entities :  {e.message} ", "danger")
        return False

    return pairwise
def validate_tag_guiding_typos(tags):
    """" Validate tag guiding typos JSON object is valid  """

    schema = {
        "type": "array",
        "items": {"type": "string"},
        }
    tags = json.loads(tags)

    try:
        validate(tags, schema = schema)
    except Exception as e:
        flash(f" Failed to save tag guiding typos :  {e.message}", "danger")
        return False

    return tags
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
    custom_wvs = validate_custom_wvs(form.custom_wvs.data)  
    
    pairwise = validate_pairwise_triplewise_entities(
        form.pairwise_triplewise_entities.data
    )

    tag_guiding_typos = validate_tag_guiding_typos(form.tag_guiding_typos.data)

    if not custom_wvs or not pairwise or not tag_guiding_typos:
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
    flash(f"Successfully updated contextualization config to config version: {str(version_id)}","success")
    return True