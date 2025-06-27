---
LABEL: NeontologyPage
BODY_PROPERTY: content
title: Commands
slug: commands
RELATIONSHIPS_OUT:
- TARGETS:
    - Ontolocy
  RELATIONSHIP_TYPE: NEONTOLOGY_PAGE_AUTHORED_BY
  TARGET_LABEL: NeontologyAuthor
---

# Commands

Flask-Neontology adds a number of commands to your Flask app.

The commands are defined using Flask's native support for `click`, so will display when the help command is run.

    flask --app app --help

## Import

You can import data from json, yaml or markdown (with frontmatter) files.

    flask --app app import /path/to/files <md|json|yaml>  # defaults to md

If you just want to validate content, you can use the `--validate-only` flag.

### File Format

For nodes, properties should be defined as key-value pairs, with a special 'LABEL' property to specify the primary label (as defined in Neontology).

    {
      "LABEL": "NeontologyPage",
      "title": "Commands",
      "slug": "commands",
      "content": "Commands page content...",
    }

Outgoing relationships (`RELATIONSHIPS_OUT`) can also be defined with a node, again properties should be defined as key-value pairs, whilst there are also special keys which must be populated:

* `TARGETS` - a list of 'primary properties' (as defined in Neontology) for target nodes.
* `RELATIONSHIP_TYPE` - the relationship type to create (must be defined in Neontology)
* `TARGET_LABEL` - the primary label of the target node

Finally, when using markdown, the front matter must also specify which property should be populated with the body content using the 'BODY_PROPERTY' key.

    ---
    LABEL: NeontologyPage
    BODY_PROPERTY: content
    title: Commands
    slug: commands
    RELATIONSHIPS_OUT:
    - TARGETS:
        - Ontolocy
    RELATIONSHIP_TYPE: NEONTOLOGY_PAGE_AUTHORED_BY
    TARGET_LABEL: NeontologyAuthor

    # Commands

    Commands page content...

## Export

Export the nodes in the database to the Neontology json format.

*Note. this isn't advisable for databases with large numbers of nodes and relationships!*

    flask export ./path/to/output-directory

The destination directory should exist.

## Freeze

Generate a static site (html files and static assets) using the [Frozen-Flask](https://frozen-flask.readthedocs.io/) extension.

For large sites, this might take a while!

    flask freeze ./path/to/output-directory

The destination directory should exist.
