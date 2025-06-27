from typing import List

from neontology import GraphConnection

from ..components import (
    BreadcrumbElement,
    ColumnData,
    Component,
    Graph2dComponent,
    HTMLComponent,
    NodeTranslatedTableComponent,
    PageElementsEnum,
    TableComponent,
)
from ..views import (
    NeontologyNodeView,
    page_element,
    page_section,
)
from .labelendpoints import LabelCreateRelationshipEndpointView, LabelEditEndpointView
from .viewset import AutographViewset


class LabelView(NeontologyNodeView):
    viewset_handler = AutographViewset

    @page_element(PageElementsEnum.TITLE)
    def page_title(self) -> str:
        return str(self.node)

    @page_section(title=None)
    def node_table(self) -> List[Component]:
        title_html = f"""
<h2>Node Properties
<a class="icon-link" href="{
            self.viewset.node_to_endpoint_url(LabelEditEndpointView.endpoint, self.node)
        }">
  <i class="bi bi-pencil-square"></i>
</a></h2>"""
        title = HTMLComponent(raw_html=title_html)
        node_table = NodeTranslatedTableComponent(node=self.node)

        return [title, node_table]

    @page_section(title=None)
    def outgoing_relationships(self):
        title_html = f"""
<h2>Outgoing Relationships
<a class="icon-link" href="{
            self.viewset.node_to_endpoint_url(
                LabelCreateRelationshipEndpointView.endpoint, self.node
            )
        }">
  <i class="bi bi-node-plus"></i>
</a></h2>"""
        title = HTMLComponent(raw_html=title_html)

        outgoing_rels = self.node.get_related()

        if outgoing_rels.relationships:
            columns = [
                ColumnData(title="Target", result_field="target"),
                ColumnData(title="Relationship Type", result_field="relationship_type"),
            ]
            rows = [
                {"target": str(x.target), "relationship_type": x.__relationshiptype__}
                for x in outgoing_rels.relationships
            ]
            table = TableComponent(columns=columns, rows=rows)

            return [title, table]
        else:
            return [title]

    @page_section(title="Graph Visualization")
    def graph_section(self) -> Graph2dComponent:
        gc = GraphConnection()

        cypher = f"""
        MATCH (n:{self.node.__primarylabel__})
        WHERE n.{self.node.__primaryproperty__} = $pp
        OPTIONAL MATCH (n)-[r]-(o)
        OPTIONAL MATCH (o)-[r2]-(o2)
        RETURN DISTINCT n,r,o,r2,o2
        LIMIT 100
        """

        params = {"pp": self.node.get_pp()}

        results = gc.evaluate_query(cypher, params)

        graph_data = {"directed": True, "nodes": [], "edges": []}

        graph_data["nodes"] = [
            {"__pp__": x["__pp__"], "__str__": x["__str__"], "LABEL": x["LABEL"]}
            for x in results.node_link_data["nodes"]
        ]

        graph_data["links"] = [
            {
                "RELATIONSHIP_TYPE": x["RELATIONSHIP_TYPE"],
                "SOURCE_LABEL": x["SOURCE_LABEL"],
                "TARGET_LABEL": x["TARGET_LABEL"],
                "source": x["source"],
                "target": x["target"],
            }
            for x in results.node_link_data["edges"]
        ]

        graph = Graph2dComponent(element_data=graph_data)

        return graph

    @page_element(PageElementsEnum.BREADCRUMBS)
    def breadcrumbs(self) -> BreadcrumbElement:
        return BreadcrumbElement(breadcrumbs=self.viewset.item_breadcrumbs(self.node))
