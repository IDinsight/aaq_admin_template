from .database_sqlalchemy import db


class FAQModel(db.Model):
    """
    SQLAlchemy data model for FAQ
    """

    __tablename__ = "faqmatches"

    faq_id = db.Column(db.Integer, primary_key=True)
    faq_added_utc = db.Column(db.DateTime())
    faq_author = db.Column(db.String())
    faq_title = db.Column(db.String())
    faq_content_to_send = db.Column(db.String())
    faq_tags = db.Column(db.ARRAY(db.String()))
    faq_thresholds = db.Column(db.ARRAY(db.Float()))

    def __repr__(self):
        """Print FAQ id"""
        return "<FAQ %r>" % self.id


class RulesModel(db.Model):
    """
    SQLAlchemy data model for rules
    """

    __tablename__ = "urgency_rules"

    urgency_rule_id = db.Column(db.Integer, primary_key=True)
    urgency_rule_added_utc = db.Column(db.DateTime())
    urgency_rule_author = db.Column(db.String())
    urgency_rule_title = db.Column(db.String())
    urgency_rule_tags_include = db.Column(db.ARRAY(db.String()))
    urgency_rule_tags_exclude = db.Column(db.ARRAY(db.String()))
