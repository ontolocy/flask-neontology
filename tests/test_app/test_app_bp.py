def test_home(test_client):
    response = test_client.get("/")

    assert "Flask Neontology Demo Homepage" in response.text


def test_components_catalogue(test_client):
    response = test_client.get("/components/")

    assert "TextComponent" in response.text
