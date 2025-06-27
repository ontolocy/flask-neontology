def test_list(mini_client):
    response = mini_client.get("/autograph/")

    assert response.status_code == 200

    assert b"DummyNode" in response.data


def test_label_page(mini_client):
    response = mini_client.get("/autograph/DummyNode/")

    assert response.status_code == 200

    assert b"foo" in response.data


def test_node_page(mini_client):
    response = mini_client.get("/autograph/DummyNode/node/foo/")

    assert response.status_code == 200

    assert b"foo" in response.data
    assert b"Node Properties" in response.data


def test_edit_node(mini_client):
    response = mini_client.get("/autograph/DummyNode/node/foo/update/")

    assert response.status_code == 200

    assert b"foo" in response.data


def test_edit_node_post(mini_client):
    post_response = mini_client.post(
        "/autograph/DummyNode/node/foo/update/",
        data={"name": "foo", "description": "description of foo"},
        follow_redirects=True,
    )

    assert post_response.status_code == 200

    assert b"description of foo" in post_response.data


def test_add_node_rel(mini_client):
    response = mini_client.get("/autograph/DummyNode/node/foo/create-relationships/")

    assert response.status_code == 200

    assert b"DUMMY_RELATIONSHIP" in response.data
    assert b"optional_prop" in response.data


def test_add_node_rel_post(mini_client):
    post_response = mini_client.post(
        "/autograph/DummyNode/node/foo/create-relationships/",
        data={
            "source": "foo",
            "source_type": "DummyNode",
            "target": "bar",
            "target_type": "DummyNode",
            "optional_prop": "optional value",
            "relationship_type": "DUMMY_RELATIONSHIP",
        },
        follow_redirects=True,
    )

    assert post_response.status_code == 200

    assert b"bar" in post_response.data
