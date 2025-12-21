import json
import urllib.parse
import warnings
from pathlib import Path

import click
from flask import current_app
from flask_frozen import Freezer, MissingURLGeneratorWarning
from neontology.tools import import_json, import_md, import_yaml
from neontology.utils import get_node_types, get_rels_by_type

from flask_neontology.views import NeontologyListView


@click.command("import")
@click.argument("directory", type=click.Path(exists=True))
@click.argument(
    "file_type",
    default="md",
    type=click.Choice(["md", "yml", "json"], case_sensitive=False),
)
@click.option(
    "--validate-only", help="Validate the content without importing it.", is_flag=True
)
def ingest(directory: str, file_type: str, validate_only: bool) -> None:
    """Import static data from the given directory."""
    click.echo(f"Importing data from {directory}")

    try:
        if file_type == "md":
            import_md(directory, validate_only=validate_only)

        elif file_type == "yml":
            import_yaml(directory, validate_only=validate_only)

        elif file_type == "json":
            import_json(directory, validate_only=validate_only)

        else:
            click.echo("Invalid file type specified. See help.")

    except KeyError:
        click.echo(
            "Import failed, are all content nodes defined "
            "and registered with the NeontologyManager."
        )


@click.command("export")
@click.argument("directory", type=click.Path(exists=True))
def export(directory) -> None:
    """Export nodes and relationships."""

    # First the nodes
    for label, node_type in get_node_types().items():
        export_path = Path(directory, label).with_suffix(".nodes.json")

        node_count = node_type.get_count()

        click.echo(f"Matching {node_count} {label} nodes.")

        raw_nodes = node_type.match_nodes()

        if raw_nodes:
            nodes = [json.loads(x.neontology_dump_json()) for x in raw_nodes]

            click.echo(f"Creating {export_path}")

            with open(export_path, "w") as export_file:
                json.dump(nodes, export_file, indent=2)

    for rel_type, rel_type_data in get_rels_by_type().items():
        export_path = Path(directory, rel_type).with_suffix(".relationships.json")

        rel_class = rel_type_data.relationship_class

        rel_count = rel_class.get_count()

        click.echo(f"Matching {rel_count} {rel_type} relationships.")

        relationships = rel_class.match_relationships()

        if relationships:
            export_rels = [json.loads(x.neontology_dump_json()) for x in relationships]

            click.echo(f"Creating {export_path}")

            with open(export_path, "w") as export_file:
                json.dump(export_rels, export_file, indent=2)


@click.command("freeze")
@click.argument("directory", type=click.Path(exists=True))
def freeze(directory) -> None:
    """Create a static version of this flask application."""

    # because we dynamically generate URLs,
    #   flask_frozen can throw some unnecessary warnings
    warnings.filterwarnings(
        "ignore",
        category=MissingURLGeneratorWarning,
    )

    filepath = Path(directory)

    click.echo("it's freezing")

    current_app.config["FREEZER_DESTINATION"] = str(filepath.absolute())

    click.echo(f"Saving to {current_app.config['FREEZER_DESTINATION']}")

    if "FREEZER_REMOVE_EXTRA_FILES" not in current_app.config:
        # by default, don't automatically delete all the files
        current_app.config["FREEZER_REMOVE_EXTRA_FILES"] = False

    freezer = Freezer(current_app)

    @freezer.register_generator
    def register_neontology_view_urls():
        neontology_manager = getattr(current_app, "neontology_manager", None)

        if neontology_manager is None:
            raise RuntimeError(
                "The Flask app does not have a 'neontology_manager' attribute. "
                "Please ensure it is initialized and attached to the app."
            )

        for view in neontology_manager.views:
            if issubclass(view, NeontologyListView):
                yield view.view_url_rule()

            else:
                nodes = view.viewset_handler(view.viewset_handler.model).match_nodes()
                for node in nodes:
                    yield view.view_url_rule().replace(
                        "<pp>", urllib.parse.quote(str(node.get_pp()))
                    )

        for api_ver, api_views in neontology_manager.api_views.items():
            for api_view in api_views:
                # first do the list endpoint
                yield api_view.get_list_endpoint(api_ver)

                nodes = api_view().match_nodes()

                for node in nodes:
                    yield api_view.get_detail_endpoint(api_ver).replace(
                        "<pp>", urllib.parse.quote(str(node.get_pp()))
                    )
                    for rel_type in api_view.related_resources.keys():
                        print(f"Freezing related: {rel_type}")
                        yield api_view.get_related_endpoint(rel_type, api_ver).replace(
                            "<pp>", urllib.parse.quote(str(node.get_pp()))
                        )

    freezer.freeze()
