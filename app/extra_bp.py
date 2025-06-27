from enum import Enum

from flask import Blueprint, redirect, request

from flask_neontology.components import (
    ModelFormComponent,
    NodeFormModel,
    PageComponent,
    SectionComponent,
)

from .ontology.author import NeontologyAuthorNode
from .ontology.page import (
    NeontologyPageNode,
    NeontologyPageToAuthor,
)
from .views.pages import NeontologyPageViewset

bp = Blueprint(
    "extra_bp",
    __name__,
)


@bp.route("/create-page/", methods=["GET", "POST"])
def create_page():
    authors = {x.name: x.name for x in NeontologyAuthorNode.match_nodes()}
    AuthorEnum = Enum("AuthorEnum", authors)

    class MyModelFields(NodeFormModel, NeontologyPageNode):
        author: AuthorEnum

    form = ModelFormComponent(
        model=MyModelFields,
    )

    form_section = SectionComponent(
        title="Create Page Form",
        description=(
            "A custom form which will be used to create a new page node as well as"
            " relationships to a Topic (optional) and an Author (required)."
        ),
        body=[form],
    )

    if request.method == "POST":
        if form.form_validate(request.form):
            form_data = form.form_to_model(request.form)

            # now split out the attack model stuff and the OU bit
            new_page = NeontologyPageNode(
                **form_data.model_dump(exclude={"topic", "author"})
            )

            new_page.merge()

            author = NeontologyAuthorNode.match(form_data.author.value)

            page_to_author = NeontologyPageToAuthor(source=new_page, target=author)
            page_to_author.merge()

            # redirect to the new page view
            return redirect(
                NeontologyPageViewset(NeontologyPageNode).node_to_url(new_page)
            )

    page = PageComponent(
        title="Create a Page",
        description="New page form.",
        sections=[form_section],
    )
    return page.render()
