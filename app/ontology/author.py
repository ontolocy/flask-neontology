from typing import ClassVar

from neontology import BaseNode


class NeontologyAuthorNode(BaseNode):
    __primarylabel__: ClassVar[str] = "NeontologyAuthor"
    __primaryproperty__: ClassVar[str] = "name"

    name: str

    def __str__(self) -> str:
        return self.name
