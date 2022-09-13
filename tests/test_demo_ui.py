import base64

import pytest


@pytest.mark.parametrize("endpoint", ["/demo", "/demo/apicall"])
def test_demo_page_loads(endpoint, client):
    credentials = base64.b64encode(b"readonly_user:testread123").decode("utf-8")
    response = client.get(
        endpoint,
        follow_redirects=True,
        headers={"Authorization": "Basic " + credentials},
    )
    assert response.status_code == 200


def test_check_new_faqs_page_load(client):
    credentials = base64.b64encode(b"readonly_user:testread123").decode("utf-8")
    response = client.get(
        "/demo/check-new-faq-tags",
        follow_redirects=True,
        headers={"authorization": "basic " + credentials},
    )
    assert response.status_code == 200
