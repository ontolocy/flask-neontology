from typing import ClassVar, List

from .component import Component
from .link_data import LinkData


class HeroComponent(Component):
    template: ClassVar = """
<div class="px-4 py-4 my-3 text-center">
    <h{{data.title_level}} class="display-5 fw-bold text-body-emphasis">{{data.title}}</{{data.title_level}}>
    <div class="col-lg-6 mx-auto">
        <p class="lead mb-2">{{data.body}}</p>
    </div>
    {% if data.links %}
    <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
        {% for link in data.links %}
        <button type="button" class="btn btn-primary btn-lg px-4 gap-3" href="{{link.url}}">{{link.title}}</button>
        {% endfor %}
    </div>
    {% endif %}
</div>
"""  # noqa: E501

    title: str
    title_level: str = "h1"
    body: str
    links: List[LinkData] = []
