import base64
import re

import pytest
from sqlalchemy import text

from admin_webapp.app.faq_ui import views


@pytest.fixture
def credentials_fullaccess():
    return base64.b64encode(b"fullaccess_user:testfullaccess123").decode("utf-8")


@pytest.fixture
def credentials_readonly():
    return base64.b64encode(b"readonly_user:testread123").decode("utf-8")


@pytest.fixture
def clean_faq_table(db_engine):
    yield
    with db_engine.connect() as db_connection:
        t = text("DELETE FROM faqmatches WHERE faq_author='pytest'")
        db_connection.execute(t)


@pytest.mark.parametrize("endpoint", ["/", "/faqs", "/faqs/view"])
def test_view_page_loads(endpoint, client, credentials_readonly):
    response = client.get(
        endpoint,
        follow_redirects=True,
        headers={"Authorization": "Basic " + credentials_readonly},
    )

    assert response.status_code == 200


def my_validate_tags(tag_list):
    VALIDWORDS = ["hello", "world", "weight", "test"]
    return [x for x in tag_list if x not in VALIDWORDS]


class TestAddFAQ:
    insert_faq = (
        "INSERT INTO faqmatches ("
        "faq_id, faq_tags, faq_questions,faq_author, faq_title, faq_content_to_send, "
        "faq_weight, faq_added_utc, faq_thresholds) "
        "VALUES (:faq_id, :faq_tags,:faq_questions, :author, :title, :content, :weight, "
        ":added_utc, :threshold)"
    )
    faq_other_params = {
        "faq_tags": """{"rock", "guitar", "melody", "chord"}""",
        "author": "pytest",
        "faq_questions": """{"This is question 1 ", "This is question 2", "This is question 3", "This is question 4","This is question 1"}""",
        "added_utc": "2022-04-14",
        "content": "{}",
        "weight": 2,
        "threshold": "{0.1, 0.1, 0.1, 0.1}",
    }

    @pytest.fixture(scope="class")
    def add_faq_data(self, client, db_engine):
        with db_engine.connect() as db_connection:
            inbound_sql = text(self.insert_faq)

            db_connection.execute(
                inbound_sql,
                faq_id=1001,
                title=f"Pytest title #1",
                **self.faq_other_params,
            )
        yield
        with db_engine.connect() as db_connection:
            t = text("DELETE FROM faqmatches " "WHERE faq_author='pytest'")
            db_connection.execute(t)

    def test_add_page_fails_unauthorized(self, client, credentials_readonly):
        response = client.get(
            "/faqs/add",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_readonly},
        )
        assert response.status_code == 403

    def test_add_page_loads_authorized(self, client, credentials_fullaccess):
        response = client.get(
            "/faqs/add",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
        )
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "tag1,tag2,outcome",
        [("hello", "world", "success"), ("madeupword", "world", "invalid")],
    )
    def test_add_new_faq(
        self,
        tag1,
        tag2,
        outcome,
        client,
        credentials_fullaccess,
        clean_faq_table,
        monkeypatch,
    ):
        monkeypatch.setattr(views, "validate_tags", my_validate_tags)
        response = client.post(
            "/faqs/add",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "tag_1": tag1,
                "tag_2": tag2,
                "faq_author": "pytest",
                "faq_title": "test_title",
                "faq_weight": 1,
                "faq_content_to_send": "Test Content Data",
                "question_1": "This is question 1",
                "question_2": "This is question 2",
                "question_3": "This is question 3",
                "question_4": "This is question 4",
                "question_5": "This is question 5",
                "submit": "True",
            },
        )

        if outcome == "success":
            assert re.search(
                "Successfully added new FAQ", response.get_data(as_text=True)
            )
        if outcome == "invalid":
            assert re.search(
                "The following tags are invalid:", response.get_data(as_text=True)
            )

    @pytest.mark.parametrize(
        "title,outcome",
        [
            ("Pytest title #1", "invalid"),
            ("Pytest title #2", "success"),
        ],
    )
    def test_add_new_faq_incorrect_title(
        self,
        title,
        outcome,
        client,
        add_faq_data,
        credentials_fullaccess,
    ):
        response = client.post(
            "/faqs/add",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "tag_1": "Hello",
                "tag_2": "World",
                "faq_author": "pytest",
                "faq_title": title,
                "question_1": "This is question 1",
                "question_2": "This is question 2",
                "question_3": "This is question 3",
                "question_4": "This is question 4",
                "question_5": "This is question 5",
                "faq_weight": 1,
                "faq_content_to_send": "Test Content Data",
                "submit": "True",
            },
        )

        if outcome == "success":
            assert re.search(
                "Successfully added new FAQ", response.get_data(as_text=True)
            )
        if outcome == "invalid":
            assert re.search(
                "The following faq title already exists:",
                response.get_data(as_text=True),
            )

    @pytest.mark.parametrize(
        "weight, error_msg",
        [
            (12, "Successfully added new FAQ"),
            (0, "This field is required"),
            (-1, "Weight must be at least 1"),
            (0.3, "This field is required"),
            ("hello", "This field is required"),
        ],
    )
    def test_add_new_faq_incorrect_weight(
        self, weight, error_msg, client, credentials_fullaccess, clean_faq_table
    ):
        """
        Note: this test, unlike some other `add_new_faq` tests, is NOT monkeypatched
        and hence needs to connect to a core model to pass. This is left as is on
        purpose to test the integration with core model.
        """
        response = client.post(
            "/faqs/add",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "tag_1": "weight",
                "tag_2": "test",
                "faq_author": "pytest",
                "faq_title": "test_title",
                "faq_weight": weight,
                "faq_content_to_send": "Test Content Data",
                "question_1": "This is question 1",
                "question_2": "This is question 2",
                "question_3": "This is question 3",
                "question_4": "This is question 4",
                "question_5": "This is question 5",
                "submit": "True",
            },
        )

        assert re.search(error_msg, response.get_data(as_text=True))

    @pytest.mark.parametrize(
        "question_1,question_2,question_3,question_4,question_5,question_6, error_msg",
        [
            (
                "This is question 1",
                "This is question 2",
                "This is question 3",
                "This is question 4",
                "This is question 5",
                None,
                "Successfully added new FAQ",
            ),
            (
                "This is question 1",
                " This is question 2",
                "This is question 3",
                "This is question 4",
                "This is question 5",
                " ",
                "The following questions are invalid",
            ),
        ],
    )
    def test_add_incorrect_question(
        self,
        question_1,
        question_2,
        question_3,
        question_4,
        question_5,
        question_6,
        error_msg,
        client,
        credentials_fullaccess,
        clean_faq_table,
    ):
        response = client.post(
            "/faqs/add",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "tag_1": "weight",
                "tag_2": "test",
                "faq_author": "pytest",
                "faq_title": "test_question",
                "faq_weight": 12,
                "faq_content_to_send": "Test Content Data",
                "question_1": question_1,
                "question_2": question_2,
                "question_3": question_3,
                "question_4": question_4,
                "question_5": question_5,
                "question_6": question_6,
                "submit": "True",
            },
        )
        assert re.search(error_msg, response.get_data(as_text=True))


