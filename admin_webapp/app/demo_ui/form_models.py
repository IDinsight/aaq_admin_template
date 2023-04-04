from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class APICallDemoForm(FlaskForm):
    """Demo API call form"""

    submission_content = StringField(
        "Sample message:",
        validators=[DataRequired()],
        widget=TextArea(),
    )

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

    submit = SubmitField("Submit")


class CheckTagsForm(FlaskForm):
    """Form for /demo/check-new-faq-tags page"""

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

    query_1 = StringField(label="", validators=[DataRequired()])
    query_2 = StringField(label="", validators=[DataRequired()])
    query_3 = StringField(label="", validators=[DataRequired()])
    query_4 = StringField(label="", validators=[DataRequired()])
    query_5 = StringField(label="", validators=[DataRequired()])

    submit = SubmitField("Submit")
