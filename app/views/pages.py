from typing import Optional

from flask_neontology.components import (
    CardListComponent,
    MarkdownComponent,
    TextComponent,
)
from flask_neontology.components.breadcrumb_element import BreadcrumbElement
from flask_neontology.components.page_component import PageElementsEnum
from flask_neontology.views import (
    NeontologyListView,
    NeontologyNodeView,
    NeontologyViewset,
    page_element,
    page_section,
)
from flask_neontology.views.apiview import NeontologyAPIView

from ..ontology.author import NeontologyAuthorNode
from ..ontology.page import NeontologyPageNode


class NeontologyPageViewset(NeontologyViewset):
    model: type[NeontologyPageNode] = NeontologyPageNode
    slug: str = "docs"

    def list_title(self) -> str:
        return "pages"


class NeontologyPageListView(NeontologyListView):
    viewset_handler = NeontologyPageViewset

    @page_element(PageElementsEnum.TITLE)
    def page_title(self) -> str:
        return "Documentation Pages"

    @page_element(PageElementsEnum.BREADCRUMBS)
    def list_breadcrumbs(self) -> BreadcrumbElement:
        return BreadcrumbElement(breadcrumbs=self.viewset.list_breadcrumbs())

    @page_section(title=None)
    def pages(self) -> CardListComponent:
        nodes = self.viewset.match_nodes()
        return self.viewset.nodes_to_cards(nodes)


class NeontologyPageView(NeontologyNodeView):
    viewset_handler = NeontologyPageViewset

    @page_element(PageElementsEnum.TITLE)
    def page_title(self) -> str:
        if self.node is None:
            raise ValueError("Node not defined on NeontologyPageView")
        return self.node.title

    @page_element(PageElementsEnum.BREADCRUMBS)
    def list_breadcrumbs(self) -> BreadcrumbElement:
        return BreadcrumbElement(breadcrumbs=self.viewset.list_breadcrumbs())

    @page_section(title=None)
    def page_author(self) -> Optional[TextComponent]:
        if self.node is None:
            raise ValueError("Node not defined on NeontologyPageView")
        if self.node.authors():
            authors = "Author(s): " + ", ".join(self.node.authors())

            return TextComponent(text=authors)

    @page_section(title=None)
    def page_content(self) -> MarkdownComponent:
        if self.node is None:
            raise ValueError("Node not defined on NeontologyPageView")
        md = MarkdownComponent(text=self.node.content)
        return md


class PageAPIView(NeontologyAPIView):
    model = NeontologyPageNode
    resource_name = "pages"
    tag_description = "API endpoints for documentation pages."

    related_resources = {"authors": (NeontologyAuthorNode, "get_related_authors")}

    def get_related_authors(self, id: str):
        page = self.match_node(id)
        if page:
            return page.author_nodes()
        return None
