import random
import string
from enum import Enum
from typing import Any, ClassVar, List, Optional, Union, get_args

from neontology import BaseNode, BaseRelationship
from neontology.schema_utils import SchemaProperty, extract_type_mapping
from neontology.utils import get_node_types
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from .component import Component


class ButtonComponent(Component):
    template: ClassVar = (
        """<button type="{{data.type}}" class="btn btn-primary">{{data.text}}</button>"""  # noqa: E501
    )

    text: str = "submit"
    type: str = "submit"
    value: str = "Submit"


class FieldComponent(Component):
    field_id: Optional[str] = Field(validate_default=True, default=None)
    label: str = "Input Field"
    name: str
    required: bool = False
    placeholder: Optional[Any] = None
    value: Optional[str] = None
    disabled: bool = False
    readonly: bool = False

    @field_validator("field_id")
    def generate_unique_id(cls, v: Optional[str]) -> str:
        if v is None:
            letters = string.ascii_lowercase
            v = "".join(random.choice(letters) for i in range(6))

        return v


class StringField(FieldComponent):
    template: ClassVar = """
<div class="mb-3">
<label for="{{data.field_id}}" class="form-label">{{data.label}}{% if data.required == true %}*{%endif%}</label>
<input type="text" name="{{data.name}}" class="form-control" id="{{data.field_id}}" {% if data.placeholder %}placeholder="{{data.placeholder}}"{% endif %}{% if data.required == true %} required{% endif %}{% if data.disabled == true %} disabled{% endif %}>
</div>
"""  # noqa: E501


class EmailField(FieldComponent):
    template: ClassVar = """
<div class="mb-3">
<label for="{{data.field_id}}" class="form-label">{{data.label}}{% if data.required == true %}*{%endif%}</label>
<input type="email" name="{{data.name}}" class="form-control" id="{{data.field_id}}" {% if data.placeholder %}placeholder="{{data.placeholder}}"{% endif %}{% if data.required == true %} required{% endif %}{% if data.disabled == true %} disabled{% endif %}>
</div>
"""  # noqa: E501


class PasswordField(FieldComponent):
    template: ClassVar = """
<div class="mb-3">
<label for="{{data.field_id}}" class="form-label">{{data.label}}{% if data.required == true %}*{%endif%}</label>
<input type="password" name="{{data.name}}" class="form-control" id="{{data.field_id}}" {% if data.placeholder %}placeholder="{{data.placeholder}}"{% endif %}{% if data.required == true %} required{% endif %}{% if data.disabled == true %} disabled{% endif %}>
</div>
"""  # noqa: E501


class SelectField(FieldComponent):
    template: ClassVar = """
<div class="mb-3">
<label for="{{data.field_id}}" class="form-label">{{data.label}}{% if data.required == true %}*{%endif%}</label>
<select type="text" name="{{data.name}}" class="form-control" id="{{data.field_id}}"{% if data.required == true %} required{% endif %}{% if data.disabled == true %} disabled{% endif %}  {% if data.multiple == true %} multiple{% endif %}>
{% if data.required != true %}<option></option>{%endif%}
{% for option in data.options %}
<option value="{{option[0]}}">{{option[1]}}</option>
{% endfor %}
</select>
</div>
"""  # noqa: E501
    options: List[tuple]
    multiple: bool = False


class HiddenField(FieldComponent):
    template: ClassVar = """
<div class="mb-3">
<input type="hidden" name="{{data.name}}" id="{{data.field_id}}" value="{{data.value}}">
</div>
"""
    value: str


class TextAreaField(FieldComponent):
    template: ClassVar = """
<div class="mb-3">
  <label for="{{data.field_id}}" class="form-label">{{data.label}}{% if data.required == true %}*{%endif%}</label>
  <textarea class="form-control" name="{{data.name}}" id="{{data.field_id}}" rows="{{data.rows}}"{% if data.required == true %} required{% endif %}>{% if data.placeholder %}{{data.placeholder}}{% endif %}</textarea>
</div>
"""  # noqa: E501

    rows: int = 1


class DateField(FieldComponent):
    template: ClassVar = """
<div class="mb-3">
<label for="{{data.field_id}}">{{data.label}}{% if data.required == true %}*{%endif%}</label>
<input id="{{data.field_id}}" class="form-control" type="date" {% if data.required == true %} required{% endif %}/>
</div>
"""  # noqa: E501


