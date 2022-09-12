import os
from functools import lru_cache

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

auth = HTTPBasicAuth()


@lru_cache
def get_users_and_hashed_password(readonly_password, fullaccess_password):
    """
    Gets hashed password for users
    """
    users = {
        "readonly_user": generate_password_hash(readonly_password),
        "fullaccess_user": generate_password_hash(fullaccess_password),
    }
    return users


@auth.verify_password
def verify_password(username, password):
    """Compare username and password against details above"""
    users = get_users_and_hashed_password(
        os.getenv("READONLY_PASSWORD"), os.getenv("FULLACCESS_PASSWORD")
    )

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
