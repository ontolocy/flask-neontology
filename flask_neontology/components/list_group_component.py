from typing import ClassVar, Sequence

from .component import Component
from .list_component_base import ListComponentBase
from .list_item_component import ListItemComponent


class ListGroupComponent(Component, ListComponentBase):
    template: ClassVar = """
<ul class="list-group list-group-flush">
  {% for item in data.children %}
  {{item.render() | safe}}
  {% endfor %}
</ul>
"""

    children: Sequence[ListItemComponent]
