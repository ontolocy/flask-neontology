from typing import ClassVar

from .component import Component
from .link_data import LinkData


class LinkComponent(Component, LinkData):
    template: ClassVar = """
{% if data.url %}<a href="{{data.url}}"
    {% if data.classes %}class="{{data.classes | join(' ')}}"{% endif %}
    {%if data.target %} target="{{data.target}}"  rel="noopener noreferrer"{% endif %} >
{% endif %}
{{data.title}}
{% if data.url %}</a>{% endif %}
"""

    classes: list = []
