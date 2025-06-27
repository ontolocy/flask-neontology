import functools
from typing import Any, Callable, Optional, Union

from ..components import (
    SectionComponent,
)
from ..components.component import Component
from ..components.page_component import PageElementsEnum


def page_element(name: PageElementsEnum) -> Callable:
    def decorator_page_element(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Union[str, Component]:
            element = f(self)

            return element

        try:
            wrapper.page_element.append(name.value)  # type: ignore [attr-defined]

        except AttributeError:
            wrapper.page_element = [name.value]

        return wrapper

    return decorator_page_element


def page_section(
    title: Optional[str] = None,
    description: Optional[str] = None,
    title_level: Optional[str] = "h2",
) -> Callable:
    def decorator_page_section(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Optional[SectionComponent]:
            body = f(self)
            if body:
                section = SectionComponent(
                    title=title,
                    description=description,
                    title_level=title_level,
                    body=body,
                )
                return section
            else:
                return None

        wrapper.page_section = True  # type: ignore [attr-defined]

        return wrapper

    return decorator_page_section
