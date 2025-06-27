from typing import ClassVar, List

from .graph2d_component import Graph2dComponent


class Graph3dComponent(Graph2dComponent):
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
  const Graph2D{{ data.unique_id  }} = ForceGraph3D()(document.getElementById("{{data.unique_id}}"))
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
    headtags: List[str] = [
        "<script src='https://cdn.jsdelivr.net/npm/3d-force-graph'></script>"
    ]
