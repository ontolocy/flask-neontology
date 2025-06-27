import os
from enum import Enum
from typing import Any, List, Optional

from flask import Blueprint, Flask, g
from neontology import BaseNode, GraphConnection, init_neontology
from neontology.graphengines import Neo4jConfig
from neontology.graphengines.graphengine import GraphEngineConfig

from .autograph import (
    AutographViewset,
    LabelCreateEndpointView,
    LabelCreateRelationshipEndpointView,
    LabelEditEndpointView,
    LabelListView,
    LabelView,
    autograph_view,
)
from .commands import export, freeze, ingest
from .views import NeontologyView


def loc():
    """Get the current location of the blueprint for loading template/static files."""
    location = os.path.abspath(os.path.dirname(__file__)) + "/"
    return location


bp = Blueprint(
    "neontology_core",
    __name__,
    # url_prefix="/nodes",
    template_folder=loc() + "templates",
    # static_folder=loc() + "static",
    # static_url_path="/neontology/static",
)


class NeontologyManager:
    def __init__(
        self,
        app: Optional[Flask] = None,
        graph_config: Optional[GraphEngineConfig] = None,
        autograph_nodes: List[BaseNode] = [],
        views: List[type[NeontologyView]] = [],
    ):
        if app is not None:
            self.init_app(
                app,
                graph_config,
                autograph_nodes=autograph_nodes,
                views=views,
            )

    def init_app(
        self,
        app: Flask,
        graph_config: Optional[GraphEngineConfig] = None,
        autograph_nodes: List[type[BaseNode]] = [],
        autograph_decorators: List = [],
        views: List[type[NeontologyView]] = [],
    ) -> None:
        app.neontology_manager = self  # type: ignore[attr-defined]

        app.logger.info("Flask-Neontology is not intended for production use.")

        if not graph_config:
            if app.config.get("NEONTOLOGY_GRAPH_CONFIG"):
                graph_config = app.config.get("NEONTOLOGY_GRAPH_CONFIG")

            else:
                graph_config = Neo4jConfig()  # type: ignore

        init_neontology(config=graph_config)

        # register the blueprint (which will make template(s) available)
        app.register_blueprint(bp)

        # add generic node pages
        self.nodes = {x.__primarylabel__: x for x in autograph_nodes}

        # register the autograph
        if autograph_nodes:
            app.config["NEONTOLOGY_AUTOGRAPH"] = True
            self.register_autograph(app, decorators=autograph_decorators)

        else:
            app.config["NEONTOLOGY_AUTOGRAPH"] = False

        self.views = views

        # register neontology views
        if views:
            self.register_views(views, app)

        # set up jinja

        @app.template_filter()
        def neontology_to_string(obj: Any) -> Any:
            if isinstance(obj, Enum):
                return obj.value

            if isinstance(obj, list):
                strings = [neontology_to_string(x) for x in obj]
                return ", ".join(strings)

            # For all other types, let Jinja use default behavior
            return obj

        # register CLI commands
        app.cli.add_command(ingest)
        app.cli.add_command(freeze)
        app.cli.add_command(export)

    def register_autograph(self, app: Flask, decorators: list) -> None:
        ag_view = autograph_view

        for decorator in decorators:
            ag_view = decorator(ag_view)

        app.add_url_rule(AutographViewset.get_base_url(), view_func=ag_view)

        for node_class in self.nodes.values():
            viewset_data = AutographViewset(node_class)

            list_view = LabelListView.as_view(
                "AutoGraph" + viewset_data.list_view_name(), node_class
            )
            create_view = LabelCreateEndpointView.as_view(
                LabelCreateEndpointView.view_name(node_class), node_class
            )
            edit_view = LabelEditEndpointView.as_view(
                LabelEditEndpointView.view_name(node_class), node_class
            )
            rel_create_view = LabelCreateRelationshipEndpointView.as_view(
                LabelCreateRelationshipEndpointView.view_name(node_class), node_class
            )
            item_view = LabelView.as_view(
                "AutoGraph" + viewset_data.item_view_name(), node_class
            )

            for decorator in decorators:
                list_view = decorator(list_view)
                create_view = decorator(create_view)
                edit_view = decorator(edit_view)
                rel_create_view = decorator(rel_create_view)
                item_view = decorator(item_view)

            app.add_url_rule(viewset_data.list_url(), view_func=list_view)

            app.add_url_rule(
                LabelCreateEndpointView.view_url_rule(node_class), view_func=create_view
            )

            app.add_url_rule(
                LabelEditEndpointView.view_url_rule(node_class), view_func=edit_view
            )

            app.add_url_rule(
                LabelCreateRelationshipEndpointView.view_url_rule(node_class),
                view_func=rel_create_view,
            )

            app.add_url_rule(viewset_data.item_url_pattern(), view_func=item_view)

    def register_views(self, views: List[type[NeontologyView]], app: Flask) -> None:
        for view in views:
            new_view = view.as_view(view.view_name())
            app.add_url_rule(view.view_url_rule(), view_func=new_view)

    def get_graph(self) -> GraphConnection:
        if "neontology_gc" not in g:
            g.neontology_gc = GraphConnection()

        return g.neontology_gc
