import base64
import re

import pytest
from sqlalchemy import text


@pytest.fixture
def credentials_fullaccess():
    return base64.b64encode(b"fullaccess_user:testfullaccess123").decode("utf-8")


@pytest.fixture
def credentials_readonly():
    return base64.b64encode(b"readonly_user:testread123").decode("utf-8")


@pytest.fixture
def clean_ud_rules_table(db_engine):
    yield
    with db_engine.connect() as db_connection:
        t = text("DELETE FROM urgency_rules WHERE urgency_rule_author='pytest'")
        db_connection.execute(t)


@pytest.mark.ud_test
class TestCheckNewUDRules:
    def test_check_new_ud_rules_page_loads(self, client_ud):
        credentials = base64.b64encode(b"readonly_user:testread123").decode("utf-8")
        response = client_ud.get(
            "/ud/check-new-urgency-rules",
            follow_redirects=True,
            headers={"authorization": "basic " + credentials},
        )
        assert response.status_code == 200

    def test_check_new_ud_rules_page_fails(self, client):
        credentials = base64.b64encode(b"readonly_user:testread123").decode("utf-8")
        response = client.get(
            "/ud/check-new-urgency-rules",
            follow_redirects=True,
            headers={"authorization": "basic " + credentials},
        )
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "includes,excludes,query,result",
        [
            (["hello", "world"], [], "hello and goodbye cruel world", "Urgent"),
            (
                ["hello", "world"],
                ["test"],
                "this is a test world",
                "Not Urgent",
            ),
        ],
    )
    def test_check_new_ud_rule(
        self,
        includes,
        excludes,
        query,
        result,
        client_ud,
        credentials_fullaccess,
    ):
        data = {"query_1": query, "Submit": "True"}
        data.update(
            dict(zip([f"include_{i+1}" for i in range(len(includes))], includes))
        )
        data.update(
            dict(zip([f"exclude_{i+1}" for i in range(len(excludes))], excludes))
        )
        print(data)
        response = client_ud.post(
            "/ud/check-new-urgency-rules",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data=data,
        )

        assert re.search(f">{result}<", response.get_data(as_text=True))


@pytest.mark.ud_test
class TestAddUDRule:
    def test_add_page_fails_unauthorized(self, client_ud, credentials_readonly):
        response = client_ud.get(
            "/ud/ud-rules/add",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_readonly},
        )
        assert response.status_code == 403

    def test_add_page_loads_authorized(self, client_ud, credentials_fullaccess):
        response = client_ud.get(
            "/ud/ud-rules/add",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
        )
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "includes,excludes",
        [
            (["hello", "world"], []),
            (["hello", "world"], ["test"]),
            (["some"], ["other", "rules"]),
        ],
    )
    def test_add_new_ud_rule(
        self,
        includes,
        excludes,
        client_ud,
        credentials_fullaccess,
        clean_ud_rules_table,
    ):
        data = {
            "rule_author": "pytest",
            "rule_title": "test rule",
            "Submit": "True",
        }
        data.update(
            dict(zip([f"include_{i+1}" for i in range(len(includes))], includes))
        )
        data.update(
            dict(zip([f"exclude_{i+1}" for i in range(len(excludes))], excludes))
        )
        print(data)
        response = client_ud.post(
            "/ud/ud-rules/add",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data=data,
        )

        assert response.status_code == 200
        assert re.search(
            "Successfully added new rule with ID", response.get_data(as_text=True)
        )


