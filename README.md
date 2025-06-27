# Flask Neontology

Flask-Neontology is an experimental, proof-of-concept Python framework for building Neo4j / graph database powered Flask websites. It uses the Neontology library for interacting with Neo4j.

The project is an early stage proof of concept and not intended for use in production environments. It is likely to see breaking changes without notice.

## Example App

The `app` directory gives a more complete example. Follow the steps below to get it up and running (including a hosted set of docs).

1. Clone the repo

2. Install the extension (you might want to do this in a virtual environment)

```bash
pip install .   # run this in the cloned repo to install in your environment
```

3. Import the seed data

```bash
flask import ./docs
```

This will handily import the docs as nodes so you can explore the app to learn more about Flask-Neontology.

4. Get started with the example `app`

```bash
flask run --debug
```

This runs the Flask app in the `app` directory, making it available at port 5000.

5. Explore the AutoGraph

As well as explicitly defined pages and views, you can activate the 'AutoGraph' which will use the defined Neontology ontology to automatically generate views for exploring, editing and populating the graph.

Hit the AutoGraph link, or go to `/autograph`.

6. Generate a static site

You can use a built in command to convert the app into a static site.

```bash
flask --app 'app:create_app("FREEZE")' run  # preview frozen site
flask --app 'app:create_app("FREEZE")' freeze ./output-directory
python -m http.server --directory ./output-directory # explore the static version
```
