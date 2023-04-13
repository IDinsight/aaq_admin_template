import base64
import re
import json

import pytest
from sqlalchemy import text


@pytest.fixture
def credentials_fullaccess():
    return base64.b64encode(b"fullaccess_user:testfullaccess123").decode("utf-8")


class TestEditConfig:
    insert_query = (
        "INSERT INTO aaq.contextualization("
        "version_id,config_added_utc,custom_wvs,"
        "pairwise_triplewise_entities, tag_guiding_typos, active)"
        "VALUES (:version_id, :date_added,:custom_wvs, :pairwise, :tags, :active);"
    )

    config_params = {
        "custom_wvs": """{"shots": {"vaccines": 1},"deliver": {"birth": 1}}""",
        "pairwise": """{"(flu, vaccine)": "flu_vaccine","(medical, aid)": "medical_aid"}""",
        "tags": """["side","sneeze","teeth","test", "vaccine"]""",
    }

    @pytest.fixture(scope="class")
    def add_default_config(self, db_engine):
        with db_engine.connect() as db_connection:
            inbound_sql = text(self.insert_query)
            db_connection.execute(
                inbound_sql,
                date_added=datetime.now(),
                version_id=secrets.token_hex(8),
                active=True,
                **self.config_params,
            )
        yield
        with db_engine.connect() as db_connection:
            db_connection.execute("DELETE FROM contextualization")

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
        self, credentials_fullaccess, client, custom_wvs, outcome
    ):
        response = client.post(
            "/config/edit-language-context",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": custom_wvs,
                "pairwise_triplewise_entities": self.config_params["pairwise"],
                "tag_guiding_typos": self.config_params["tags"],
                "submit": "True",
            },
        )
        if outcome == "error":
            assert re.search(
                "Failed to save Custom word mapping", response.get_data(as_text=True)
            )
        else:
            assert re.search(
                "Successfully updated language context to version:",
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
        self, credentials_fullaccess, client, pairwise, outcome
    ):
        response = client.post(
            "/config/edit-language-context",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": self.config_params["custom_wvs"],
                "pairwise_triplewise_entities": pairwise,
                "tag_guiding_typos": self.config_params["tags"],
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
                "Successfully updated language context to version:",
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
        self, credentials_fullaccess, client, tags, outcome
    ):
        response = client.post(
            "/config/edit-language-context",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "custom_wvs": self.config_params["custom_wvs"],
                "pairwise_triplewise_entities": self.config_params["pairwise"],
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
                "Successfully updated language context to version:",
                response.get_data(as_text=True),
            )
