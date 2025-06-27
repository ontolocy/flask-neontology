import inspect
from typing import Callable, Dict, Optional, Type, Union

from flask.views import MethodView
from neontology import BaseNode

from ..components import (
    SectionComponent,
)
from ..components.component import Component
from ..components.page_component import PageComponent
from .viewset import NeontologyViewset


class NeontologyView(MethodView):
    viewset_handler: type[NeontologyViewset]

    title = None

    def __init__(self, model: Optional[Type[BaseNode]] = None):
        if self.viewset_handler.model:
            self.model = self.viewset_handler.model
        elif model is not None:
            self.model = model

        else:
            raise ValueError("Model not defined.")

        self.viewset = self.viewset_handler(self.model)

    @classmethod
    def get_viewset(cls, model: Optional[Type[BaseNode]] = None) -> NeontologyViewset:
        """
        Returns the viewset handler for the given model or
            the default model defined in the viewset handler.

        Args:
            model (Optional[Type[BaseNode]]): The model to get the viewset for.

        Returns:
            Viewset: The viewset handler for the model.
        """
        if model:
            return cls.viewset_handler(model)
        elif cls.viewset_handler.model is not None:
            return cls.viewset_handler(cls.viewset_handler.model)
        else:
            raise ValueError("Viewset Model Not Defined")

    @classmethod
    def collect_decorated_methods(cls, attribute_name: str) -> Dict[str, Callable]:
        """
        Collects all methods that have a specific attribute
         from this class and its base classes.

        Args:
            attribute_name (str): The attribute to look for on methods

        Returns:
            dict: Dictionary mapping method names to their corresponding
                     method objects
        """
        decorated_methods = {}

        # Get all classes in the inheritance hierarchy in method resolution order
        classes = cls.__mro__

        # Inspect each class in reverse order (base classes first)
        for class_ in reversed(classes):
            for name, member in class_.__dict__.items():
                if inspect.isfunction(member) and hasattr(member, attribute_name):
                    decorated_methods[name] = member

        return decorated_methods

    def get_sections(self) -> list[SectionComponent]:
        sections = self.collect_decorated_methods("page_section")

        return [
            section(self) for section in sections.values() if section(self) is not None
        ]

    def get_elements(self) -> Dict[str, Union[Component, str]]:
        elements = self.collect_decorated_methods("page_element")

        new_elements = {}

        for method in elements.values():
            if hasattr(method, "page_element"):
                for element_name in method.page_element:
                    new_elements[element_name] = method(self)

        return new_elements

    def get(self) -> str:
        sections = self.get_sections()
        elements = self.get_elements()

        page = PageComponent(title=self.title, elements=elements, sections=sections)

        return page.render()
