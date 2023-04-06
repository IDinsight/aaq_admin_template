import base64
import re
import json

import pytest
from sqlalchemy import text


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
        # return {key: json.dumps(value) for (key, value) in default_dict.items()}
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
        "custom_wvs,outcome",
        [
            ("""{"5g": {"cellphone": 0.5, "radiation": "0.5"}}""", "error"),
            ("""{"5g": {"cellphone": 0.5, "radiation": 0.5}}}""", "error"),
            (
                """{666: {"devil": 1}}""",
                "error",
            ),
            (
                """{"5g": {"cellphone": 0.5, "radiation": 0.5}, " ": {"devil": 1}}""",
                "error",
            ),
            (
                """{"666@": {"devil": 1}}""",
                "error",
            ),
            (
                """{"jab": {"vaccine": 1}, "5g": {"cellphone": 0.5, "radiation": 0.5}}""",
                "valid",
            ),
        ],
    )
    def test_edit_custom_wvs_config(
        self, credentials_fullaccess, client, default_config, custom_wvs, outcome
    ):

        response = client.post(
            "/config//edit-language-context",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": custom_wvs,
                "pairwise_triplewise_entities": json.dumps(
                    default_config["pairwise_triplewise_entities"]
                ),
                "tag_guiding_typos": json.dumps(default_config["tag_guiding_typos"]),
                "submit": "True",
            },
        )
        if outcome == "error":
            assert re.search(
                "Failed to save Custom word mapping", response.get_data(as_text=True)
            )
        else:
            assert re.search(
                "Successfully updated contextualization config",
                response.get_data(as_text=True),
            )

    @pytest.mark.parametrize(
        "pairwise,outcome",
        [
            ("""{"c, section": "c_section"}""", "error"),
            ("""{"(heart)": "heart_burn"}""", "error"),
            (
                """{"(c, section)": "c_section",, "(heart, burn)": "heart_burn"}""",
                "error",
            ),
            (
                """{"(c, section&)": "c_section"}""",
                "error",
            ),
            (
                """{"(c, section)": "c_section"," ": "heart_burn"}""",
                "error",
            ),
            (
                """{"(medical, aid)": "medical_aid","(pain, killer)": "pain_killer"}""",
                "valid",
            ),
        ],
    )
    def test_edit_pairwise_config(
        self, credentials_fullaccess, client, default_config, pairwise, outcome
    ):
        response = client.post(
            "/config/edit-language-context",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": json.dumps(default_config["custom_wvs"]),
                "pairwise_triplewise_entities": pairwise,
                "tag_guiding_typos": json.dumps(default_config["tag_guiding_typos"]),
                "submit": "True",
            },
        )

        if outcome == "error":
            assert re.search(
                "Failed to save Pairwise entities",
                response.get_data(as_text=True),
            )
        else:
            assert re.search(
                "Successfully updated contextualization config",
                response.get_data(as_text=True),
            )

    @pytest.mark.parametrize(
        "tags,outcome",
        [
            (
                """[{"ingredients", "effects", "labor", "miscarriage",, "rash"]""",
                "error",
            ),
            ("""["ingredients", 3, "labor", "miscarriage", "rash"]""", "error"),
            ("""[1, 12, 23, 245]""", "error"),
            ("""{"ingredients", "effects", "labor", "miscarriage", "rash"}""", "error"),
            ("""["bleed", "breast", "effects"]""", "valid"),
        ],
    )
    def test_edit_tag_guiding_typos_config(
        self, credentials_fullaccess, client, default_config, tags, outcome
    ):
        response = client.post(
            "/config/edit-language-context",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": json.dumps(default_config["custom_wvs"]),
                "pairwise_triplewise_entities": json.dumps(
                    default_config["pairwise_triplewise_entities"]
                ),
                "tag_guiding_typos": tags,
                "submit": "True",
            },
        )
        if outcome == "error":
            assert re.search(
                "Failed to save Tag guiding typos",
                response.get_data(as_text=True),
            )
        else:
            assert re.search(
                "Successfully updated contextualization config",
                response.get_data(as_text=True),
            )