class FormComponent(Component):
    template: ClassVar = """
<form {% if data.action %}action="{{data.action}}"{% endif %} {% if data.method %}method="{{data.method}}"{% endif %}>{%for field in data.fields%}{{field.render() | safe}}{% endfor %}</form>
"""  # noqa: E501
    action: Optional[str] = None
    method: Optional[str] = None
    fields: List[Component] = []


FIELD_MAPPINGS = {
    "str": TextAreaField,
    "datetime": DateField,
    "SecretStr": PasswordField,
    "EmailStr": EmailField,
    "Enum": SelectField,
    "date": DateField,
}


class NodeFormModel:
    """Used as a mixin for neontology node forms which are
    augmented before being turned into a form.
    """

    __primarylabel__: ClassVar[Optional[str]] = None
    __primaryproperty__: ClassVar[Optional[str]] = None

    def __init__(self, **data: dict):
        try:
            super().__init__(**data)

        except NotImplementedError:
            pass

    def merge_nodes(self):
        raise NotImplementedError

    def create_nodes(self):
        raise NotImplementedError

    def validate_identifiers(self):
        return self


class ModelFormComponent(FormComponent):
    model: type[Union[BaseModel, BaseNode]]
    default_data: Optional[BaseModel] = None
    method: Optional[str] = "post"
    exclude_fields: List[str] = []

    @model_validator(mode="after")
    def generate_form(self):
        model_properties: list = []

        for field_name, field_props in self.model.model_fields.items():
            field_type = extract_type_mapping(
                field_props.annotation, show_optional=True
            )

            node_property = SchemaProperty(
                type_annotation=field_type,
                name=field_name,
                required=field_props.is_required(),
            )

            model_properties.append(node_property)

        for prop in model_properties:
            field_type = prop.type_annotation.core_type
            field_type_name = field_type.__name__
            field_name = prop.name

            if field_name in self.exclude_fields:
                continue

            if self.default_data:
                placeholder = self.default_data.model_dump().get(field_name)
            else:
                placeholder = None

            if str(field_type).startswith("list") and "Enum" in str(field_type):
                enum_type = get_args(field_type)[0]
                choices = [(x.value, x.name) for x in enum_type]
                field = SelectField(
                    label=field_name.title(),
                    name=field_name,
                    required=prop.required,
                    placeholder=placeholder,
                    options=choices,
                    multiple=True,
                )
                self.fields.append(field)

            elif isinstance(field_type, type) and issubclass(field_type, Enum):
                choices = [(x.value, x.name) for x in field_type]
                field = FIELD_MAPPINGS["Enum"](
                    label=field_name.title(),
                    name=field_name,
                    required=prop.required,
                    placeholder=placeholder,
                    options=choices,
                )
                self.fields.append(field)

            else:
                field = FIELD_MAPPINGS.get(field_type_name, StringField)(
                    label=field_name.title(),
                    name=field_name,
                    required=prop.required,
                    placeholder=placeholder,
                )
                self.fields.append(field)

        submit = ButtonComponent(text="Submit")

        self.fields.append(submit)

        return self

    @classmethod
    def _tidy_data(cls, data: dict):
        return {k: v for k, v in data.items() if v != ""}

    def form_validate(self, data: dict):
        try:
            # remove empty fields
            self.model(**self._tidy_data(data))
            return True
        except ValidationError:
            return False

    def form_to_model(self, data: dict):
        return self.model(**self._tidy_data(data))


