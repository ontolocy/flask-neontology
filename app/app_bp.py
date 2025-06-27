from flask import Blueprint, current_app, url_for
from neontology import GraphConnection

from flask_neontology.components import (
    CardComponent,
    CardListComponent,
    ColumnData,
    CytoscapeComponent,
    Graph2dComponent,
    Graph3dComponent,
    HeroComponent,
    LinkComponent,
    LinkData,
    ListGroupComponent,
    ListItemComponent,
    MarkdownComponent,
    PageComponent,
    PageElements,
    SectionComponent,
    SideMenuElement,
    SideMenuItem,
    TableComponent,
    TextComponent,
)

from .views.pages import (
    NeontologyPageListView,
)

bp = Blueprint(
    "app_bp",
    __name__,
)


@bp.route("/")
def home() -> str:
    hero = HeroComponent(
        title="Flask Neontology",
        body=(
            "Welcome to the demonstration app for Flask-Neontology - "
            "a Flask extension for building web applications with Neo4j."
        ),
    )

    cards = [
        CardComponent(
            title="Component Catalogue",
            description="See what components are available for building out your site.",
            links=[LinkComponent(url=url_for("app_bp.components_catalogue"))],
        ),
        CardComponent(
            title="Documentation",
            description="Explore the docs, built with an example viewset",
            links=[LinkComponent(url=url_for(NeontologyPageListView.view_name()))],
        ),
    ]

    if current_app.config["APP_ENV"] != "FREEZE":
        cards.append(
            CardComponent(
                title="Create Page",
                description="Experiment with adding a new page node to the graph.",
                links=[LinkComponent(url=url_for("extra_bp.create_page"))],
            )
        )

    card_list = CardListComponent(children=cards)

    card_section = SectionComponent(title="Explore Flask Neontology", body=card_list)

    gc = GraphConnection()
    results = gc.evaluate_query("MATCH (n)-[r]->(o) RETURN n,r,o LIMIT 25")

    graph_view = Graph3dComponent(results=results)
    graph_section = SectionComponent(
        title="Graph View",
        description="A 3D view of the nodes and relationships in the graph.",
        body=graph_view,
    )

    page = PageComponent(
        title="Flask Neontology Demo Homepage",
        description="This home page comes with the Flask Neontology demo app.",
        sections=[hero, card_section, graph_section],
    )
    return page.render()


# a simple page that shows off our components
@bp.route("/components/")
def components_catalogue() -> str:
    table_entries = [
        {
            "name": "Robert Burns",
            "location": "Ayrshire",
            "profession": "Poet",
            "wikipedia_page": LinkComponent(
                url="https://en.wikipedia.org/wiki/Robert_Burns"
            ),
        },
        {
            "name": "William Shakespeare",
            "location": "Stratford-upon-Avon",
            "profession": "Playwright",
            "wikipedia_page": LinkComponent(
                url="https://en.wikipedia.org/wiki/William_Shakespeare"
            ),
        },
        {
            "name": "Charlotte Brontë",
            "location": "Haworth",
            "profession": "Author",
            "wikipedia_page": LinkComponent(
                url="https://en.wikipedia.org/wiki/Charlotte_Bront%C3%AB"
            ),
        },
        {
            "name": "Christopher Marlowe",
            "location": "Canterbury",
            "profession": "Playwright, Poet and Translator",
            "wikipedia_page": LinkComponent(
                url="https://en.wikipedia.org/wiki/Christopher_Marlowe"
            ),
        },
    ]

    hero_component = HeroComponent(
        title="Component Catalogue",
        body=(
            "Welcome to the component catalogue. "
            "This page demonstrates different types of component. "
            "This is the Hero Component!"
        ),
    )

    text = TextComponent(text="This is just some standard body text.")

    markdown = MarkdownComponent(
        text="""### Markdown Component
The markdown component turns raw markdown into HTML.

    # code example

And bullets:

- Foo
- Bar

"""
    )

    gc = GraphConnection()

    results = gc.evaluate_query("MATCH (n)-[r]->(o) RETURN n,r,o LIMIT 25")

    cytoscape_graph = CytoscapeComponent(results=results)
    cytoscape_section = SectionComponent(
        title="Cytoscape Network Graph",
        description="Can take results directly from a neontology query.",
        body=cytoscape_graph,
    )

    graph2d = Graph2dComponent(results=results)
    graph2d_section = SectionComponent(
        title="2D Force Graph",
        description="Can take results directly from a neontology query.",
        body=graph2d,
    )

    graph3d = Graph3dComponent(results=results)
    graph3d_section = SectionComponent(
        title="3D Force Graph",
        description="Can take results directly from a neontology query.",
        body=graph3d,
    )

    text_section = SectionComponent(title="TextComponent", body=text)

    cards = [
        CardComponent(
            title=x["name"],
            subtitle=x["profession"],
            description=f"{x['name']} is associated with the area of {x['location']}.",
            links=[
                x["wikipedia_page"],
                LinkComponent(url="https://google.com/maps", title="Map"),
            ],
        )
        for x in table_entries
    ]
    card_list = CardListComponent(children=cards)
    card_section = SectionComponent(
        title="CardComponent",
        body=card_list,
    )

    list_items = [
        ListItemComponent(
            title=x["name"], subtitle=x["profession"], description=x["location"]
        )
        for x in table_entries
    ]
    list_group = ListGroupComponent(children=list_items)
    list_group_section = SectionComponent(
        title="ListItemComponent",
        body=list_group,
    )

    table_columns = [
        ColumnData(title="Name", result_field="name"),
        ColumnData(title="Location", result_field="location"),
        ColumnData(title="Vocation", result_field="profession"),
    ]

    table = TableComponent(columns=table_columns, rows=table_entries)

    table_section = SectionComponent(title="TableComponent", body=table)

    datatable = TableComponent(
        columns=table_columns, rows=table_entries, datatable=True
    )

    datatable_section = SectionComponent(
        title="TableComponent with DataTables", body=datatable
    )

    sidebar = SideMenuElement(
        items=[
            SideMenuItem(
                parent_link=LinkData(
                    title="Side Link 1",
                    url="#1",
                ),
                parent_icon="bi-check-square",
            ),
            SideMenuItem(
                parent_link=LinkData(title="Side Link 2", url="#2"),
                parent_icon="bi-diagram-3",
            ),
            SideMenuItem(
                parent_link=LinkData(title="Side Link 3", url="#3"),
                parent_icon="bi-diagram-3",
                child_links=[
                    LinkData(title="Child Link 1", url="#3.1"),
                    LinkData(title="Child Link 2", url="#3.2"),
                ],
            ),
        ]
    )

    elements = PageElements(leftbar=sidebar, footer_text="Footer Element Content")

    page = PageComponent(
        elements=elements,
        title="Flask Neontology Component Catalogue",
        description="Explore the different components available.",
        sections=[
            hero_component,
            text_section,
            markdown,
            graph2d_section,
            graph3d_section,
            cytoscape_section,
            card_section,
            list_group_section,
            table_section,
            datatable_section,
        ],
    )
    return page.render()
