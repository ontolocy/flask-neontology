---
LABEL: NeontologyPage
BODY_PROPERTY: content
title: Components
slug: components
RELATIONSHIPS_OUT:
- TARGETS:
    - Ontolocy
  RELATIONSHIP_TYPE: NEONTOLOGY_PAGE_AUTHORED_BY
  TARGET_LABEL: NeontologyAuthor
---

# Components

Flask Neontology provides a flexible, component-based system for building dynamic, data-driven web pages. Components are Python classes (often Pydantic models) that encapsulate both data and rendering logic, making it easy to compose complex UIs from reusable building blocks.

## Core Concepts

### 1. Component

Components are the base class for all Flask-Neontology UI elements.

Call `.render()` on any component to get its HTML. This uses the component’s Jinja2 template and its data.

The template class variable defines the Jinja template used to render the component.

Components can be nested and composed to build complex layouts. For example, a `PageComponent` can contain multiple `SectionComponent` objects, each with their own cards, tables, or lists.

**Example:**

    from flask_neontology.components import Component

    class MyComponent(Component):
        template: ClassVar = "<div>{{data.text}}</div>"
        text: str

    comp = MyComponent(text="Hello!")
    html = comp.render()

### 2. MetaData

- Used for page and card metadata (title, subtitle, description, links, tags).
- Often passed to higher-level components like `PageComponent` or `CardComponent`.

**Example:**

    from flask_neontology.components import MetaData

    meta = MetaData(
        title="My Page",
        subtitle="Welcome!",
        description="This is a demo.",
        tags=["demo", "flask"]
    )

### 3. SectionComponent

- Represents a logical section of a page.
- Can include a title, description, and a body (which can be a single component or a list of components).

**Example:**

    from flask_neontology.components import SectionComponent, TextComponent

    section = SectionComponent(
        title="Introduction",
        body=TextComponent(text="Welcome to the introduction section.")
    )

### 4. PageComponent

- The top-level component for rendering a full page.
- Accepts metadata, a list of sections, and optional elements (breadcrumbs, footer, etc.).

**Example:**

    from flask_neontology.components import PageComponent, MetaData, SectionComponent, TextComponent

    page = PageComponent(
        title="Demo Page",
        description="A demonstration of Flask Neontology components.",
        sections=[
            SectionComponent(
                title="Section 1",
                body=TextComponent(text="This is section 1.")
            )
        ]
    )
    html = page.render()

## Individual Components

### 5. CardComponent & CardListComponent

- `CardComponent` displays a single card with title, subtitle, description, and links.
- `CardListComponent` displays a grid/list of cards.

**Example:**

    from flask_neontology.components import CardComponent, CardListComponent
    card1 = CardComponent(title="Card 1", subtitle="Sub 1", description="Desc 1")
    card2 = CardComponent(title="Card 2", subtitle="Sub 2", description="Desc 2")
    card_list = CardListComponent(children=[card1, card2])

### 6. TableComponent

- Renders tabular data.
- Requires columns (as `ColumnData`) and rows (as dicts).

**Example:**

    from flask_neontology.components import TableComponent, ColumnData

    columns = [ColumnData(title="User Name", result_field="name")]
    rows = [{"name": "Alice"}, {"name": "Bob"}]
    table = TableComponent(columns=columns, rows=rows)

### 7. ListGroupComponent & ListItemComponent

- For Bootstrap-style list groups.
- `ListGroupComponent` holds multiple `ListItemComponent` objects.

**Example:**

    from flask_neontology.components import   ListGroupComponent, ListItemComponent
    item1 = ListItemComponent(title="Item 1", description="Desc 1")
    item2 = ListItemComponent(title="Item 2", description="Desc 2")
    list_group = ListGroupComponent(children=[item1, item2])

### 8. Form Components

- `ModelFormComponent` and `RelationshipFormComponent` generate forms for nodes and relationships.
- They handle validation and conversion from form data to model instances.

**Example:**

    from flask_neontology.components import ModelFormComponent

    form = ModelFormComponent(model=MyNodeClass)
    if form.form_validate(request.form):
        node = form.form_to_model(request.form)

### 9. Custom Components

- You can create your own by subclassing `Component` and defining a `template` and fields.

**Example:**

    class AlertComponent(Component):
        template: ClassVar = '<div class="alert alert-{{data.level}}">{{data.message}}</div>'
        level: str = "info"
        message: str
