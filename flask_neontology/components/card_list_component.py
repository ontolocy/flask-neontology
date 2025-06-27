from typing import ClassVar, Sequence

from .card_component import CardComponent
from .component import Component
from .list_component_base import ListComponentBase


class CardListComponent(Component, ListComponentBase):
    template: ClassVar = """
  <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-4 g-4 pt-3">
  {% for card in data.children %}
  <div class="col">
  {{card.render() | safe}}
  </div>
  {% endfor %}
  </div>
"""

    children: Sequence[CardComponent]
