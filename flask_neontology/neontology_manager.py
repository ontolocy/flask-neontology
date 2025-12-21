import os
from enum import Enum
from typing import Any, List, Optional

from flask import Blueprint, Flask, g
from neontology import BaseNode, GraphConnection, init_neontology
from neontology.graphengines import Neo4jConfig
from neontology.graphengines.graphengine import GraphEngineConfig
from spectree import Response, SpecTree, Tag

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
from .views import NeontologyAPIView, NeontologyView


def loc():
    """Get the current location of the blueprint for loading template/static files."""
    location = os.path.abspath(os.path.dirname(__file__)) + "/"
    return location


bp = Blueprint(
    "neontology_core",
    __name__,
    template_folder=loc() + "templates",
)


class NeontologyManager:
    def __init__(
        self,
        app: Optional[Flask] = None,
        graph_config: Optional[GraphEngineConfig] = None,
        autograph_nodes: List[BaseNode] = [],
        views: List[type[NeontologyView]] = [],
        api_views: dict[str, List[type[NeontologyAPIView]]] = {},
    ):
        if app is not None:
            self.init_app(
                app,
                graph_config=graph_config,
                autograph_nodes=autograph_nodes,
                views=views,
                api_views=api_views,
            )

    def init_app(
        self,
        app: Flask,
        graph_config: Optional[GraphEngineConfig] = None,
        autograph_nodes: List[type[BaseNode]] = [],
        autograph_decorators: List = [],
        views: List[type[NeontologyView]] = [],
        api_views: dict[str, List[type[NeontologyAPIView]]] = {},
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

        self.api_views = api_views

        # register neontology API views
        if api_views:
            self.api = {}
            for api_ver, api_ver_views in api_views.items():
                # Initialize SpecTree
                self.api[api_ver] = SpecTree(
                    "flask",
                    title="API",
                    version=api_ver,
                    description=f"API {api_ver} Documentation",
                    mode="strict",
                    path="apidoc/" + api_ver,
                )
                self.register_api_views(api_ver_views, api_ver, app)
                self.api[api_ver].register(app)

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

    def register_api_views(
        self, api_views: List[type[NeontologyAPIView]], api_ver, app: Flask
    ) -> None:
        for api_view in api_views:
            api_view.validate_configuration()

            # Create tag for documentation grouping
            tag = Tag(
                name=api_view.resource_name.title(),
                description=api_view.tag_description,
            )

            # Store tag and api reference in the view class
            api_view._tag = tag
            api_view._api = self.api[api_ver]

            # Create decorated methods
            list_view = self._create_list_view(api_view, tag, api_ver)
            detail_view = self._create_detail_view(api_view, tag, api_ver)

            # Register routes
            endpoint_base = f"{api_view.resource_name}_api"

            app.add_url_rule(
                api_view.get_list_endpoint(api_ver),
                view_func=list_view,
                endpoint=f"{endpoint_base}_list",
                methods=["GET"],
            )

            app.add_url_rule(
                api_view.get_detail_endpoint(api_ver),
                view_func=detail_view,
                endpoint=f"{endpoint_base}_detail",
                methods=["GET"],
            )

            # Register related resource endpoints
            for relationship, (
                related_model,
                _,
            ) in api_view.related_resources.items():
                related_view = self._create_related_view(
                    api_view, relationship, related_model, tag, api_ver
                )

                app.add_url_rule(
                    api_view.get_related_endpoint(relationship, api_ver),
                    view_func=related_view,
                    endpoint=f"{endpoint_base}_{relationship}",
                    methods=["GET"],
                )

    def _create_list_view(
        self, view_class: type[NeontologyAPIView], tag: Tag, api_ver: str
    ) -> callable:
        """Create the list view function with proper decorators"""

        api = self.api[api_ver]

        @api.validate(resp=Response(HTTP_200=List[view_class.model]), tags=[tag])
        def list_view():
            f"""List all {view_class.resource_name}"""
            view_instance = view_class()
            return view_instance.get(pp=None)

        list_view.__name__ = f"{view_class.resource_name}_list"
        list_view.__doc__ = f"Get all {view_class.resource_name}"

        return list_view

    def _create_detail_view(
        self, view_class: type[NeontologyAPIView], tag: Tag, api_ver: str
    ) -> callable:
        """Create the detail view function with proper decorators"""

        api = self.api[api_ver]

        @api.validate(
            resp=Response(HTTP_200=view_class.model, HTTP_404=None), tags=[tag]
        )
        def detail_view(pp):
            f"""Get {view_class.resource_name[:-1]} by ID"""
            view_instance = view_class()
            return view_instance.get(pp=pp)

        detail_view.__name__ = f"{view_class.resource_name}_detail"
        detail_view.__doc__ = f"Get {view_class.resource_name[:-1]} by ID"

        return detail_view

    def _create_related_view(
        self,
        view_class: type[NeontologyAPIView],
        relationship: str,
        related_model: type[BaseNode],
        tag: Tag,
        api_ver: str,
    ) -> callable:
        """Create a related resource view function with proper decorators"""

        api = self.api[api_ver]

        @api.validate(
            resp=Response(HTTP_200=List[related_model], HTTP_404=None), tags=[tag]
        )
        def related_view(pp: int):
            f"""Get {relationship} for {view_class.resource_name[:-1]}"""
            view_instance = view_class()
            return view_instance.get(pp=pp, relationship=relationship)

        related_view.__name__ = f"{view_class.resource_name}_{relationship}"
        related_view.__doc__ = (
            f"Get {relationship} for a {view_class.resource_name[:-1]}"
        )

        return related_view

    def get_graph(self) -> GraphConnection:
        if "neontology_gc" not in g:
            g.neontology_gc = GraphConnection()

        return g.neontology_gc
