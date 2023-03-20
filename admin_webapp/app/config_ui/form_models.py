from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class AddLangCtxForm(FlaskForm):
    """Class for adding a contextualization form to template"""

    pairwise_triplewise_entities = StringField(
        "Pairwise triplewise entities JSON data",
        validators=[DataRequired()],
        widget=TextArea(),
    )
    custom_wvs = StringField(
        "Custom WVS JSON data",
        validators=[DataRequired()],
        widget=TextArea(),
    )
    tag_guiding_typos = StringField(
        "Tag guiding typos JSON data",
        validators=[DataRequired()],
        widget=TextArea(),
    )
    submit = SubmitField("Save")
