import os

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

auth = HTTPBasicAuth()

users = {
    "readonly_user": generate_password_hash(os.getenv("READONLY_PASSWORD")),
    "fullaccess_user": generate_password_hash(os.getenv("FULLACCESS_PASSWORD")),
}


@auth.verify_password
def verify_password(username, password):
    """Compare username and password against details above"""
    if username in users and check_password_hash(users.get(username), password):
        return username


@auth.get_user_roles
def get_user_roles(user):
    """Return roles for users"""
    if user == "readonly_user":
        return ["read"]
    elif user == "fullaccess_user":
        return ["read", "add"]
    else:
        return None
