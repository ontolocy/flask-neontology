from typing import Optional

from flask import abort, redirect, request
from neontology import BaseNode
from neontology.utils import (
    get_rels_by_source,
    get_rels_by_type,
)

from ..components import (
    BreadcrumbElement,
    ModelFormComponent,
    PageElementsEnum,
    RelationshipFormComponent,
)
from ..views import (
    NeontologyEndpointView,
    NeontologyView,
    page_element,
    page_section,
)
from .viewset import AutographViewset


class LabelCreateEndpointView(NeontologyView):
    endpoint = "create/"
    viewset_handler = AutographViewset

    @classmethod
    def view_name(cls, model: Optional[type[BaseNode]] = None) -> str:
        return "AutoGraph" + cls.get_viewset(model).list_view_name() + "-create"

    @classmethod
    def view_url_rule(cls, model: Optional[type[BaseNode]] = None) -> str:
        return cls.get_viewset(model).list_url() + cls.endpoint

    @page_element(PageElementsEnum.TITLE)
    def page_title(self) -> str:
        return f"Create a {self.model.__primarylabel__}"

    @page_section(title="Creation Form")
    def main_section(self):
        return ModelFormComponent(
            model=self.model, action=self.view_url_rule(self.model)
        )

    def post(self):
        form = ModelFormComponent(model=self.model)

        if not form.form_validate(request.form):
            abort(422)

        else:
            new_node = form.form_to_model(request.form)

        try:
            new_node.create()

        except RuntimeError:
            abort(409)

        return redirect(self.viewset.pp_to_url(str(new_node.get_pp())))


class LabelEditEndpointView(NeontologyEndpointView):
    endpoint = "update/"
    viewset_handler = AutographViewset

    @page_element(PageElementsEnum.TITLE)
    def page_title(self) -> str:
        return f"Edit '{str(self.node)}' Node"

    @page_element(PageElementsEnum.BREADCRUMBS)
    def breadcrumbs(self) -> BreadcrumbElement:
        breadcrumbs = self.viewset.endpoint_breadcrumbs(self.node, "Edit")
        return BreadcrumbElement(breadcrumbs=breadcrumbs)

    @page_section(title="Update Node Form")
    def main_section(self):
        return ModelFormComponent(
            model=self.model,
            action=self.viewset.pp_to_endpoint_url(
                endpoint=self.endpoint, pp=self.node.get_pp()
            ),
            default_data=self.node,
        )

    def post(self, pp: str):
        self.node = self.model.match(pp)

        form = ModelFormComponent(model=self.model)

        if not self.node:
            abort(404)

        if not form.form_validate(request.form):
            abort(422)

        else:
            updated_node = form.form_to_model(request.form)

        if updated_node.get_pp() != self.node.get_pp():
            abort(409)

        updated_node.merge()

        return redirect(self.viewset.pp_to_url(str(updated_node.get_pp())))


class LabelCreateRelationshipEndpointView(NeontologyEndpointView):
    endpoint = "create-relationships/"
    viewset_handler = AutographViewset

    @page_element(PageElementsEnum.TITLE)
    def page_title(self) -> str:
        return f"Create Relationships For {str(self.node)}"

    @page_section(title="Creation Form")
    def main_section(self):
        rel_forms = []

        outgoing_rels = get_rels_by_source().get(self.model.__primarylabel__, set())
        all_rel_types = get_rels_by_type()

        for rel_type_str in outgoing_rels:
            rel_class = all_rel_types[rel_type_str].relationship_class

            rel_targets = all_rel_types[rel_type_str].target_class.match_nodes()

            rel_form = RelationshipFormComponent(
                model=rel_class,
                source_node=self.node,
                target_options=rel_targets,
                action=self.viewset.pp_to_endpoint_url(
                    endpoint=self.endpoint, pp=self.node.get_pp()
                ),
            )

            if rel_targets:
                rel_forms.insert(0, rel_form)
            else:
                rel_forms.append(rel_form)

        return rel_forms

    def post(self, pp: str):
        all_rel_types = get_rels_by_type()

        self.node = self.model.match(pp)

        if not self.node:
            abort(404)

        new_rel_type = request.form.get("relationship_type")

        if new_rel_type is None or new_rel_type not in all_rel_types.keys():
            abort(404)

        new_rel_class = all_rel_types[new_rel_type].relationship_class

        rel_form = RelationshipFormComponent(
            model=new_rel_class,
            source_node=self.node,
        )

        if not rel_form.form_validate(request.form):
            abort(422)

        new_rel = rel_form.form_to_model(request.form)

        if new_rel.source.get_pp() != self.node.get_pp():
            abort(409)

        new_rel.merge()

        return redirect(self.viewset.pp_to_url(str(self.node.get_pp())))
