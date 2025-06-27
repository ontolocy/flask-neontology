import urllib.parse
from typing import Optional

from neontology import BaseNode

from ..components import (
    CardComponent,
    CardListComponent,
    LinkComponent,
    NodeListTableComponent,
)
from ..components.link_data import LinkData


class NeontologyViewset(object):
    # Used to generate links (final parent becomes the root) and breadcrumbs
    parents: tuple[LinkData, ...] = (LinkData(url="/", title="Home"),)
    title: Optional[str] = None
    slug: Optional[str] = None
    order_by: Optional[str] = None
    model: Optional[type[BaseNode]] = None

    def __init__(self, model: type[BaseNode]) -> None:
        self.model = model

    def match_nodes(
        self, limit: Optional[int] = None, skip: Optional[int] = None
    ) -> list[BaseNode]:
        """Match the full set of nodes for this view."""
        if self.model is None:
            raise ValueError("Model not defined.")

        return self.model.match_nodes(limit=limit, skip=skip)

    def match_node(self, pp: str) -> Optional[BaseNode]:
        """Return a single node based on the provided primary property value."""
        if self.model is None:
            raise ValueError("Model not defined.")

        return self.model.match(pp)

    @classmethod
    def get_base_url(cls) -> str:
        base_url = None

        if cls.parents:
            base_url = cls.parents[-1].url

        if base_url is None:
            base_url = "/"

        return base_url

    def _replace_pp(self, url_pattern: str, pp: str) -> str:
        return url_pattern.replace("<pp>", urllib.parse.quote(str(pp)))

    # List Properties

    def list_url(self) -> str:
        """Return the URL for the list view."""
        url = f"{self.get_base_url()}{self.list_slug()}/"

        return url

    def list_title(self) -> str:
        if self.title:
            return self.title

        if self.model is None:
            raise ValueError("Model not defined.")

        return str(self.model.__primarylabel__)

    def list_slug(self) -> str:
        if self.slug:
            return self.slug

        return self.list_title()

    def list_subtitle(self) -> Optional[str]:
        return None

    def list_description(self) -> Optional[str]:
        return f"Find out more about {self.list_title()}"

    def list_view_name(self) -> str:
        return f"{self.__class__.__name__}-{self.model.__primarylabel__}-list"

    # Item/Node Properties

    def item_url_pattern(self) -> str:
        return f"{self.get_base_url()}{self.list_slug()}/<pp>/"

    def pp_to_url(self, pp: str) -> str:
        return self._replace_pp(self.item_url_pattern(), pp)

    def node_to_url(self, node: BaseNode) -> str:
        return self.pp_to_url(node.get_pp())

    def item_title(self, node: BaseNode) -> str:
        return str(node)

    def item_subtitle(self, node: BaseNode) -> Optional[str]:
        return self.list_title()

    def item_description(self, node: BaseNode) -> Optional[str]:
        return None

    def item_view_name(self) -> str:
        return f"{self.__class__.__name__}-{self.model.__primarylabel__}-item"

    # Endpoint Properties

    def endpoint_view_name(self, endpoint: str) -> str:
        return (
            f"{self.__class__.__name__}-{self.model.__primarylabel__}"
            f"-{endpoint}-endpoint"
        )

    def endpoint_url_pattern(self, endpoint: str) -> str:
        return self.item_url_pattern() + urllib.parse.quote(str(endpoint))

    def pp_to_endpoint_url(self, endpoint: str, pp: str) -> str:
        return self._replace_pp(self.endpoint_url_pattern(endpoint), pp)

    def node_to_endpoint_url(self, endpoint: str, node: BaseNode) -> str:
        return self.pp_to_endpoint_url(endpoint, node.get_pp())

    # Breadcrumbs

    def list_breadcrumbs(self) -> list[LinkData]:
        breadcrumbs = list(self.parents)

        breadcrumbs += [LinkData(title=self.list_title())]

        return breadcrumbs

    def item_breadcrumbs(self, node: BaseNode) -> list[LinkData]:
        breadcrumbs = list(self.parents)

        breadcrumbs += [
            LinkData(url=self.list_url(), title=self.list_title()),
            LinkData(title=str(node)),
        ]

        return breadcrumbs

    def endpoint_breadcrumbs(
        self, node: BaseNode, endpoint_name: Optional[str] = None
    ) -> list[LinkData]:
        breadcrumbs = list(self.parents)

        if endpoint_name is None:
            endpoint_name = "here"

        breadcrumbs += [
            LinkData(url=self.list_url(), title=self.list_title()),
            LinkData(title=str(node), url=self.node_to_url(node)),
            LinkData(title=endpoint_name),
        ]

        return breadcrumbs

    # Components

    def node_to_card(self, node: BaseNode) -> CardComponent:
        return CardComponent(
            title=str(node),
            subtitle=self.list_title(),
            description=self.item_description(node),
            links=[LinkComponent(url=self.node_to_url(node))],
        )

    def nodes_to_cards(self, nodes: list[BaseNode]) -> CardListComponent:
        node_cards = [self.node_to_card(x) for x in nodes]

        node_card_list = CardListComponent(children=node_cards)

        return node_card_list

    def nodes_to_table(
        self, nodes: list[BaseNode], fields: Optional[list] = None
    ) -> NodeListTableComponent:
        node_list_table = NodeListTableComponent(
            nodes=nodes, url_pattern=self.item_url_pattern(), fields=fields
        )

        return node_list_table
