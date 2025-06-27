from flask_neontology.components import (
    PageComponent,
    PageElements,
)


def test_blank_page(mini_app):
    page = PageComponent(title="Test Page", description="This is a test page.")

    with mini_app.app_context():
        page_content = page.render()

    assert "<title>Test Page</title>" in page_content
    assert '<meta name="description" content="This is a test page.">' in page_content
    assert "sticky-top" not in page_content


def test_sticky_top_nav(mini_app):
    page = PageComponent(
        title="Test Page", description="This is a test page.", sticky_topnav=True
    )

    with mini_app.app_context():
        page_content = page.render()

    assert "sticky-top" in page_content


def test_element_footer(mini_app):
    elements = PageElements(footer_text="This is the footer text.")
    page = PageComponent(elements=elements)
    with mini_app.app_context():
        page_content = page.render()

    assert "This is the footer text." in page_content
