from abc import ABC
from typing import Any, Dict, List, Optional, Type

from flask import jsonify
from flask.views import MethodView
from neontology import BaseNode
from spectree import SpecTree, Tag


class NeontologyAPIView(MethodView, ABC):
    """
    Base class for API endpoints. Subclass this to create your API views.

    Required class attributes:
        - model: Pydantic model for the resource
        - resource_name: Name of the resource (e.g., 'users', 'posts')
        - tag_description: Description for API documentation grouping

    Required methods to implement:
        - get_all(): Return all items from database
        - get_by_id(pp): Return single item by ID

    Example:
        class UserAPI(APIClassView):
            model = User
            resource_name = 'users'
            tag_description = 'User management operations'

            def get_all(self):
                return db.get_all_users()

            def get_by_id(self, pp):
                return db.get_user_by_id(pp)
    """

    # Must be set by subclass
    model: Type[BaseNode] = None
    resource_name: str = None
    tag_description: str = None

    # Optional: define related resources
    # Format: {'relationship_name': (model, fetch_method_name)}
    related_resources: Dict[str, tuple] = {}

    # Will be set by Manager when registering
    _api: SpecTree = None
    _tag: Tag = None

    def match_nodes(
        self, limit: Optional[int] = None, skip: Optional[int] = None
    ) -> list[BaseNode]:
        """Match the full set of nodes for this view."""
        if self.model is None:
            raise ValueError("Model not defined.")

        return self.model.match_nodes(limit=limit, skip=skip)

    def match_node(self, pp: str) -> Optional[BaseNode]:
        """Return a single node based on the provided primary property value."""
        if self.model is None:
            raise ValueError("Model not defined.")

        return self.model.match(pp)

    @classmethod
    def validate_configuration(cls):
        """Validate that required class attributes are set"""
        if cls.model is None:
            raise ValueError(f"{cls.__name__} must define 'model' class attribute")
        if cls.resource_name is None:
            raise ValueError(
                f"{cls.__name__} must define 'resource_name' class attribute"
            )
        if cls.tag_description is None:
            raise ValueError(
                f"{cls.__name__} must define 'tag_description' class attribute"
            )

    def get_all(self) -> List[Any]:
        """
        Fetch all items from the database.

        Returns:
            List of items (will be serialized using self.model)
        """
        return self.match_nodes()

    def get_by_id(self, pp: Any) -> Optional[Any]:
        """
        Fetch a single item by ID from the database.

        Args:
            pp: The ID of the item to fetch

        Returns:
            Single item or None if not found
        """
        return self.match_node(pp)

    def get_related(self, pp: Any, relationship: str) -> List[Any]:
        """
        Fetch related items for a given ID and relationship.
        Override this or define specific methods like get_related_<relationship>

        Args:
            pp: The ID of the parent item
            relationship: Name of the relationship (e.g., 'ip_addresses')

        Returns:
            List of related items
        """
        # Check if there's a specific method for this relationship
        method_name = f"get_related_{relationship.replace('-', '_')}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(pp)

        raise NotImplementedError(
            f"Related resource '{relationship}' not implemented. "
            f"Define '{method_name}(self, pp)' method or override get_related()"
        )

    def serialize_item(self, item: BaseNode) -> dict:
        """
        Serialize a single item. Override if custom serialization needed.

        Args:
            item: Raw item from database

        Returns:
            Dictionary representation
        """

        return item.model_dump()

    def get(self, pp: Optional[Any] = None, relationship: Optional[str] = None):
        """
        Handle GET requests for list, detail, or related resource views.
        This method is automatically decorated by the Manager.
        """
        if pp is not None:
            if relationship is not None:
                # Related resource view (e.g., /api/users/1/posts)
                parent_item = self.get_by_id(pp)
                if parent_item is None:
                    return {
                        "error": f"{self.resource_name[:-1].title()} not found"
                    }, 404

                related_items = self.get_related(pp, relationship)

                return (
                    jsonify([self.serialize_item(item) for item in related_items]),
                    200,
                )
            else:
                # Detail view
                item = self.get_by_id(pp)
                if item is None:
                    return {
                        "error": f"{self.resource_name[:-1].title()} not found"
                    }, 404
                return jsonify(self.serialize_item(item)), 200
        else:
            # List view
            items = self.get_all()
            return jsonify([self.serialize_item(item) for item in items]), 200

    @classmethod
    def get_list_endpoint(cls, api_ver: str) -> str:
        """Get the URL pattern for the list endpoint"""
        return f"/api/{api_ver}/{cls.resource_name}.json"

    @classmethod
    def get_detail_endpoint(cls, api_ver: str) -> str:
        """Get the URL pattern for the detail endpoint"""
        return f"/api/{api_ver}/{cls.resource_name}/<pp>.json"

    @classmethod
    def get_related_endpoint(cls, relationship: str, api_ver: str) -> str:
        """Get the URL pattern for a related resource endpoint"""
        return f"/api/{api_ver}/{cls.resource_name}/<pp>/{relationship}.json"
