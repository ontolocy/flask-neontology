from typing import ClassVar, Optional

from neontology import BaseNode, BaseRelationship, related_nodes, related_property

from .author import NeontologyAuthorNode


class NeontologyPageNode(BaseNode):
    __primarylabel__: ClassVar[str] = "NeontologyPage"
    __primaryproperty__: ClassVar[str] = "slug"

    title: str
    description: Optional[str] = None
    slug: str
    content: str

    def __str__(self) -> str:
        return self.title

    @related_property
    def authors(self) -> str:
        return """
        MATCH (#ThisNode)-[:NEONTOLOGY_PAGE_AUTHORED_BY]->(a:NeontologyAuthor)
        RETURN COLLECT(a.name)
        """

    @related_nodes
    def author_nodes(self) -> str:
        return """
        MATCH (#ThisNode)-[:NEONTOLOGY_PAGE_AUTHORED_BY]->(a:NeontologyAuthor)
        RETURN a
        """


class NeontologyPageToAuthor(BaseRelationship):
    __relationshiptype__: ClassVar[str] = "NEONTOLOGY_PAGE_AUTHORED_BY"

    source: NeontologyPageNode
    target: NeontologyAuthorNode

    comments: Optional[str] = None
