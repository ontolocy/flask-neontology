from typing import ClassVar, List

from .component import Component
from .link_component import LinkData


class BreadcrumbElement(Component):
    template: ClassVar = """
<div class="container">
  <nav aria-label="breadcrumb" class="mx-4 mt-4">
    <ol class="breadcrumb">
    {% for breadcrumb in data.breadcrumbs %}
    {% if breadcrumb.url %}
    <li class="breadcrumb-item"><a href="{{breadcrumb.url}}">{{breadcrumb.title}}</a></li>
    {% else %}
    <li class="breadcrumb-item active" aria-current="page">{{breadcrumb.title}}</li>
    {% endif %}
    {% endfor %}
    </ol>
</nav>
</div>
"""  # noqa: E501
    breadcrumbs: List[LinkData]
