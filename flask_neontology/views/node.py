from typing import Optional, Type

from neontology import BaseNode

from ..components.page_component import PageComponent
from .baseview import NeontologyView


class NeontologyNodeView(NeontologyView):
    def __init__(self, model: Optional[Type[BaseNode]] = None):
        if self.viewset_handler.model:
            self.model = self.viewset_handler.model
        elif model is not None:
            self.model = model
        else:
            raise ValueError("Model not defined.")

        self.viewset = self.viewset_handler(self.model)
        self.node = None

    def get(self, pp: str) -> str:  # type: ignore [override]
        if self.model is None:
            raise ValueError("NeontologyNodeView model not provided.")

        self.node = self.model.match(pp)

        sections = self.get_sections()
        elements = self.get_elements()

        title = self.viewset_handler(self.model).item_title(self.node)

        page = PageComponent(title=title, elements=elements, sections=sections)

        return page.render()

    @classmethod
    def view_name(cls) -> str:
        return cls.get_viewset().item_view_name()

    @classmethod
    def view_url_rule(cls) -> str:
        return cls.get_viewset().item_url_pattern()
