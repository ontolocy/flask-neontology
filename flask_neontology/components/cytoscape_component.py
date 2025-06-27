from enum import Enum
from pathlib import Path
from typing import ClassVar, List, Optional, Union

from neontology.result import NeontologyResult
from pydantic import AnyHttpUrl, model_validator

from .component import Component


class CytoscapeLayoutEnum(Enum):
    NULL = "null"
    RANDOM = "random"
    GRID = "grid"
    CIRCLE = "circle"
    CONCENTRIC = "concentric"
    BREADTH = "breadthfirst"
    COSE = "cose"


class CytoscapeComponent(Component):
    template: ClassVar = """
<div id="cy" class="w-100 h-100 vh-100 d-inline-block"  style="max-height:600px;"></div>
<script>
var elements = {{data.element_data | tojson}}

{% if data.element_data %}
var elements = {{data.element_data | tojson}}
{% endif %}
{% if data.url %}
fetch("{{data.url}}").then(res => res.json()).then(elements => {
{% endif %}
var cy = cytoscape({
  container: document.getElementById('cy'),
  elements: elements,
  style: [ // the stylesheet for the graph
    {
      selector: 'node',
      style: {
        'background-color': '#666',
        'label': 'data(name)'
      }
    },

    {
      selector: 'edge',
      style: {
        'width': 3,
        'line-color': '#ccc',
        'target-arrow-color': '#ccc',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier'
      }
    }
  ],
  layout: {
    name: '{{data.layout.value}}'
  }
});
{% if data.url %}
});
{% endif %}
</script>
"""

    headtags: List[str] = [
        "<script src='https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js'></script>"
    ]
    url: Optional[Union[AnyHttpUrl, Path, str]] = None
    layout: CytoscapeLayoutEnum = CytoscapeLayoutEnum.COSE
    element_data: Optional[list] = None
    results: Optional[NeontologyResult] = None

    @model_validator(mode="after")
    def generate_element_data(self):
        if self.url is None and self.element_data is None:
            if self.results is None:
                raise ValueError("results cannot be None if element_data is None")

            nodes = [
                {
                    "data": {
                        "id": x.get_pp(),
                        "name": str(x),
                        "label": x.__primarylabel__,
                    }
                }
                for x in self.results.nodes
            ]

            edges = [
                {
                    "data": {
                        "id": (
                            f"({str(x.source.get_pp())})"
                            f"-[{x.__relationshiptype__}]->({str(x.target.get_pp())})"
                        ),
                        "source": x.source.get_pp(),
                        "target": x.target.get_pp(),
                    }
                }
                for x in self.results.relationships
            ]

            self.element_data = nodes + edges

        return self
