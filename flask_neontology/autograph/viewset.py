from flask import current_app
from neontology.utils import (
    get_rels_by_type,
)

from ..components import (
    CardComponent,
    CardListComponent,
    Graph2dComponent,
    LinkComponent,
    LinkData,
    PageComponent,
    PageElements,
    SectionComponent,
)
from ..views import (
    NeontologyViewset,
)


class AutographViewset(NeontologyViewset):
    parents = (
        LinkData(url="/", title="Home"),
        LinkData(url="/autograph/", title="Autograph"),
    )

    def item_url_pattern(self) -> str:
        return str(f"{self.parents[-1].url}{str(self.list_title())}/node/<pp>/")


def autograph_view() -> str:
    neontology_manager = getattr(current_app, "neontology_manager", None)

    if neontology_manager is None:
        raise RuntimeError(
            "The Flask app does not have a 'neontology_manager' attribute. "
            "Please ensure it is initialized and attached to the app."
        )

    node_classes = neontology_manager.nodes

    label_cards = [
        CardComponent(
            title=label,
            links=[LinkComponent(url=AutographViewset(node_class).list_url())],
        )
        for label, node_class in node_classes.items()
    ]

    label_cards_list = CardListComponent(children=label_cards)

    label_cards_section = SectionComponent(
        title="Explore the Labels", body=label_cards_list
    )

    node_types = neontology_manager.nodes

    nodes = [
        {
            "__pp__": x.__primarylabel__,
            "__str__": "Label",
            "LABEL": x.__primarylabel__,
        }
        for x in node_types.values()
    ]

    rel_types = get_rels_by_type()

    links = [
        {
            "source": x.source_class.__primarylabel__,
            "target": x.target_class.__primarylabel__,
            "RELATIONSHIP_TYPE": (
                f"Relationship Type: {x.relationship_class.__relationshiptype__}"
            ),
        }
        for x in rel_types.values()
        if hasattr(x.source_class, "__primarylabel__")
        and hasattr(x.target_class, "__primarylabel__")
        and hasattr(x.relationship_class, "__relationshiptype__")
        and x.source_class.__primarylabel__ in node_types.keys()
        and x.target_class.__primarylabel__ in node_types.keys()
    ]

    graph_data = {"links": links, "nodes": nodes}

    graph_schema = Graph2dComponent(element_data=graph_data)
    graph_section = SectionComponent(title="Schema", body=graph_schema)

    elements = PageElements(title="Autograph")

    page = PageComponent(
        sections=[graph_section, label_cards_section], elements=elements
    )
    return page.render()
