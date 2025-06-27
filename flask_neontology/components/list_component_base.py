from typing import Sequence

from pydantic import BaseModel

from .component import Component


class ListComponentBase(BaseModel):
    children: Sequence[Component]
