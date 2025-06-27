from typing import ClassVar

from .component import Component


class HTMLComponent(Component):
    template: ClassVar = "{{data.raw_html | safe}}"

    raw_html: str
