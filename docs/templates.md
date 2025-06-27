---
LABEL: NeontologyPage
BODY_PROPERTY: content
title: Templates and Pages
slug: templates
RELATIONSHIPS_OUT:
- TARGETS:
    - Ontolocy
  RELATIONSHIP_TYPE: NEONTOLOGY_PAGE_AUTHORED_BY
  TARGET_LABEL: NeontologyAuthor
---
# Templates and Pages

The NeontologyManager must be initialised before you can use components (and templates).

Neontology comes with a default template at: `neontology/neontology_default.html`

The Page components expects a 'neontology_base.html' template at the root template directory. Neontology comes with one by default which just pulls it through:

```html
{% extends 'neontology/neontology_default.html' %}
```

You can override this by putting your own 'neontology_base.html' in the root template directory.

The main thing you need in the base template is a `content` block.

Flask Neontology should magically use the Flask template environment so things like `url_for` should still work.

Key blocks:

* Favicon
* Brand Text
* Common Scripts

The PageComponent then extends `neontology_base.html`, replacing key blocks with dynamic data and defined components.

It relies on the Jinja environment (which is typically established by Flask), so generating a PageComponent outside of a Flask context and without a JinjaEnvironment which includes the defined templates will cause errors.
