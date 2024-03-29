from sqlalchemy.dialects.postgresql import JSONB

from .database_sqlalchemy import db


class FAQModel(db.Model):
    """
    SQLAlchemy data model for FAQ
    """

    __tablename__ = "faqmatches"

    faq_id = db.Column(db.Integer, primary_key=True)
    faq_added_utc = db.Column(db.DateTime())
    faq_updated_utc = db.Column(db.DateTime())
    faq_author = db.Column(db.String())
    faq_title = db.Column(db.String())
    faq_content_to_send = db.Column(db.String())
    faq_tags = db.Column(db.ARRAY(db.String()))
    faq_questions = db.Column(db.ARRAY(db.String()), nullable=False)
    faq_contexts = db.Column(db.ARRAY(db.String()))
    faq_thresholds = db.Column(db.ARRAY(db.Float()))
    faq_weight = db.Column(db.Integer())

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


class ContextualizationModel(db.Model):
    """
    SQLAlchemy data model for contextualization configurations
    """

    __tablename__ = "contextualization"
    contextualization_id = db.Column(db.Integer, primary_key=True, nullable=False)
    version_id = db.Column(db.String(), nullable=False)
    config_added_utc = db.Column(db.DateTime(), nullable=False)
    config_updated_utc = db.Column(db.DateTime())
    custom_wvs = db.Column(JSONB, nullable=False)
    pairwise_triplewise_entities = db.Column(JSONB, nullable=False)
    tag_guiding_typos = db.Column(JSONB, nullable=False)
    active = db.Column(db.Boolean, default=1)
