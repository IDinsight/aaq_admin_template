import base64
import re
import json

import pytest
from sqlalchemy import text

from admin_webapp.app.config_ui import views


@pytest.fixture
def credentials_fullaccess():
    return base64.b64encode(b"fullaccess_user:testfullaccess123").decode("utf-8")


@pytest.fixture
def credentials_readonly():
    return base64.b64encode(b"readonly_user:testread123").decode("utf-8")


@pytest.fixture
def default_config(db_engine):
    with db_engine.connect() as db_connection:
        t = text("SELECT * FROM contextualization WHERE active=true")
        rs = db_connection.execute(t)
        return rs.mappings().one()


@pytest.fixture
def reset_config(db_engine, default_config):
    yield
    query = text("UPDATE contextualization SET active = false WHERE active = true")
    db_engine.execute(query)
    set_default_query = text(
        "UPDATE contextualization SET active = true WHERE contextualization_id = :config_id"
    )
    db_engine.execute(
        set_default_query, config_id=default_config["contextualization_id"]
    )
    db_engine.execute("DELETE FROM contextualization WHERE active = false")


class TestEditConfig:
    @pytest.mark.parametrize(
        "custom_wvs",
        [
            ({"5g": {"cellphone": 0.5, "radiation": "0.5"}}),
            ({"5g": {"cellphone": 0.5, "radiation": "0.5"}, 666: {"devil": 1}},),
            ({"666@": {"devil": 1}, "5g": {"cellphone": 0.5, "radiation": 0.5}}),
        ],
    )
    def test_edit_config_incorrect_custom_wvs(
        self, credentials_fullaccess, client, default_config, custom_wvs
    ):
        print(default_config)
        response = client.post(
            "/config/edit-contextualization",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": json.dumps(custom_wvs),
                "pairwise_triplewise_entities": json.dumps(
                    default_config["pairwise_triplewise_entities"]
                ),
                "tag_guiding_typos": json.dumps(default_config["tag_guiding_typos"]),
                "submit": "True",
            },
        )

        assert re.search(
            "Failed to save custom word mapping", response.get_data(as_text=True)
        )

    @pytest.mark.parametrize(
        "pairwise",
        [
            ({"c, section": "c_section", "(heart, burn)": "heart_burn"}),
            ({"(c, section)": "c_section", "(heart)": "heart_burn"}),
            ({"c, section": "c_section", "(heart, burn)": "heart_burn"}),
            ({"(c, section&)": "c_section", "(heart, burn)": "heart_burn"}),
        ],
    )
    def test_edit_config_incorrect_pairwise(
        self, credentials_fullaccess, client, default_config, pairwise
    ):
        response = client.post(
            "/config/edit-contextualization",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": json.dumps(default_config["custom_wvs"]),
                "pairwise_triplewise_entities": json.dumps(pairwise),
                "tag_guiding_typos": json.dumps(default_config["tag_guiding_typos"]),
                "submit": "True",
            },
        )

        assert re.search(
            "Failed to save Pairwise or triple-wise entities",
            response.get_data(as_text=True),
        )

    @pytest.mark.parametrize(
        "tags",
        [(["ingredients", 3, "labor", "miscarriage", "rash"]), ([1, 12, 23, 245])],
    )
    def test_edit_config_incorrect_tag_guiding_typos(
        self, credentials_fullaccess, client, default_config, tags
    ):
        response = client.post(
            "/config/edit-contextualization",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": json.dumps(default_config["custom_wvs"]),
                "pairwise_triplewise_entities": json.dumps(
                    default_config["pairwise_triplewise_entities"]
                ),
                "tag_guiding_typos": json.dumps(tags),
                "submit": "True",
            },
        )

        assert re.search(
            "Failed to save tag guiding typos",
            response.get_data(as_text=True),
        )

    def test_edit_config_correct_custom_wvs(
        self, credentials_fullaccess, client, default_config, reset_config
    ):
        custom_wvs = {
            "666": {"devil": 1},
            "5g": {"cellphone": 0.5, "radiation": 0.5},
            "jab": {"vaccine": 1},
            "cord": {"umbilical_cord": 1},
            "evds": {"database": 0.5, "vaccines": 0.5},
        }
        response = client.post(
            "/config/edit-contextualization",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": json.dumps(custom_wvs),
                "pairwise_triplewise_entities": json.dumps(
                    default_config["pairwise_triplewise_entities"]
                ),
                "tag_guiding_typos": json.dumps(default_config["tag_guiding_typos"]),
                "submit": "True",
            },
        )
        assert re.search(
            "Successfully updated contextualization config",
            response.get_data(as_text=True),
        )

    def test_edit_config_correct_pairwise(
        self, credentials_fullaccess, client, default_config, reset_config
    ):
        pairwise = {
            "(c, section)": "c_section",
            "(heart, burn)": "heart_burn",
            "(acid, reflux)": "acid_reflux",
            "(flu, vaccine)": "flu_vaccine",
            "(medical, aid)": "medical_aid",
            "(pain, killer)": "pain_killer",
            "(second, dose)": "second_dose",
            "(side, effect)": "side_effects",
            "(side, effects)": "side_effects",
        }
        response = client.post(
            "/config/edit-contextualization",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": json.dumps(default_config["custom_wvs"]),
                "pairwise_triplewise_entities": json.dumps(pairwise),
                "tag_guiding_typos": json.dumps(default_config["tag_guiding_typos"]),
                "submit": "True",
            },
        )
        assert re.search(
            "Successfully updated contextualization config",
            response.get_data(as_text=True),
        )

    def test_edit_config_correct_tag_guiding_typos(
        self, credentials_fullaccess, client, default_config, reset_config
    ):
        tags = [
            "bleed",
            "breast",
            "effects",
            "fever",
            "immunity",
            "ingredients",
            "jaundice",
            "labor",
            "miscarriage",
            "rash",
            "results",
        ]
        response = client.post(
            "/config/edit-contextualization",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": json.dumps(default_config["custom_wvs"]),
                "pairwise_triplewise_entities": json.dumps(
                    default_config["pairwise_triplewise_entities"]
                ),
                "tag_guiding_typos": json.dumps(tags),
                "submit": "True",
            },
        )
        assert re.search(
            "Successfully updated contextualization config",
            response.get_data(as_text=True),
        )
