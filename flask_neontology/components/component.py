from typing import ClassVar, List

from flask import render_template_string
from pydantic import BaseModel, ConfigDict


class Component(BaseModel):
    template: ClassVar = ""

    headtags: List[str] = []
    tailtags: List[str] = []

    model_config = ConfigDict(extra="forbid")

    def render(self) -> str:
        return render_template_string(self.template, data=self)