@pytest.mark.ud_test
class TestEditUDRule:

    insert_ud = (
        "INSERT INTO urgency_rules ("
        "urgency_rule_id, urgency_rule_added_utc, urgency_rule_author, "
        "urgency_rule_title, urgency_rule_tags_include, urgency_rule_tags_exclude) "
        "VALUES (:ud_id, :added_utc, :author, :title, :includes, :excludes)"
    )
    includes = [
        """{"rock", "guitar"}""",
        """{"lake", "mountain", "sky"}""",
        """{"draw", "sing", "exercise", "code"}""",
    ]
    excludes = ["""{}""", """{"test"}""", """{"hello", "world"}"""]
    ud_other_params = {
        "added_utc": "2022-04-14",
        "author": "pytest",
    }

    @pytest.fixture(scope="class")
    def ud_rules_data(self, client, db_engine):
        with db_engine.connect() as db_connection:
            add_ud_sql = text(self.insert_ud)
            for i, (include, exclude) in enumerate(zip(self.includes, self.excludes)):
                db_connection.execute(
                    add_ud_sql,
                    ud_id=1000 + i,
                    title=f"Pytest title #{i}",
                    includes=include,
                    excludes=exclude,
                    **self.ud_other_params,
                )
        yield
        with db_engine.connect() as db_connection:
            t = text("DELETE FROM urgency_rules WHERE urgency_rule_author='pytest'")
            db_connection.execute(t)

    def test_edit_page_fails_unauthorized(
        self, ud_rules_data, client_ud, credentials_readonly
    ):
        response = client_ud.get(
            "/ud/ud-rules/edit/1000",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_readonly},
        )
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "ud_id,status",
        ([1000, 200], [1001, 200], [1002, 200], [9999, 404]),
    )
    def test_edit_page_loads_authorized(
        self, ud_id, status, ud_rules_data, client_ud, credentials_fullaccess
    ):
        response = client_ud.get(
            f"/ud/ud-rules/edit/{ud_id}",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
        )
        assert response.status_code == status

    # TODO: Need test cases for edit - add terms, delete terms, change terms


@pytest.mark.ud_test
class TestDeleteUDRule:

    insert_ud = (
        "INSERT INTO urgency_rules ("
        "urgency_rule_id, urgency_rule_added_utc, urgency_rule_author, "
        "urgency_rule_title, urgency_rule_tags_include, urgency_rule_tags_exclude) "
        "VALUES (:ud_id, :added_utc, :author, :title, :includes, :excludes)"
    )
    includes = [
        """{"rock", "guitar"}""",
        """{"lake", "mountain", "sky"}""",
        """{"draw", "sing", "exercise", "code"}""",
    ]
    excludes = ["""{}""", """{"test"}""", """{"hello", "world"}"""]
    ud_other_params = {
        "added_utc": "2022-04-14",
        "author": "pytest",
    }

    @pytest.fixture(scope="class")
    def ud_rules_data(self, client, db_engine):
        with db_engine.connect() as db_connection:
            add_ud_sql = text(self.insert_ud)
            for i, (include, exclude) in enumerate(zip(self.includes, self.excludes)):
                db_connection.execute(
                    add_ud_sql,
                    ud_id=1000 + i,
                    title=f"Pytest title #{i}",
                    includes=include,
                    excludes=exclude,
                    **self.ud_other_params,
                )
        yield
        with db_engine.connect() as db_connection:
            t = text("DELETE FROM urgency_rules WHERE urgency_rule_author='pytest'")
            db_connection.execute(t)

    def test_delete_page_fails_unauthorized(
        self, ud_rules_data, client_ud, credentials_readonly
    ):
        response = client_ud.get(
            "/ud/ud-rules/delete/1001",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_readonly},
        )
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "ud_id,status",
        ([1000, 200], [1001, 200], [1002, 200], [9999, 404]),
    )
    def test_delete_page_loads_authorized(
        self, ud_id, status, ud_rules_data, client_ud, credentials_fullaccess
    ):
        response = client_ud.get(
            f"/ud/ud-rules/delete/{ud_id}",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
        )
        assert response.status_code == status

    @pytest.mark.parametrize(
        "ud_id,status_code,message",
        [
            ("aabbcc", 404, "Invalid Urgency Rule ID: aabbcc"),
            ("1", 404, "No Urgency Rule with ID: 1"),
            ("1002", 200, "Successfully deleted Urgency Rule with ID: 1002"),
        ],
    )
    def test_delete_faq(
        self,
        ud_id,
        status_code,
        message,
        ud_rules_data,
        client_ud,
        credentials_fullaccess,
    ):
        response = client_ud.post(
            f"/ud/ud-rules/delete/{ud_id}",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
        )

        assert re.search(message, response.get_data(as_text=True))
        assert response.status_code == status_code
