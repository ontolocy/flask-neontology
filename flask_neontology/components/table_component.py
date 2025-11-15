import urllib.parse
from collections import OrderedDict
from typing import ClassVar, Dict, List, Optional, Union
from uuid import uuid4

from neontology import BaseNode
from pydantic import BaseModel, Field, field_validator, model_validator

from .component import Component


class ColumnData(BaseModel):
    title: str
    result_field: str
    link_field: Optional[str] = None
    link_target: Optional[str] = None
    separator: Optional[str] = ", "


class TableComponent(Component):
    template: ClassVar = """
<div class="col-12">
    <table id="{{data.table_id}}" class="table table-striped caption-top table-hover">
        <thead>
            <tr>
                {% for column in data.columns %}
                <th scope="col">{{column.title}}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row_dict in data.rows %}
            <tr>
                {% for column in data.columns %}
                    <td>
                    {% if column.link_field %}
                        <a {%if column.link_target %}
                            target="{{column.link_target}}"
                            rel="noopener noreferrer"{% endif %}
                            href="{{row_dict[column.link_field]}}">
                    {% endif %}
                    {% if row_dict[column.result_field] is iterable
                        and (row_dict[column.result_field] is not string) %}
                    {{ row_dict[column.result_field]|join(column.separator | safe) }}
                    {% else %}
                    {{ row_dict[column.result_field] }}
                    {% endif %}
                    {% if column.link_field %}
                        </a>
                    {% endif %}
                    </td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% if data.datatable %}
<script type="text/javascript">
$(document).ready( function () {
  $('#{{data.table_id}}').DataTable({
    {% if data.datatable_columncontrol %}
    "columnControl": ['order', ['orderAsc', 'orderDesc', 'search']],{% endif %}
    "pageLength": {{data.datatable_page_length}},
    "ordering": {% if data.datatable_ordering %}true{% else %}false{% endif %},
    "lengthChange": {% if data.datatable_length_change %}true{% else %}false{% endif %},
    "searching": {% if data.datatable_searching %}true{% else %}false{% endif %},
  });
} );
</script>
{% endif %}
"""

    columns: List[ColumnData]
    rows: List[Dict[str, Union[str, int, list, dict]]]

    datatable: bool = False
    datatable_page_length: int = 50
    datatable_length_change: bool = False
    datatable_searching: Optional[bool] = None
    datatable_ordering: bool = False

    datatable_columncontrol: bool = False

    table_id: Optional[str] = Field(default_factory=uuid4)

    @model_validator(mode="after")
    def add_datatable_scripts(self):
        if self.datatable is True:
            self.headtags += [
                "<link href='https://cdn.datatables.net/2.1.2/css/dataTables.dataTables.min.css' rel='stylesheet'>",  # noqa: E501
                (
                    "<script src='https://code.jquery.com/jquery-3.7.1.min.js'"
                    " integrity='sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo='"
                    " crossorigin='anonymous'></script>"
                ),
                "<script src='https://cdn.datatables.net/2.3.5/js/dataTables.min.js'></script>",
                "<script src='https://cdn.datatables.net/2.3.5/js/dataTables.bootstrap5.min.js'></script>",
            ]

            if self.datatable_columncontrol is True:
                self.headtags += [
                    "<link href='https://cdn.datatables.net/columncontrol/1.1.1/css/columnControl.dataTables.min.css' rel='stylesheet'>",  # noqa: E501
                    "<script src='https://cdn.datatables.net/columncontrol/1.1.1/js/dataTables.columnControl.min.js'></script>",  # noqa: E501
                ]

        return self

    @model_validator(mode="after")
    def auto_search(self) -> "TableComponent":
        if self.datatable_searching is None:
            if len(self.rows) > 20:
                self.datatable_searching = True
            else:
                self.datatable_searching = False

        return self


class NodeListTableComponent(TableComponent):
    columns: List[ColumnData] = []
    rows: List[Dict[str, Union[str, int, list]]] = []
    nodes: List[BaseNode]
    url_pattern: Optional[str] = None
    url_field: Optional[str] = None
    fields: Optional[Union[List[str], Dict[str, str]]] = None

    @field_validator("nodes")
    def check_nodes_uniformity(cls, v):
        classes = [x.__class__.__name__ for x in v]
        classes_set = set(classes)

        if len(classes_set) > 1:
            raise ValueError("Nodes should all be of the same type.")

        return v

    @model_validator(mode="before")
    @classmethod
    def generate_columns(cls, data: dict) -> dict:
        if data.get("columns") is None and data["nodes"]:
            first_node = data["nodes"][0]
            data["columns"] = []

            if not data.get("fields"):
                fields = OrderedDict([(x, x) for x in first_node.model_fields])

            else:
                if isinstance(data["fields"], list):
                    fields = OrderedDict([(x.title(), x) for x in data["fields"]])
                else:
                    fields = data["fields"]

            if data.get("url_pattern"):
                if data.get("url_field"):
                    url_column = data["url_field"]
                elif first_node.__primaryproperty__ in fields:
                    url_column = first_node.__primaryproperty__
                else:
                    url_column = list(fields.items())[0][1]

            else:
                url_column = None

            for title, key in fields.items():
                if isinstance(data.get("fields"), list) and title in [
                    "__Str__",
                    "__str__",
                ]:
                    title = "Node"

                elif isinstance(data.get("fields"), list) and title in [
                    "__Pp__",
                    "__pp__",
                ]:
                    title = "Primary Property"

                if key == url_column:
                    column_data = ColumnData(
                        title=title,
                        result_field=key,
                        link_field="fn_node_link_field",
                    )

                else:
                    column_data = ColumnData(title=title, result_field=key)

                data["columns"].append(column_data)

        return data

    @model_validator(mode="after")
    def generate_rows(self) -> "NodeListTableComponent":
        self.rows = []
        for x in self.nodes:
            row = {
                **x.model_dump(),
                "__str__": str(x),
                "__pp__": str(x.get_pp()),
            }

            if self.url_pattern:
                row["fn_node_link_field"] = self.url_pattern.replace(
                    "<pp>", urllib.parse.quote(str(x.get_pp()))
                )

            self.rows.append(row)

        return self
