from typing import ClassVar, Optional

import markdown
from markdown_link_attr_modifier import LinkAttrModifierExtension
from pydantic import Field, ValidationInfo, field_validator

from .component import Component


class MarkdownComponent(Component):
    template: ClassVar = "{{data.output_html | safe}}"

    text: str
    output_html: Optional[str] = Field(validate_default=True, default=None)

    @field_validator("output_html")
    def generate_output_html(cls, v: Optional[str], info: ValidationInfo) -> str:
        values = info.data
        raw = values["text"]

        output = markdown.markdown(
            raw,
            extensions=[
                LinkAttrModifierExtension(
                    new_tab="external_only", no_referrer="external_only"
                ),
                "tables",
            ],
        )

        return output
