from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange
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
    faq_weight = IntegerField(
        "FAQ Weight",
        validators=[
            DataRequired(),
            NumberRange(min=1, message="Weight must be at least 1"),
        ],
        default=1,
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

    question_1 = StringField(validators=[DataRequired()])
    question_2 = StringField(validators=[DataRequired()])
    question_3 = StringField(validators=[DataRequired()])
    question_4 = StringField(validators=[DataRequired()])
    question_5 = StringField(validators=[DataRequired()])
    question_6 = StringField()
    question_7 = StringField()
    question_8 = StringField()
    question_9 = StringField()
    question_10 = StringField()

    context_1 = StringField()
    context_2 = StringField()
    context_3 = StringField()
    context_4 = StringField()
    context_5 = StringField()
    context_6 = StringField()
    context_7 = StringField()
    context_8 = StringField()
    context_9 = StringField()
    context_10 = StringField()

    submit = SubmitField("Save")
