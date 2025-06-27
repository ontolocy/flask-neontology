from typing import Optional, Type

from neontology import BaseNode

from .node import NeontologyNodeView


class NeontologyEndpointView(NeontologyNodeView):
    endpoint: Optional[str] = None

    @classmethod
    def view_name(cls, model: Optional[Type[BaseNode]] = None) -> str:
        if model:
            viewset = cls.viewset_handler(model)
        elif cls.viewset_handler.model is not None:
            viewset = cls.viewset_handler(cls.viewset_handler.model)
        else:
            raise ValueError("Viewset Handler Model Not Defined")

        if cls.endpoint is None:
            raise ValueError(
                "Endpoint name (endpoint) is not defined for NeontologyEndpointView."
            )

        return viewset.endpoint_view_name(cls.endpoint)

    @classmethod
    def view_url_rule(cls, model: Optional[Type[BaseNode]] = None) -> str:
        if model:
            viewset = cls.viewset_handler(model)
        elif cls.viewset_handler.model is not None:
            viewset = cls.viewset_handler(cls.viewset_handler.model)
        else:
            raise ValueError("Viewset Handler Model Not Defined")

        if cls.endpoint is None:
            raise ValueError(
                "Endpoint name (endpoint) is not defined for NeontologyEndpointView."
            )

        return viewset.endpoint_url_pattern(cls.endpoint)
