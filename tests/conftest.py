from pathlib import Path

import pytest
import sqlalchemy
import yaml

from admin_webapp.app import create_app, get_config_data


@pytest.fixture(scope="session")
def monkeysession(request):
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def test_params(monkeysession):
    with open(Path(__file__).parent / "config.yaml", "r") as stream:
        params_dict = yaml.safe_load(stream)

    monkeysession.setenv("READONLY_PASSWORD", params_dict["READONLY_PASSWORD"])
    monkeysession.setenv("FULLACCESS_PASSWORD", params_dict["FULLACCESS_PASSWORD"])

    return params_dict


@pytest.fixture(scope="session")
def app(test_params, monkeysession):
    app = create_app(test_params)
    yield app


@pytest.fixture(scope="session")
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def app_ud(test_params):
    app = create_app(test_params, enable_ud=True)
    yield app


@pytest.fixture(scope="session")
def client_ud(app_ud):
    with app_ud.test_client() as client:
        yield client


@pytest.fixture(scope="class")
def db_engine(test_params):
    config = get_config_data(test_params)
    uri = config["SQLALCHEMY_DATABASE_URI"]
    engine = sqlalchemy.create_engine(uri)
    yield engine
