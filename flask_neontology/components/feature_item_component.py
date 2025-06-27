from typing import ClassVar, Optional

from .component import Component
from .link_component import LinkComponent


class FeatureItemComponent(Component):
    template: ClassVar = """
<div class="col d-flex flex-column gap-2">
    <{{data.title_level}} class="fw-semibold mb-0">{{data.title}}</{{data.title_level}}>
    {%- if data.body is not none %}
    <p class="text-body-secondary">{{data.body}}</p>
    {%- endif -%}
    {%- if data.link %}
    {{data.link.render() | safe}}
    {%- endif -%}
</div>
"""

    title: str
    title_level: str = "h4"
    body: Optional[str] = None
    link: Optional[LinkComponent] = None
