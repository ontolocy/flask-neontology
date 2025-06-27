from typing import ClassVar, Optional

import pytest
from flask import Flask
from neontology import BaseNode, BaseRelationship

from flask_neontology import (
    NeontologyEndpointView,
    NeontologyListView,
    NeontologyManager,
    NeontologyNodeView,
    NeontologyViewset,
)
from flask_neontology.components import (
    CardListComponent,
    PageElementsEnum,
    TextComponent,
)
from flask_neontology.views import (
    page_element,
    page_section,
)


class DummyNode(BaseNode):
    __primarylabel__: ClassVar[str] = "DummyNode"
    __primaryproperty__: ClassVar[str] = "name"

    name: str
    description: Optional[str] = None


class DummyRelationship(BaseRelationship):
    __relationshiptype__: ClassVar[str] = "DUMMY_RELATIONSHIP"

    source: DummyNode
    target: DummyNode
    optional_prop: Optional[str] = None


class DummyViewset(NeontologyViewset):
    model = DummyNode
    slug = "dummies"
    title = "Dummy Data Views"


class DummyListView(NeontologyListView):
    viewset_handler = DummyViewset

    @page_section(title=None)
    def pages(self) -> CardListComponent:
        nodes = self.viewset.match_nodes()
        return self.viewset.nodes_to_cards(nodes)


class DummyNodeView(NeontologyNodeView):
    viewset_handler = DummyViewset

    @page_element(PageElementsEnum.TITLE)
    def title(self):
        return f"{self.node.name} TITLE"

    @page_section(title=None)
    def content(self):
        return TextComponent(text=f"{self.node.name} CONTENT")

    @page_section(title=None)
    def description(self):
        if self.node.description:
            return TextComponent(text=f"{self.node.description}")
        else:
            return None


class DummyEndpointView(NeontologyEndpointView):
    viewset_handler = DummyViewset
    endpoint = "test-endpoint"


@pytest.fixture
def populate_dummy_nodes(use_graph):
    foo = DummyNode(name="foo")
    foo.merge()

    bar = DummyNode(name="bar")
    bar.merge()


@pytest.fixture
def mini_app(get_graph_config, populate_dummy_nodes, use_graph):
    """A small app for testing the extension"""

    nm = NeontologyManager()

    app = Flask("TestAPP")

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    app.config["SERVER_NAME"] = "localhost"
    app.config["FREEZER_IGNORE_MIMETYPE_WARNINGS"] = True
    app.config["FREEZER_IGNORE_404_NOT_FOUND"] = True

    nm.init_app(
        app=app,
        graph_config=get_graph_config,
        autograph_nodes=[DummyNode],
        views=[DummyEndpointView, DummyListView, DummyNodeView],
    )

    @app.route("/")
    def index():
        return "Hello World"

    yield app


@pytest.fixture
def mini_client(mini_app):
    return mini_app.test_client()


@pytest.fixture
def cli_runner(mini_app):
    return mini_app.test_cli_runner()
