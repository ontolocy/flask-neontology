from typing import ClassVar, Dict, List, Optional, Union

from neontology import BaseNode
from pydantic import BaseModel, field_validator, model_validator

from .component import Component
from .link_component import LinkComponent


class RowData(BaseModel):
    title: str
    data: Union[str, int, LinkComponent, List[Union[str, int, LinkComponent]]]
    separator: Optional[str] = ", "

    @field_validator("data")
    def make_list(
        cls, v: Union[str, int, LinkComponent, List[Union[str, int, LinkComponent]]]
    ) -> list:
        if isinstance(v, list):
            return v
        else:
            return [v]


class TranslatedTableComponent(Component):
    template: ClassVar = """
    <div class="col-12">
        <table class="table table-striped caption-top table-hover">
            <tbody>
                {% for row in data.rows %}
                {% if row.data %}
                <tr>
                    <th scope="row">
                        {{row.title}}
                    </th>
                    <td>
                    {% for entry in row.data %}
                        {% if entry.__class__.__name__ == 'LinkComponent' %}
                            {{entry.render() | safe}}
                            {%- if not loop.last %}{{row.separator}}{% endif -%}
                        {% else %}
                            {{entry|neontology_to_string}}
                            {%- if not loop.last %}{{row.separator}}{% endif -%}
                        {% endif %}
                    {% endfor %}
                    </td>
                </tr>
                {% endif %}
                {% endfor %}
            </tbody>
        </table>
    </div>
    """

    rows: List[RowData]


class NodeTranslatedTableComponent(TranslatedTableComponent):
    rows: List[RowData] = []
    node: BaseNode
    columns: Optional[Dict[str, str]] = None
    show_empty: Optional[bool] = False

    @model_validator(mode="before")
    @classmethod
    def generate_columns(cls, data: dict) -> dict:
        if data.get("columns") is None and data["node"]:
            data["columns"] = {
                k: k.title() for k in data["node"].__class__.model_fields
            }

        return data

    @model_validator(mode="after")
    def generate_rows(self) -> "NodeTranslatedTableComponent":
        if not self.rows and self.columns:
            for key, title in self.columns.items():
                # only include rows where there is a value
                if self.show_empty is False and self.node.model_dump().get(key):
                    if key == self.node.__primaryproperty__:
                        title = title + " (Primary Property)"

                    row = RowData(
                        title=title, data=str(self.node.model_dump().get(key))
                    )

                    if key == self.node.__primaryproperty__:
                        self.rows.insert(0, row)

                    else:
                        self.rows.append(row)

        return self
