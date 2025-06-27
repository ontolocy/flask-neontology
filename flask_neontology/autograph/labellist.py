from typing import List

from ..components import (
    BreadcrumbElement,
    Component,
    HTMLComponent,
    MarkdownComponent,
    PageElementsEnum,
)
from ..views import (
    NeontologyListView,
    page_element,
    page_section,
)
from .labelendpoints import LabelCreateEndpointView
from .viewset import AutographViewset


class LabelListView(NeontologyListView):
    init_every_request = False

    viewset_handler = AutographViewset

    @page_element(PageElementsEnum.TITLE)
    def page_title(self) -> str:
        return self.viewset.list_title()

    @page_element(PageElementsEnum.BREADCRUMBS)
    def list_breadcrumbs(self) -> BreadcrumbElement:
        return BreadcrumbElement(breadcrumbs=self.viewset.list_breadcrumbs())

    @page_section(title=None)
    def generate_node_list_table(self) -> List[Component]:
        title_html = f"""
<h2>Nodes
<a class="icon-link" href="{LabelCreateEndpointView.view_url_rule(self.model)}">
  <i class="bi bi-plus-square"></i>
</a></h2>"""
        title = HTMLComponent(raw_html=title_html)

        nodes = self.viewset.match_nodes()

        node_list_table = self.viewset.nodes_to_table(
            nodes, fields=["__str__", self.model.__primaryproperty__]
        )

        return [title, node_list_table]

    @page_section(title="Schema")
    def schema_section(self) -> MarkdownComponent:
        schema = self.model.neontology_schema()
        md = schema.md_node_table()

        return MarkdownComponent(text=md)
