from flask import Flask

from flask_neontology import NeontologyManager

from .conftest import DummyEndpointView, DummyListView, DummyNode, DummyNodeView


def test_nm_init(get_graph_config):
    nm = NeontologyManager()

    app = Flask("TestAPP")

    nm.init_app(
        app=app,
        graph_config=get_graph_config,
    )

    @app.route("/")
    def index():
        return "Hello World"

    test_client = app.test_client()

    response = test_client.get("/")

    assert response.data == b"Hello World"

    autograph_response = test_client.get("/autograph/")

    assert autograph_response.status_code == 404


def test_nm_init_autograph(get_graph_config):
    nm = NeontologyManager()

    app = Flask("TestAPP")

    nm.init_app(
        app=app,
        graph_config=get_graph_config,
        autograph_nodes=[DummyNode],
    )

    test_client = app.test_client()

    response = test_client.get("/autograph/")

    assert response.status_code == 200

    # page should contain a link to explore the defined labels
    assert b"/autograph/DummyNode/" in response.data


def test_nm_init_views(get_graph_config, populate_dummy_nodes):
    nm = NeontologyManager()

    app = Flask("TestAPP")

    nm.init_app(
        app=app,
        graph_config=get_graph_config,
        views=[DummyEndpointView, DummyListView, DummyNodeView],
    )

    test_client = app.test_client()

    response = test_client.get("/dummies/")

    assert response.status_code == 200

    response = test_client.get("/dummies/foo/")

    assert response.status_code == 200

    response = test_client.get("/dummies/foo/test-endpoint")

    assert response.status_code == 200