class RelationshipFormComponent(ModelFormComponent):
    # wrap the form in an accordion
    template: ClassVar = """
<div class="accordion accordion-flush" id="{{data.model.__relationshiptype__}}CONTAINER">
<div class="accordion-item">
    <h2 class="accordion-header">
      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#{{data.model.__relationshiptype__}}" aria-expanded="false" aria-controls="{{data.model.__relationshiptype__}}">
        {{data.model.__relationshiptype__}} {% if not data.target_options %}<i class="bi bi-exclamation-diamond-fill ms-2"></i>{% endif %}
      </button>
    </h2>
    <div id="{{data.model.__relationshiptype__}}" class="accordion-collapse collapse" data-bs-parent="#{{data.model.__relationshiptype__}}CONTAINER">
      <form {% if data.action %}action="{{data.action}}"{% endif %} {% if data.method %}method="{{data.method}}"{% endif %}>{%for field in data.fields%}{{field.render() | safe}}{% endfor %}</form>
    </div>
  </div>
"""  # noqa: E501

    model: type[BaseRelationship]
    source_options: Optional[List[BaseNode]] = None
    target_options: Optional[List[BaseNode]] = None
    source_types: Optional[List[type[BaseNode]]] = None
    target_types: Optional[List[type[BaseNode]]] = None
    source_node: Optional[BaseNode] = None
    target_node: Optional[BaseNode] = None
    exclude_fields: List[str] = []
    method: Optional[str] = "post"

    def add_source_target_fields(
        self,
        name: str,
        input_options: Optional[List[BaseNode]] = None,
        input_types: Optional[List[type[BaseNode]]] = None,
        input_node: Optional[BaseNode] = None,
    ):
        node_field_label = f"{name.title()} Node"
        type_field_name = f"{name}_type"
        type_field_label = f"{name.title()} Label"

        if input_node:
            src_options = [(input_node.get_pp(), str(input_node))]
            source_field = SelectField(
                options=src_options, name=name, label=node_field_label
            )
            self.fields.append(source_field)

            input_types = [input_node.__class__]

        elif input_options:
            src_options = [(x.get_pp(), str(x)) for x in input_options]
            source_field = source_field = SelectField(
                options=src_options, name=name, label=node_field_label, required=True
            )
            self.fields.append(source_field)

            input_types = [x.__class__ for x in input_options]

        else:
            source_field = StringField(name=name, label=node_field_label, required=True)
            self.fields.append(source_field)

        if input_types:
            src_type_options = list(
                set([(x.__primarylabel__, x.__primarylabel__) for x in input_types])
            )

            src_type_field = SelectField(
                name=type_field_name,
                options=list(src_type_options),
                label=type_field_label,
                required=True,
            )
            self.fields.append(src_type_field)

        else:
            src_type_field = StringField(
                name=type_field_name, label=type_field_label, required=True
            )
            self.fields.append(src_type_field)

    @model_validator(mode="after")
    def generate_form(self):
        rel_schema = self.model.neontology_schema()

        # handle relationship type field (hidden?)
        self.fields.append(
            HiddenField(value=rel_schema.relationship_type, name="relationship_type")
        )

        # handle source field
        self.add_source_target_fields(
            "source", self.source_options, self.source_types, self.source_node
        )

        # handle target field
        self.add_source_target_fields(
            "target", self.target_options, self.target_types, self.target_node
        )

        for prop in rel_schema.properties:
            field_type = prop.type_annotation.core_type.__name__
            field_name = prop.name

            if field_name in self.exclude_fields:
                continue

            field = FIELD_MAPPINGS.get(field_type, StringField)(
                label=field_name.title(),
                name=field_name,
                required=prop.required,
                placeholder=None,
            )

            self.fields.append(field)

        submit = ButtonComponent(text="Submit")

        self.fields.append(submit)

        return self

    def _process_data(self, data: dict):
        input_data = dict(self._tidy_data(data))

        node_types = get_node_types()

        new_rel_source_label = str(input_data.get("source_type"))
        new_rel_source_pp = str(input_data.get("source"))

        new_rel_target_label = str(input_data.get("target_type"))
        new_rel_target_pp = str(input_data.get("target"))

        source_class = node_types[new_rel_source_label]
        target_class = node_types[new_rel_target_label]

        source_node = source_class.match(new_rel_source_pp)
        target_node = target_class.match(new_rel_target_pp)

        input_data["source"] = source_node
        input_data["target"] = target_node

        output_data = {
            k: v
            for k, v in input_data.items()
            if k not in ["source_type", "target_type", "relationship_type"]
        }

        return output_data

    def form_validate(self, data: dict):
        try:
            # remove empty fields
            self.model(**self._process_data(data))
            return True
        except ValidationError:
            return False

    def form_to_model(self, data: dict):
        return self.model(**self._process_data(data))
