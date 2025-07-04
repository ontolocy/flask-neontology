from typing import Optional

from flask import Flask
from neontology.graphengines.graphengine import GraphEngineConfig

from flask_neontology import NeontologyManager

from .ontology.author import NeontologyAuthorNode
from .ontology.page import (
    NeontologyPageNode,
)
from .views.pages import NeontologyPageListView, NeontologyPageView

nm = NeontologyManager()


def create_app(app_env="DEV", config: Optional[GraphEngineConfig] = None) -> Flask:
    app = Flask(
        __name__,
    )

    app.config["APP_ENV"] = app_env

    # Set templating environment
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    #
    # Set up neontology extension
    #

    if app_env == "FREEZE":
        nodes = []

    else:
        nodes = [
            NeontologyPageNode,
            NeontologyAuthorNode,
        ]

    node_pages = [
        NeontologyPageListView,
        NeontologyPageView,
    ]

    nm.init_app(
        app=app,
        graph_config=config,
        autograph_nodes=nodes,
        views=node_pages,
    )

    #
    # import app blueprint(s)
    #

    from .app_bp import bp

    app.register_blueprint(bp)

    if app_env != "FREEZE":
        from .extra_bp import bp as extra_bp

        app.register_blueprint(extra_bp)

    return app
