---
LABEL: NeontologyPage
BODY_PROPERTY: content
title: Getting Started
slug: getting-started
RELATIONSHIPS_OUT:
- TARGETS:
    - Ontolocy
  RELATIONSHIP_TYPE: NEONTOLOGY_PAGE_AUTHORED_BY
  TARGET_LABEL: NeontologyAuthor
---

# Getting Started

Flask-Neontology is a Flask extension which allows you to easily combine the Flask web framework with the Neontology Python library to simplify the development of graph driven websites with Neo4j and Pydantic.

Key features:

* 'AutoGraph' - an automatically generated interface for exploring, creating and updating nodes as well as creating relationships between them. It is available at `/autograph`
* Neontology Viewsets - lets you custom build views based on nodes returned by cypher / GQL queries.
* Components - Pydantic based bootstrap components that reduce the need for boilerplate HTML and provide Node friendly user interface elements.

## Defining an Ontology

At the heart of a Flask-Neontology website is the underlying ontology or schema for the graph which is defined with Neontology classes and used to build class based views and the built in AutoGraph.

Learn more about defining nodes and relationships with [Neontology](https://neontology.readthedocs.io/) to get started.

## Neontology Manager

The `NeontologyManager` class provides Neontology functionality to your flask application. Similar to other Flask extensions, Flask-Neontology needs to be initialized with an instance of your app.

    from flask import Flask
    from flask_neontology import NeontologyManager
    from flask_neontology.components import MarkdownComponent, PageComponent

    from .ontology.page import NeontologyPageNode
    from .views.pages import NeontologyPageView, NeontologyPageListView
    
    
    nm = NeontologyManager()

    def create_app() -> Flask:
        app = Flask(
            __name__,
        )

        nm.init_app(
          app=app,
          autograph_nodes=[NeontologyPageNode],
          views=[NeontologyPageView, NeontologyPageListView],
        )

        @app.route("/")
        def home() -> str:
          body = MarkdownComponent(text="# Hello World\n\nWelcome to my app.")

          page = PageComponent(
                  title="Flask Neontology Default Homepage",
                  sections=[body])

        return app

The example code above will initialize Neontology with an 'AutoGraph' which includes NeontologyAuthorNode, NeontologyPageNode nodes and associated relationships as well as generating the associated NeontologyViews.

NeontologyManager is then accessible from the current app at `current_app.neontology_manager`. It provides a `.get_graph()` method for obtaining a global Neontology `GraphConnection` object to run queries from anywhere in your application.

By default, neontology manager will look for default Neontology environment variables to initialize the connection to the graph. Alternatively, you can pass in a Neontology GraphEngineConfig.