class TestEditFAQ:

    insert_faq = (
        "INSERT INTO faqmatches ("
        "faq_id, faq_tags, faq_author, faq_title, faq_content_to_send, "
        "faq_weight, faq_added_utc, faq_thresholds,faq_questions) "
        "VALUES (:faq_id, :faq_tags, :author, :title, :content, :weight, "
        ":added_utc, :threshold,:faq_questions)"
    )
    faq_tags = [
        """{"rock", "guitar", "melody", "chord"}""",
        """{"cheese", "tomato", "bread", "mustard"}""",
        """{"rock", "lake", "mountain", "sky"}""",
        """{"trace", "vector", "length", "angle"}""",
        """{"draw", "sing", "exercise", "code"}""",
        """{"digest", "eat", "chew", "expel"}""",
    ]
    faq_other_params = {
        "added_utc": "2022-04-14",
        "author": "pytest",
        "content": "{}",
        "faq_questions": """{"Dummmy question 1", "Dummmy question 2", "Dummmy question 3", "Dummmy question 4","Dummmy question 5","Dummy question 6"}""",
        "weight": 2,
        "threshold": "{0.1, 0.1, 0.1, 0.1}",
    }

    @pytest.fixture(scope="class")
    def faq_data(self, client, db_engine):
        with db_engine.connect() as db_connection:
            inbound_sql = text(self.insert_faq)
            for i, tags in enumerate(self.faq_tags):
                db_connection.execute(
                    inbound_sql,
                    faq_id=1000 + i,
                    title=f"Pytest title #{i}",
                    faq_tags=tags,
                    **self.faq_other_params,
                )
        yield
        with db_engine.connect() as db_connection:
            t = text("DELETE FROM faqmatches " "WHERE faq_author='pytest'")
            db_connection.execute(t)

    def test_edit_page_fails_unauthorized(self, faq_data, client, credentials_readonly):
        response = client.get(
            "/faqs/edit/1001",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_readonly},
        )
        assert response.status_code == 403

    def test_edit_page_loads_authorized(self, faq_data, client, credentials_fullaccess):
        response = client.get(
            "/faqs/edit/1001",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
        )
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "tag1,tag2,outcome",
        [("hello", "world", "success"), ("madeupword", "world", "invalid")],
    )
    def test_edit_faq(
        self, tag1, tag2, outcome, faq_data, client, credentials_fullaccess, monkeypatch
    ):
        monkeypatch.setattr(views, "validate_tags", my_validate_tags)
        response = client.post(
            "/faqs/edit/1001",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "tag_1": tag1,
                "tag_2": tag2,
                "faq_author": "pytest",
                "faq_title": "test_title",
                "faq_content_to_send": "Test Content Data",
                "question_1": "This is question 1",
                "question_2": "This is question 2",
                "question_3": "This is question 3",
                "question_4": "This is question 4",
                "question_5": "This is question 5",
                "faq_weight": 10,
                "submit": "True",
            },
        )

        if outcome == "success":
            assert re.search(
                "Successfully edited FAQ with ID: 1001", response.get_data(as_text=True)
            )
        if outcome == "invalid":
            assert re.search(
                "The following tags are invalid:", response.get_data(as_text=True)
            )

    @pytest.mark.parametrize(
        "faq_id,title,outcome",
        [
            (1001, "Pytest title #1", "success"),
            (1001, "Pytest title #2", "invalid"),
            (1001, "Pytest title #7", "success"),
        ],
    )
    def test_edit_faq_incorrect_title(
        self, faq_data, faq_id, title, outcome, client, credentials_fullaccess
    ):
        response = client.post(
            f"/faqs/edit/{faq_id}",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "tag_1": "Hello",
                "tag_2": "World",
                "faq_author": "pytest",
                "faq_title": title,
                "question_1": "This is question 1",
                "question_2": "This is question 2",
                "question_3": "This is question 3",
                "question_4": "This is question 4",
                "question_5": "This is question 5",
                "faq_weight": 1,
                "faq_content_to_send": "Test Content Data",
                "submit": "True",
            },
        )

        if outcome == "success":
            assert re.search(
                "Successfully edited FAQ with ID: 1001", response.get_data(as_text=True)
            )
        if outcome == "invalid":
            assert re.search(
                "The following faq title already exists:",
                response.get_data(as_text=True),
            )

    @pytest.mark.parametrize(
        "weight, error_msg",
        [
            (12, "Successfully edited FAQ with ID: 1001"),
            (0, "This field is required"),
            (-1, "Weight must be at least 1"),
            (0.3, "This field is required"),
            ("hello", "This field is required"),
        ],
    )
    def test_edit_faq_incorrect_weight(
        self, weight, error_msg, faq_data, client, credentials_fullaccess
    ):
        """
        Note: this test, unlike some other `edit_faq` tests, is NOT monkeypatched
        and hence needs to connect to a core model to pass. This is left as is on
        purpose to test the integration with core model.
        """

        response = client.post(
            "/faqs/edit/1001",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "tag_1": "weight",
                "tag_2": "test",
                "faq_author": "pytest",
                "faq_title": f"test_title_{weight}",
                "question_1": "This is question 1",
                "question_2": "This is question 2",
                "question_3": "This is question 3",
                "question_4": "This is question 4",
                "question_5": "This is question 5",
                "faq_weight": weight,
                "faq_content_to_send": "Test Content Data",
                "submit": "True",
            },
        )

        assert re.search(error_msg, response.get_data(as_text=True))

    @pytest.mark.parametrize(
        "question_1,question_2,question_3,question_4,question_5,question_6, error_msg",
        [
            (
                "Dummmy question 1",
                "Dummmy question 2",
                "Dummmy question 3",
                "Dummmy question 4",
                "Dummmy question 5",
                None,
                "Successfully edited FAQ with ID: 1001",
            ),
            (
                "Dummmy question 1",
                "Dummmy question 2",
                "Dummmy question 3",
                "Dummmy question 4",
                "Dummmy question 5",
                " ",
                "The following questions are invalid",
            ),
        ],
    )
    def test_edit_incorrect_question(
        self,
        question_1,
        question_2,
        question_3,
        question_4,
        question_5,
        question_6,
        error_msg,
        client,
        faq_data,
        credentials_fullaccess,
    ):
        response = client.post(
            "/faqs/edit/1001",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
            data={
                "tag_1": "weight",
                "tag_2": "test",
                "faq_author": "pytest",
                "faq_title": "test_question",
                "faq_weight": 12,
                "faq_content_to_send": "Test Content Data",
                "question_1": question_1,
                "question_2": question_2,
                "question_3": question_3,
                "question_4": question_4,
                "question_5": question_5,
                "question_6": question_6,
                "submit": "True",
            },
        )
        assert re.search(error_msg, response.get_data(as_text=True))


