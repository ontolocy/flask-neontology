from typing import ClassVar, Optional

from .component import Component
from .list_component_base import ListComponentBase


class FeaturePanelComponent(ListComponentBase, Component):
    template: ClassVar = """
<div class="container px-4 py-5">
{% if data.title is not none %}
<{{data.title_level}} class="pb-2 border-bottom">{{data.title}}</{{data.title_level}}>
{% endif %}
{% if data.subtitle is not none or data.body is not none %}
    <div class="row row-cols-1 row-cols-md-2 align-items-md-center g-3 py-3">
    {% else %}
    <div class="row align-items-md-center g-3 py-3">
    {% endif %}
        {% if data.subtitle is not none or data.body is not none %}
        <div class="col d-flex flex-column align-items-start gap-2">
            {% if data.subtitle is not none or data.body is not none %}
            <{{data.subtitle_level}} class="fw-bold">{{data.subtitle}}</{{data.subtitle_level}}>
            {% endif %}
            {% if data.subtitle is not none or data.body is not none %}
            <p class="text-body-secondary">{{data.body}}</p>
            {% endif %}
        </div>
        {% endif %}
        <div class="col">
            <div class="row row-cols-1 row-cols-sm-{% if data.subtitle is not none or data.body is not none %}2{% else %}3{% endif %} g-4">
                {%- for item in data.children %}
                {{item.render() | safe}}
                {% endfor %}
            </div>
        </div>
    </div>
</div>
"""  # noqa: E501

    title: Optional[str] = None
    title_level: str = "h2"
    subtitle: Optional[str] = None
    subtitle_level: str = "h3"
    body: Optional[str] = None
