from typing import ClassVar, List, Optional, Union

from pydantic import field_validator, model_validator

from .component import Component
from .text_component import TextComponent


class SectionHeadComponent(Component):
    template: ClassVar = """
{% if data.title %}
<{{data.title_level}}>{{data.title}}</{{data.title_level}}>
{% endif %}
{% if data.description %}
{{data.description.render() | safe}}
{% endif %}
"""

    title: Optional[str] = None
    description: Optional[Union[str, Component]] = None
    title_level: Optional[str] = "h2"

    @field_validator("description")
    def generate_description_component(cls, v: Union[Component, str]) -> Component:
        if isinstance(v, str):
            v = TextComponent(text=v)

        return v


class SectionComponent(SectionHeadComponent):
    template: ClassVar = """
    <div class="container pt-2 px-4">
    {% if data.title %}
        <{{data.title_level}}>{{data.title}}</{{data.title_level}}>
    {% endif %}
    {% if data.description %}
        {{data.description.render() | safe}}
    {% endif %}
    {% if data.body %}
    <div class="pb-3">
        {% for section in data.body %}
            {{ section.render() | safe }}
        {% endfor %}
    </div>
    {% endif %}
    </div>
"""

    body: Optional[Union[Component, List[Component]]]

    @field_validator("body")
    def convert_body(
        cls, v: Optional[Union[Component, List[Component]]]
    ) -> Optional[List[Component]]:
        if isinstance(v, list):
            return v
        elif v is not None:
            return [v]
        else:
            return None

    @model_validator(mode="after")
    def extract_scripts(self) -> "SectionComponent":
        if self.body:
            for component in self.body:
                if isinstance(component, Component):
                    self.headtags += component.headtags
                    self.tailtags += component.tailtags

        return self
