from typing import ClassVar, List

from pydantic import field_validator

from .component import Component
from .link_component import LinkComponent
from .meta_data import MetaData


class CardComponent(Component, MetaData):
    template: ClassVar = """
<div class="card h-100">
    {% if data.subtitle %}
    <div class="card-header">{{data.subtitle}}</div>
    {% endif %}
    <div class="card-body">
        <h3 class="card-title h5">{{data.title}}</h3>
        {% if data.description %}
        <p class="card-text">{{data.description}}</p>
        {% endif %}
    </div>
    {% if data.links %}
    <div class="card-footer">
    {% for link in data.links %}
    {{link.render() | safe}}
    {% endfor %}
    </div>
    {% endif %}
</div>
"""

    @field_validator("links")
    def set_link_class(cls, v: List[LinkComponent]) -> List[LinkComponent]:
        for link in v:
            link.classes.append("btn btn-secondary")
        return v
