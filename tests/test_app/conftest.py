import logging

import pytest

from app import create_app
from app.ontology.author import NeontologyAuthorNode
from app.ontology.page import NeontologyPageNode, NeontologyPageToAuthor

logger = logging.getLogger(__name__)


@pytest.fixture()
def test_app(get_graph_config, use_graph):
    app = create_app(config=get_graph_config)

    yield app


@pytest.fixture()
def populated_app_graph(use_graph):
    page1 = NeontologyPageNode(
        title="Page 1", slug="page-1", content="## This is page1 content."
    )

    page1.merge()

    page2 = NeontologyPageNode(
        title="Page 2", slug="page-2", content="This is page2 content."
    )
    page2.merge()

    author1 = NeontologyAuthorNode(name="Author 1")
    author1.merge()

    author2 = NeontologyAuthorNode(name="Author 2")
    author2.merge()

    author3 = NeontologyAuthorNode(name="Author 3")
    author3.merge()

    page1_author1 = NeontologyPageToAuthor(source=page1, target=author1)
    page1_author1.merge()

    page1_author3 = NeontologyPageToAuthor(source=page1, target=author3)
    page1_author3.merge()

    page2_author2 = NeontologyPageToAuthor(source=page2, target=author2)
    page2_author2.merge()

    page2_author3 = NeontologyPageToAuthor(source=page2, target=author3)
    page2_author3.merge()


@pytest.fixture()
def test_client(test_app, populated_app_graph):
    return test_app.test_client()
