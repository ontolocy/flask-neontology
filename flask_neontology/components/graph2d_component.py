import random
import string
from pathlib import Path
from typing import ClassVar, List, Optional, Union

from neontology.result import NeontologyResult
from pydantic import AnyHttpUrl, Field, field_validator, model_validator

from .component import Component


class Graph2dComponent(Component):
    template: ClassVar = """
<div id="graphViewer_{{data.unique_id}}" class="vw-80">
  <div id="{{data.unique_id}}"></div>
</div>
<script>
const graphWidth2D{{ data.unique_id }} = document.getElementById("graphViewer_{{data.unique_id}}").clientWidth;
const graphHeight2D{{ data.unique_id }} = graphWidth2D{{ data.unique_id }} * (9 / 16);
{% if data.element_data %}
var gData3 = {{data.element_data | tojson}}
{% endif %}
{% if data.url %}
fetch("{{data.url}}").then(res => res.json()).then(gData3 => {
{% endif %}
  const Graph2D{{ data.unique_id  }} = ForceGraph()(document.getElementById("{{data.unique_id}}"))
  .graphData(gData3)
  .nodeAutoColorBy('LABEL')
  .nodeId("__pp__")
  .nodeLabel(node => `${node.LABEL}: ${node.__str__}`)
  .linkLabel('RELATIONSHIP_TYPE')
  .linkDirectionalParticles(1)
  .width(graphWidth2D{{ data.unique_id }})
  .height(graphHeight2D{{ data.unique_id }})
{% if data.url %}
});
{% endif %}
</script>
"""  # noqa: E501

    url: Optional[Union[AnyHttpUrl, Path, str]] = None
    unique_id: Optional[str] = Field(validate_default=True, default=None)

    headtags: List[str] = ["<script src='https://unpkg.com/force-graph'></script>"]

    element_data: Optional[dict] = None
    results: Optional[NeontologyResult] = None

    @model_validator(mode="after")
    def generate_element_data(self):
        if self.url is None and self.element_data is None:
            if self.results is None:
                raise ValueError("results cannot be None if element_data is None")

            graph_data = {"directed": True, "nodes": [], "edges": []}

            graph_data["nodes"] = [
                {
                    # Add label for nodes of same pp but different label
                    "__pp__": f"{x['LABEL']}#{x['__pp__']}",
                    "__str__": x["__str__"],
                    "LABEL": x["LABEL"],
                }
                for x in self.results.node_link_data["nodes"]
            ]

            graph_data["links"] = [
                {
                    "RELATIONSHIP_TYPE": x["RELATIONSHIP_TYPE"],
                    "SOURCE_LABEL": x["SOURCE_LABEL"],
                    "TARGET_LABEL": x["TARGET_LABEL"],
                    "source": f"{x['SOURCE_LABEL']}#{x['source']}",
                    "target": f"{x['TARGET_LABEL']}#{x['target']}",
                }
                for x in self.results.node_link_data["edges"]
            ]

            self.element_data = graph_data

        return self

    @field_validator("unique_id")
    def generate_unique_id(cls, v: Optional[str]) -> str:
        if v is None:
            letters = string.ascii_lowercase
            v = "".join(random.choice(letters) for i in range(6))

        return v
