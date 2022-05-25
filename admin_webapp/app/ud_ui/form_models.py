from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CheckRulesForm(FlaskForm):
    """Form for testing new keyword-based urgency rule"""

    include_1 = StringField(validators=[DataRequired()])
    include_2 = StringField()
    include_3 = StringField()
    include_4 = StringField()
    include_5 = StringField()
    include_6 = StringField()
    include_7 = StringField()
    include_8 = StringField()
    include_9 = StringField()
    include_10 = StringField()

    exclude_1 = StringField()
    exclude_2 = StringField()
    exclude_3 = StringField()
    exclude_4 = StringField()
    exclude_5 = StringField()
    exclude_6 = StringField()
    exclude_7 = StringField()
    exclude_8 = StringField()
    exclude_9 = StringField()
    exclude_10 = StringField()

    query_1 = StringField(label="", validators=[DataRequired()])
    query_2 = StringField(label="", validators=[])
    query_3 = StringField(label="", validators=[])
    query_4 = StringField(label="", validators=[])
    query_5 = StringField(label="", validators=[])

    submit = SubmitField("Submit")
    add_rule = SubmitField("Add This Rule")


class AddRuleForm(FlaskForm):
    """Form for Urgency Rule (for adding or editing)"""

    rule_author = StringField("Author of rule:", validators=[DataRequired()])
    rule_title = StringField(
        "Title of rule:",
        validators=[DataRequired()],
    )

    include_1 = StringField(validators=[DataRequired()])
    include_2 = StringField()
    include_3 = StringField()
    include_4 = StringField()
    include_5 = StringField()
    include_6 = StringField()
    include_7 = StringField()
    include_8 = StringField()
    include_9 = StringField()
    include_10 = StringField()

    exclude_1 = StringField()
    exclude_2 = StringField()
    exclude_3 = StringField()
    exclude_4 = StringField()
    exclude_5 = StringField()
    exclude_6 = StringField()
    exclude_7 = StringField()
    exclude_8 = StringField()
    exclude_9 = StringField()
    exclude_10 = StringField()

    submit = SubmitField("Save")
