from typing import ClassVar

from .component import Component


class TextComponent(Component):
    template: ClassVar = "<{{data.tag}}>{{data.text}}</{{data.tag}}>"

    text: str
    tag: str = "p"
