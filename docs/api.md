---
LABEL: NeontologyPage
BODY_PROPERTY: content
title: API Views
slug: api
RELATIONSHIPS_OUT:
- TARGETS:
    - Ontolocy
  RELATIONSHIP_TYPE: NEONTOLOGY_PAGE_AUTHORED_BY
  TARGET_LABEL: NeontologyAuthor
---

# Creating API Views with NeontologyAPIView

Flask-Neontology provides a powerful system for building RESTful API endpoints through the `NeontologyAPIView` class. This guide shows how to create API views by subclassing `NeontologyAPIView` and registering them with the `NeontologyManager`.

This uses [SpecTree](https://github.com/0b01001001/spectree) under the hood.

## Overview

`NeontologyAPIView` is a base class that simplifies the creation of RESTful APIs for your Neontology models. It provides:

- **Automatic route generation** for list and detail endpoints
- **Built-in serialization** of your models
- **Support for related resources** (e.g., get authors of a page)
- **Automatic API documentation** via SpecTree/OpenAPI

## Basic Setup

### 1. Define an API View

Create a subclass of `NeontologyAPIView` with the required class attributes:

```python
from flask_neontology.views import NeontologyAPIView
from myapp.ontology.page import NeontologyPageNode
from myapp.ontology.author import NeontologyAuthorNode

class PageAPIView(NeontologyAPIView):
    # Required: The Neontology model this API serves
    model = NeontologyPageNode
    
    # Required: The resource name (used in URL paths)
    resource_name = "pages"
    
    # Required: Description for API documentation
    tag_description = "API endpoints for documentation pages"
    
    # Optional: Define related resources
    related_resources = {
        "authors": (NeontologyAuthorNode, "get_related_authors")
    }
    
    # Optional: Implement method to fetch related resources
    def get_related_authors(self, id: str):
        page = self.match_node(id)
        if page:
            return page.author_nodes()
        return []
```

### 2. Register API Views with NeontologyManager

Pass your API views to the `NeontologyManager` using the `api_views` parameter, organized by API version:

```python
from flask import Flask
from flask_neontology import NeontologyManager
from myapp.views.pages import PageAPIView
from myapp.views.authors import AuthorAPIView
from myapp.ontology.page import NeontologyPageNode
from myapp.ontology.author import NeontologyAuthorNode

def create_app():
    app = Flask(__name__)
    
    nm = NeontologyManager()
    
    nm.init_app(
        app=app,
        autograph_nodes=[NeontologyPageNode, NeontologyAuthorNode],
        api_views={
            "v1": [PageAPIView, AuthorAPIView],
        }
    )
    
    return app
```

### 3. Try It

You should now find the API endpoints at:

- `/api/v1/pages.json`
- `/api/v1/pages/<page id>.json`
- `/api/v1/pages/<page id>/authors.json`

Then the documentation is at:

- `/apidoc/v1/swagger/`
- `/apidoc/v1/redoc/`
- `/apidoc/v1/scalar/`

## Generated Endpoints

When you register an API view, `NeontologyManager` automatically creates the following routes:

### List Endpoint

**Route:** `GET /api/{api_ver}/{resource_name}`

Returns a list of all items.

```bash
curl http://localhost:5000/api/v1/pages
```

**Response:**

```json
[
    {
        "id": "page-1",
        "title": "Getting Started",
        "content": "..."
    },
    {
        "id": "page-2",
        "title": "Installation",
        "content": "..."
    }
]
```

### Detail Endpoint

**Route:** `GET /api/{api_ver}/{resource_name}/<id>`

Returns a single item by ID.

```bash
curl http://localhost:5000/api/v1/pages/page-1
```

**Response:**

```json
{
    "id": "page-1",
    "title": "Getting Started",
    "content": "..."
}
```

### Related Resource Endpoints

**Route:** `GET /api/{api_ver}/{resource_name}/<id>/{relationship}`

Returns related resources for a given item.

```bash
curl http://localhost:5000/api/v1/pages/page-1/authors
```

**Response:**

```json
[
    {
        "id": "author-1",
        "name": "Jane Doe",
        "email": "jane@example.com"
    }
]
```
