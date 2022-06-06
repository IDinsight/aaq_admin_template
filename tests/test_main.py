import pytest
import sqlalchemy as sa


class MockInspect:
    def __init__(self, tables):
        self.tables = tables

    def get_table_names(
        self,
    ):
        return self.tables


@pytest.fixture
def correct_model_string(app):
    model_connection_string = (
        f"{app.MODEL_PROTOCOL}://{app.MODEL_HOST}:9902/auth-healthcheck"
    )
    return model_connection_string


class TestHealthCheck:
    """
    We mock out the core model in all of these test cases
    """

    def test_health_check_works(self, correct_model_string, client, requests_mock):
        requests_mock.get(correct_model_string)
        response = client.get("/healthcheck")
        assert response.status_code == 200

    def test_health_check_fails_no_faq_table(
        self, correct_model_string, client, monkeypatch, requests_mock
    ):
        requests_mock.get(correct_model_string)
        monkeypatch.setattr(sa, "inspect", lambda x: MockInspect(["urgency_rules"]))
        response = client.get("/healthcheck")

        assert response.status_code == 500

    def test_health_check_passes_no_ud_table_ud_disabled(
        self, correct_model_string, client, monkeypatch, requests_mock
    ):
        requests_mock.get(correct_model_string)
        monkeypatch.setattr(sa, "inspect", lambda x: MockInspect(["faqmatches"]))
        response = client.get("/healthcheck")

        assert response.status_code == 200

    @pytest.mark.ud_test
    def test_health_check_fails_no_ud_table_ud_enabled(
        self, correct_model_string, client_ud, monkeypatch, requests_mock
    ):
        requests_mock.get(correct_model_string)
        monkeypatch.setattr(sa, "inspect", lambda x: MockInspect(["faqmatches"]))
        response = client_ud.get("/healthcheck")

        assert response.status_code == 500

    def test_health_check_fails_model_failure(
        self, correct_model_string, client, requests_mock
    ):
        requests_mock.get(correct_model_string, status_code=500)
        response = client.get("/healthcheck")
        assert response.status_code == 500
