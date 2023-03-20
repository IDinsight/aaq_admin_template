from flask import render_template

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

    return render_template(
        "edit_lang_ctx.html",
        version_id=contextualization.version_id,
        custom_wvs=contextualization.custom_wvs,
        pairwise_triplewise_entities=contextualization.pairwise_triplewise_entities,
        tag_guiding_typos=contextualization.tag_guiding_typos,
        form=form,
    )
