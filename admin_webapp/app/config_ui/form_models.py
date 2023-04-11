from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class AddLanguageContextForm(FlaskForm):
    """Class for adding a contextualization form to template"""

    pairwise_triplewise_entities = StringField(
        label="Pairwise or triple-wise entities",
        description="To treat two to three words as a single expression.",
        validators=[DataRequired()],
        widget=TextArea(),
    )
    custom_wvs = StringField(
        label="Custom word mapping",
        description="""To allow mapping a context-specific word to a (combination of)
                    more commonly understood word(s).
        If mapping to multiple words, ensure the weights add up to 1.""",
        validators=[DataRequired()],
        widget=TextArea(),
    )
    tag_guiding_typos = StringField(
        label="Spell guides",
        description="When running spell-correction, the following words will be chosen before any other spell correction candidates.",
        validators=[DataRequired()],
        widget=TextArea(),
    )
    submit = SubmitField("Save")
