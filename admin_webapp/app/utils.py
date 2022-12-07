"""
General utility functions
"""
import os
from collections import UserDict
from pathlib import Path

import yaml


def load_yaml_config(filename, config_subfolder=None):
    """
    Load generic yaml files from config and return dictionary
    """
    if config_subfolder:
        full_path = Path(__file__).parents[1] / "config/{}/{}".format(
            config_subfolder, filename
        )
    else:
        full_path = Path(__file__).parents[1] / "config/{}".format(filename)

    with open(full_path) as file:
        yaml_dict = yaml.full_load(file)

    return yaml_dict


def load_parameters(key=None):
    """
    Load parameters
    """
    params = load_yaml_config("parameters.yml")

    if key is not None:
        params = params[key]

    return params


def get_postgres_uri(
    endpoint,
    port,
    database,
    username,
    password,
):
    """
    Returns PostgreSQL database URI given info and secrets
    """

    connection_uri = "postgresql://%s:%s@%s:%s/%s" % (
        username,
        password,
        endpoint,
        port,
        database,
    )

    return connection_uri


class DefaultEnvDict(UserDict):
    """
    Dictionary but uses env variables as defaults
    """

    def __missing__(self, key):
        """
        If `key` is missing, look for env variable with the same name.
        """

        value = os.getenv(key)
        if value is None:
            raise KeyError(f"{key} not found in dict or environment variables")
        return os.getenv(key)


def check_id_match(title, titles, ids, _id):
    """

    Check if the new title is already in the titles saved in Database.

    Parameters
    ----------
    title : title of the new or modified rule/faq
    titles: List[String]
        List of titles in the database.
    ids: List[int]
        List of Ids in the database
    ids: {int,None}
        Id of the modified faq/rule in the database

    Returns
    -------
    Boolean
        True if there was a duplicate
        False if there is no duplicates
    """
    match = None
    for title_pair in zip(titles, ids):
        if title == title_pair[0]:
            match = title_pair[1]
            break
    if match not in [None, _id]:
        return True
    return False
