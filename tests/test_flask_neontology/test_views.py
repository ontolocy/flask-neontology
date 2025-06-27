def test_list(mini_client):
    response = mini_client.get("/dummies/")

    assert b"Dummy Data Views" in response.data
    assert b"foo" in response.data
    assert b"bar" in response.data


def test_item(mini_client):
    response = mini_client.get("/dummies/foo", follow_redirects=True)

    assert b"foo CONTENT" in response.data

    assert b"foo TITLE" in response.data
