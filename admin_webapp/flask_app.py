"""
Main python script called by gunicorn
"""
from app import create_app, db
from app.data_models import RulesModel

app = create_app(enable_ud=False)


@app.shell_context_processor
def make_shell_context():
    """
    Return flask shell with objects imported
    """
    return dict(db=db, RulesModel=RulesModel)
