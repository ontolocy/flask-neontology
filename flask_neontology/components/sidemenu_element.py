from typing import ClassVar, List, Optional

from pydantic import BaseModel

from .component import Component
from .link_component import LinkData


class SideMenuItem(BaseModel):
    parent_link: LinkData
    parent_icon: Optional[str] = None
    child_links: Optional[List[LinkData]] = None


class SideMenuElement(Component):
    template: ClassVar = """
<div class="{% if data.fixed is true %}position-fixed{% endif %} bg-body-tertiary text-body p-0 shadow" style="width: 180px;">
    <div class="d-flex flex-column align-items-stretch px-0 pt-3 min-vh-100">
        <ul class="nav nav-pills flex-column mb-0 gap-1" id="menu">
        {% for item in data.items %}
        <li class="nav-item w-100">
            <a href="{{item.parent_link.url}}" class="nav-link text-body-emphasis d-flex align-items-center px-3 py-2 rounded-2">
                {% if item.parent_icon is not none %}
                  <i class="fs-6 align-middle me-2 {{item.parent_icon}}"></i>
                {% endif %}
                <span>{{item.parent_link.title}}</span>
            </a>
            {% if item.child_links is not none %}
            <ul class="nav flex-column ms-3 bg-body-secondary rounded-start py-2 border-0 border-start" >
                {% for subitem in item.child_links %}
                <li>
                    <a href="{{subitem.url}}" class="nav-link text-body small px-2 py-1 rounded-1 d-block">
                        {{subitem.title}}
                    </a>
                </li>
                {% endfor %}
            </ul>
            {% endif %}
        </li>
        {% endfor %}
        </ul>
    </div>
</div>
<div class="col overflow-auto py-5 px-2" {% if data.fixed is true %}style="margin-left: 180px;"{% endif %}>
"""  # noqa: E501

    items: List[SideMenuItem]
    fixed: bool = False
