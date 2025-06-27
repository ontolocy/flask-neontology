from flask_neontology.components import (
    LinkData,
    PageComponent,
    PageElements,
    SideMenuElement,
    SideMenuItem,
)


def test_element_leftbar(mini_app):
    elements = PageElements(
        leftbar=SideMenuElement(
            items=[
                SideMenuItem(
                    parent_link=LinkData(
                        title="Side Link 1",
                        url="#1",
                    ),
                    parent_icon="bi-check-square",
                ),
                SideMenuItem(
                    parent_link=LinkData(title="Side Link 2", url="#2"),
                    parent_icon="bi-diagram-3",
                ),
                SideMenuItem(
                    parent_link=LinkData(title="Side Link 3", url="#3"),
                    parent_icon="bi-diagram-3",
                    child_links=[
                        LinkData(title="Child Link 1", url="#3.1"),
                        LinkData(title="Child Link 2", url="#3.2"),
                    ],
                ),
            ]
        )
    )
    page = PageComponent(elements=elements)
    with mini_app.app_context():
        page_content = page.render()

    assert "Side Link 1" in page_content
    assert "position-fixed" not in page_content
    assert "margin-left: 180px;" not in page_content


def test_element_leftbar_fixed(mini_app):
    elements = PageElements(
        leftbar=SideMenuElement(
            items=[
                SideMenuItem(
                    parent_link=LinkData(
                        title="Side Link 1",
                        url="#1",
                    ),
                    parent_icon="bi-check-square",
                ),
            ],
            fixed=True,
        )
    )
    page = PageComponent(elements=elements)
    with mini_app.app_context():
        page_content = page.render()

    assert "position-fixed" in page_content
    assert "margin-left: 180px;" in page_content
