---
LABEL: NeontologyPage
BODY_PROPERTY: content
title: Views
slug: views
RELATIONSHIPS_OUT:
- TARGETS:
    - Ontolocy
  RELATIONSHIP_TYPE: NEONTOLOGY_PAGE_AUTHORED_BY
  TARGET_LABEL: NeontologyAuthor
---

# Using Neontology Viewsets and Class-Based Views

Flask Neontology provides a flexible, class-based approach for building list and detail pages for your data models.

**Viewsets** - encapsulate model logic and URL patterns
**Class-Based Views** - handle HTTP requests and rendering

## Core Concepts

### 1. Viewset

A **Viewset** encapsulates logic for a particular model, including:

- How to query/match nodes
- How to generate URLs and breadcrumbs
- How to convert nodes to components

**Example:**

    from flask_neontology.views import NeontologyViewset
    from myapp.ontology.page import NeontologyPageNode

    class NeontologyPageViewset(NeontologyViewset):
        model: type[NeontologyPageNode] = NeontologyPageNode

        def list_title(self) -> str:
            return "pages"

By default, viewsets will match all nodes based on the defined model. Alternatively, you gan define custom `match_nodes` and `match_node` methods.

### 2. Class-Based Views

Neontology provides several base classes for views:

- `NeontologyListView`: For list pages (collections)
- `NeontologyNodeView`: For detail pages (single node)
- `NeontologyEndpointView`: For custom endpoints (create, update, etc.)

These classes inherit from Flask's standard [Class-based MethodView](https://flask.palletsprojects.com/en/stable/views/).

To build out views, you subclass these and connect them to your viewset.

`@page_element` and `@page_section` decorators are used to decorate methods which return Components to construct the final HTML view.

**Example:**

    from flask_neontology.views import NeontologyListView, NeontologyNodeView
    from flask_neontology.components import CardListComponent, TextComponent, MarkdownComponent
    from flask_neontology.components.breadcrumb_element import BreadcrumbElement
    from flask_neontology.components.page_component import PageElementsEnum, page_element, page_section

    class NeontologyPageListView(NeontologyListView):
        viewset_handler = NeontologyPageViewset

        @page_element(PageElementsEnum.TITLE)
        def page_title(self) -> str:
            return "Pages"

        @page_element(PageElementsEnum.BREADCRUMBS)
        def list_breadcrumbs(self) -> BreadcrumbElement:
            return BreadcrumbElement(breadcrumbs=self.viewset.list_breadcrumbs())

        @page_section(title=None)
        def pages(self) -> CardListComponent:
            nodes = self.viewset.match_nodes()
            return self.viewset.nodes_to_cards(nodes)

    class NeontologyPageView(NeontologyNodeView):
        viewset_handler = NeontologyPageViewset

        @page_element(PageElementsEnum.TITLE)
        def page_title(self) -> str:
            return self.node.title

        @page_section(title="Page Authors")
        def page_author(self) -> Optional[TextComponent]:

            if self.node.authors():
                authors = "Author(s): " + ", ".join(self.node.authors())
                return TextComponent(text=authors)

        @page_section(title=None)
        def page_content(self) -> MarkdownComponent:

            md = MarkdownComponent(text=self.node.content)
            return md

## Key Page Element Decorators

- `@page_element(PageElementsEnum.TITLE)`: Defines the page title.
- `@page_element(PageElementsEnum.BREADCRUMBS)`: Defines breadcrumbs.

## Customizing Viewsets

You can override methods in your viewset to customize:

- URL patterns
- Breadcrumbs
- How nodes are converted to components (e.g., cards, tables)

**Example:**

    class MyCustomViewset(NeontologyViewset):
        def nodes_to_cards(self, nodes):
            # Custom logic to convert nodes to CardComponents
            ...
