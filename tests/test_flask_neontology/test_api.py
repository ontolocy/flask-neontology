def test_list(mini_client):
    response = mini_client.get("/api/v1/dummies.json")

    assert {"description": None, "name": "foo"} in response.json

    assert {"description": None, "name": "bar"} in response.json


def test_item(mini_client):
    response = mini_client.get("/api/v1/dummies/foo.json", follow_redirects=True)

    assert response.json == {"description": None, "name": "foo"}


def test_related(mini_client):
    response = mini_client.get(
        "/api/v1/dummies/foo/dum-dummies.json", follow_redirects=True
    )

    print(response.data)

    assert response.json == [
        {"description": None, "name": "bar"},
    ]
