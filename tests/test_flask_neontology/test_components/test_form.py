from enum import Enum
from typing import Optional

from flask_neontology.components import (
    ModelFormComponent,
    NodeFormModel,
)

from ..conftest import DummyNode


def test_model_form(mini_app):
    form = ModelFormComponent(
        model=DummyNode,
    )

    with mini_app.app_context():
        rendered_form = form.render()

    assert "Name*" in rendered_form


def test_hybrid_form(mini_app):
    topics = {"foo": "foo", "bar": "bar", "baz": "baz"}
    TopicEnum = Enum("TopicEnum", topics)

    class MyModelFields(NodeFormModel, DummyNode):
        optional_topic: Optional[TopicEnum] = None
        primary_topic: TopicEnum

    form = ModelFormComponent(
        model=MyModelFields,
    )

    with mini_app.app_context():
        rendered_form = form.render()

    assert "Name*" in rendered_form
    assert "<option></option>" in rendered_form
    assert '<option value="foo">foo</option>' in rendered_form
    assert ">Description</label>" in rendered_form
    assert "Optional_Topic</label>" in rendered_form

    good_form_content = {"name": "Test Node", "primary_topic": "foo"}
    assert form.form_validate(good_form_content) is True

    bad_form_content = {"name": "", "primary_topic": "foo"}
    assert form.form_validate(bad_form_content) is False

    assert form.form_to_model(good_form_content) == MyModelFields(
        name="Test Node", primary_topic=TopicEnum.foo, optional_topic=None
    )