class TestDeleteFAQ:

    insert_faq = (
        "INSERT INTO faqmatches ("
        "faq_id, faq_tags, faq_author, faq_title, faq_content_to_send, "
        "faq_weight, faq_added_utc, faq_thresholds,faq_questions) "
        "VALUES (:faq_id, :faq_tags, :author, :title, :content, :weight, "
        ":added_utc, :threshold,:faq_questions)"
    )
    faq_tags = [
        """{"rock", "guitar", "melody", "chord"}""",
        """{"cheese", "tomato", "bread", "mustard"}""",
        """{"rock", "lake", "mountain", "sky"}""",
        """{"trace", "vector", "length", "angle"}""",
        """{"draw", "sing", "exercise", "code"}""",
        """{"digest", "eat", "chew", "expel"}""",
    ]
    faq_other_params = {
        "added_utc": "2022-04-14",
        "author": "pytest",
        "content": "{}",
        "faq_questions": """{"Dummmy question 1", "Dummmy question 2", "Dummmy question 3", "Dummmy question 4","Dummmy question 5"}""",
        "weight": 2,
        "threshold": "{0.1, 0.1, 0.1, 0.1}",
    }

    @pytest.fixture(scope="class")
    def faq_data(self, client, db_engine):
        with db_engine.connect() as db_connection:
            inbound_sql = text(self.insert_faq)
            for i, tags in enumerate(self.faq_tags):
                db_connection.execute(
                    inbound_sql,
                    faq_id=1000 + i,
                    title=f"Pytest title #{i}",
                    faq_tags=tags,
                    **self.faq_other_params,
                )
        yield
        with db_engine.connect() as db_connection:
            t = text("DELETE FROM faqmatches " "WHERE faq_author='pytest'")
            db_connection.execute(t)

    def test_delete_page_fails_unauthorized(
        self, faq_data, client, credentials_readonly
    ):
        response = client.get(
            "/faqs/delete/1001",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_readonly},
        )
        assert response.status_code == 403

    def test_delete_page_loads_authorized(
        self, faq_data, client, credentials_fullaccess
    ):
        response = client.get(
            "/faqs/delete/1002",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
        )
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "faq_id,status_code,message",
        [
            ("aabbcc", 404, "Invalid FAQ ID: aabbcc"),
            ("1000001", 404, "No FAQ with ID: 1"),
            ("1003", 200, "Successfully deleted FAQ with ID: 1003"),
        ],
    )
    def test_delete_faq(
        self, faq_id, status_code, message, faq_data, client, credentials_fullaccess
    ):
        response = client.post(
            f"/faqs/delete/{faq_id}",
            follow_redirects=True,
            headers={"Authorization": "Basic " + credentials_fullaccess},
        )

        assert re.search(message, response.get_data(as_text=True))
        assert response.status_code == status_code
