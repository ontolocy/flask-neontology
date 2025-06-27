def test_page_list(test_client):
    response = test_client.get("/docs/")

    assert "Documentation Pages" in response.text

    assert "Page 1" in response.text


def test_page_view(test_client):
    response = test_client.get("/docs/page-1/")

    assert "This is page1" in response.text

    assert "Page 1" in response.text
