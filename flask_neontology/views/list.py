from typing import Optional

from neontology import BaseNode

from .baseview import NeontologyView


class NeontologyListView(NeontologyView):
    @classmethod
    def view_name(cls, model: Optional[type[BaseNode]] = None) -> str:
        if model:
            viewset = cls.viewset_handler(model)
        elif cls.viewset_handler.model is not None:
            viewset = cls.viewset_handler(cls.viewset_handler.model)
        else:
            raise ValueError("Viewset Handler Model Not Defined")
        return viewset.list_view_name()

    @classmethod
    def view_url_rule(cls, model: Optional[type[BaseNode]] = None) -> str:
        if model:
            viewset = cls.viewset_handler(model)
        elif cls.viewset_handler.model is not None:
            viewset = cls.viewset_handler(cls.viewset_handler.model)
        else:
            raise ValueError("Viewset Handler Model Not Defined")
        return viewset.list_url()
