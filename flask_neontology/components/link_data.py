from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class LinkData(BaseModel):
    url: Optional[str] = None
    title: str = "Link"
    target: Optional[str] = None
    domain: Optional[str] = Field(validate_default=True, default=None)

    @field_validator("domain")
    def set_domain(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        values = info.data

        if v is None and values.get("url"):
            parsed_url = urlparse(values["url"])
            if parsed_url.hostname:
                v = str(parsed_url.hostname)

        return v
