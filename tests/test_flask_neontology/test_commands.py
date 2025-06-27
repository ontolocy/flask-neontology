import json

import pytest


def test_import_md(cli_runner, tmp_path, use_graph):
    content = """---
LABEL: DummyNode
BODY_PROPERTY: description
name: testimport
---

This is the description of the test node.

"""
    md_file = tmp_path / "test.md"

    with open(md_file, "w") as f:
        f.write(content)

    result = cli_runner.invoke(args=["import", str(tmp_path)])

    assert result.exit_code == 0

    cypher_result = use_graph.evaluate_query_single(
        "MATCH (n:DummyNode {name: 'testimport'}) RETURN COUNT(n)"
    )

    assert cypher_result == 1


def test_validate_md(cli_runner, tmp_path, use_graph):
    content = """---
LABEL: DummyNode
BODY_PROPERTY: description
name: testimport
---

This is the description of the test node.

"""
    md_file = tmp_path / "test.md"

    with open(md_file, "w") as f:
        f.write(content)

    result = cli_runner.invoke(args=["import", str(tmp_path), "--validate-only"])

    assert result.exit_code == 0

    cypher_result = use_graph.evaluate_query_single(
        "MATCH (n:DummyNode {name: 'testimport'}) RETURN COUNT(n)"
    )

    assert cypher_result == 0


def test_validate_md_bad(cli_runner, tmp_path):
    content = """---
BODY_PROPERTY: description
name: testimport
---

This is the description of the test node.

"""
    md_file = tmp_path / "test.md"

    with open(md_file, "w") as f:
        f.write(content)

    result = cli_runner.invoke(args=["import", str(tmp_path), "--validate-only"])

    assert result.exit_code == 1


@pytest.mark.filterwarnings("ignore:Ignored '404 NOT FOUND' on URL /static/favicon.ico")
def test_freeze(mini_app, cli_runner, tmp_path):
    with mini_app.app_context():
        result = cli_runner.invoke(args=["freeze", str(tmp_path)])

    assert result.exit_code == 0

    assert tmp_path.joinpath("dummies", "foo", "index.html").exists()

    with open(tmp_path.joinpath("dummies", "foo", "index.html"), "r") as f:
        content = f.read()

    assert "foo CONTENT" in content


def test_export_json(cli_runner, tmp_path, use_graph):
    result = cli_runner.invoke(args=["export", str(tmp_path)])

    assert result.exit_code == 0

    nodes_file = tmp_path / "DummyNode.nodes.json"
    assert nodes_file.exists()

    with open(nodes_file, "r") as f:
        nodes_data = json.load(f)

    assert len(nodes_data) > 0

    names = [node["name"] for node in nodes_data]
    assert "foo" in names
    assert "bar" in names
