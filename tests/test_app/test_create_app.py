def test_dev_mode(get_graph_config):
    """Test that the app is in development mode which should be the default."""
    from app import create_app

    app = create_app(config=get_graph_config)
    assert app.config["APP_ENV"] == "DEV"

    client = app.test_client()

    response = client.get("/")
    assert "AutoGraph" in response.text


def test_freeze_mode(get_graph_config):
    """Test that the app is in freeze mode.
    This which should disable create page and AutoGraph."""

    from app import create_app

    app = create_app(app_env="FREEZE", config=get_graph_config)
    assert app.config["APP_ENV"] == "FREEZE"

    client = app.test_client()

    autograph_response = client.get("/")
    assert "AutoGraph" not in autograph_response.text

    create_page_response = client.get("/create-page/")
    assert create_page_response.status_code == 404, (
        "Create page should not be available in freeze mode"
    )
