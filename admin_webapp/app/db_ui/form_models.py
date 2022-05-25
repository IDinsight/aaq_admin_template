from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class AddFAQForm(FlaskForm):
    """Class for adding a form to template"""

    faq_author = StringField("Author of FAQ:", validators=[DataRequired()])
    faq_title = StringField(
        "Title of FAQ (to display in initial list of 3):",
        validators=[DataRequired()],
    )
    faq_content_to_send = StringField(
        "Content of FAQ (to send upon user selection):",
        validators=[DataRequired()],
        widget=TextArea(),
    )
    tag_1 = StringField(validators=[DataRequired()])
    tag_2 = StringField(validators=[DataRequired()])
    tag_3 = StringField()
    tag_4 = StringField()
    tag_5 = StringField()
    tag_6 = StringField()
    tag_7 = StringField()
    tag_8 = StringField()
    tag_9 = StringField()
    tag_10 = StringField()

    submit = SubmitField("Save")
