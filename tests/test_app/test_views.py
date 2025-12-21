def test_page_list(test_client):
    response = test_client.get("/docs/")

    assert "Documentation Pages" in response.text

    assert "Page 1" in response.text


def test_page_view(test_client):
    response = test_client.get("/docs/page-1/")

    assert "This is page1" in response.text

    assert "Page 1" in response.text


def test_api_view_list(test_client):
    response = test_client.get("/api/v1/pages.json")

    assert response.status_code == 200

    assert "Page 1" in [x["title"] for x in response.json]


def test_api_view_detail(test_client):
    response = test_client.get("/api/v1/pages/page-2.json")

    assert response.status_code == 200

    assert response.json["title"] == "Page 2"


def test_api_view_related(test_client):
    response = test_client.get("/api/v1/pages/page-2/authors.json")

    assert response.status_code == 200

    assert {"name": "Author 2"} in response.json
    assert {"name": "Author 3"} in response.json
