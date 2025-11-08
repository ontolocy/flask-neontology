from enum import Enum
from typing import ClassVar, List, Optional, Union

from pydantic import BaseModel, field_validator, model_validator

from .component import Component
from .section_component import SectionComponent


class PageElementsEnum(Enum):
    BREADCRUMBS = "breadcrumbs"
    TITLE = "title"
    DESCRIPTION = "description"
    FOOTER_TEXT = "footertext"
    LEFTBAR = "leftbar"
    H1 = "h1"


class PageElements(BaseModel):
    breadcrumbs: Optional[Component] = None
    title: Optional[str] = None
    description: Optional[str] = None
    footer_text: Optional[str] = None
    leftbar: Optional[Component] = None
    h1: Optional[str] = None


class PageComponent(Component):
    template: ClassVar = """
{% extends 'neontology_base.html' %}
{% block title %}
{% if data.elements.title %}
{{data.elements.title}}
{% elif data.title %}
{{data.title}}
{%- endif %}
{% endblock %}
{% block metas %}
{% if data.description %}
<meta name="description" content="{{data.description}}">
{% elif data.elements.description %}
<meta name="description" content="{{data.elements.description}}">
{% endif %}
{% endblock %}
{% if data.headtags %}
{% block headtags %}
{% for headtag in data.headtags %}
{{headtag | safe}}
{% endfor %}
{% endblock headtags %}
{% endif %}

{% block stickytop %}
{% if data.sticky_topnav %}sticky-top{% endif %}{% endblock %}

{% block leftbar %}
{% if data.elements.leftbar is not none  %}
{{ data.elements.leftbar.render() | safe }}
{% else %}
<div class="col overflow-auto py-5 px-2">
{% endif %}
{% endblock leftbar %}

{% block content %}
{% if data.elements.h1 is not none %}
<div class="container px-4 pt-4">
<h1>{{data.elements.h1}}</h1>
</div>
{% endif %}
{% if data.elements.breadcrumbs is not none  %}
{{ data.elements.breadcrumbs.render() | safe }}
{% endif %}
{% for section in data.sections %}
{{section.render() | safe}}
{% endfor %}
{% endblock content %}


{% block footer %}
{% if data.elements.footer_text %}
<footer class="footer mt-auto py-3 bg-body-tertiary text-center w-100">
    <div class="container">
      <span class="text-muted">{{data.elements.footer_text}}</span>
    </div>
</footer>
{% endif %}
{% endblock footer %}


{% if data.tailtags %}
{% block tailtags %}
{% for tailtag in data.tailtags %}
{{tailtag | safe}}
{% endfor %}
{% endblock tailtags %}
{% endif %}
"""
    title: Optional[str] = None
    description: Optional[str] = None
    sticky_topnav: bool = False
    sections: List[Union[SectionComponent, Component]] = []
    elements: PageElements = PageElements()

    @field_validator("sections", mode="before")
    @classmethod
    def component_to_section(cls, value: list) -> list:
        sections = []
        for entry in value:
            if isinstance(entry, SectionComponent):
                sections.append(entry)
            else:
                sections.append(SectionComponent(body=[entry]))
        return sections

    @model_validator(mode="after")
    def extract_scripts(self) -> "PageComponent":
        all_headtags = []
        all_tailtags = []

        for section in self.sections:
            all_headtags += section.headtags
            all_tailtags += section.tailtags

        for headtag in all_headtags:
            if headtag not in self.headtags:
                self.headtags.append(headtag)

        for tailtag in all_tailtags:
            if tailtag not in self.tailtags:
                self.tailtags.append(tailtag)

        return self
