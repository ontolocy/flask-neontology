from typing import List, Optional

from pydantic import BaseModel

from .link_component import LinkComponent


class MetaData(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    links: List[LinkComponent] = []
    tags: Optional[List[str]] = None
