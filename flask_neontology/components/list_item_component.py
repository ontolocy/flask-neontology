from typing import ClassVar, List

from pydantic import field_validator

from .component import Component
from .link_component import LinkComponent
from .meta_data import MetaData


class ListItemComponent(Component, MetaData):
    template: ClassVar = """
{% if data.links|length == 1 %}
<a href="{{data.links[0].url}} "
{% if data.links[0].target %}
target="{{data.links[0].target}}" rel="noopener noreferrer"
{% endif %}
class="list-group-item list-group-item-action d-flex justify-content-between align-items-start">
{% else %}
<li class="list-group-item d-flex justify-content-between align-items-start">
{% endif %}
    <div class="ms-2 me-auto">
        <h5>{{data.title}}</h5>
        {% if data.subtitle %}
        <h6>{{data.subtitle}}</h6>
        {% endif %}
        {% if data.description %}
        {{data.description}}
        {% endif %}
        {% if data.links|length > 1 %}
        {% for link in data.links %}
        {{link.render() | safe}}
        {% endfor %}
        {% endif %}
    </div>
    {% if data.tags %}
    {% for tag in data.tags %}
    <span class="badge text-bg-secondary py-1 mx-1">{{tag}}</span>
    {% endfor %}
    {% endif %}
{% if data.links|length == 1 %}
</a>
{% else %}
</li>
{% endif %}
"""  # noqa: E501

    @field_validator("links")
    def set_link_class(cls, v: List[LinkComponent]) -> List[LinkComponent]:
        for link in v:
            link.classes.append("btn btn-secondary")
        return v
