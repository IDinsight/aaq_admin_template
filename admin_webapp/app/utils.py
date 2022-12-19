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


def check_new_id_match(title, titles_dic, title_id):
    """

    Check if the title exists in the dictionary of titles .

    Parameters
    ----------
    title : title
    titles: List[String]
        Dictionary with titles as key and ids as value.
    title_id: int
        Id linked to the title

    Returns
    -------
    Boolean
        True if there was a duplicate
        False if there is no duplicates
    """

    matching_id = titles_dic.get(title)
    if matching_id != title_id:
        return True
    else:
        return False
