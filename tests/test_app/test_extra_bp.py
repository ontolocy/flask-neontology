def test_create_page(test_client):
    """Test that the create page is available in development mode."""
    response = test_client.get("/create-page/")

    assert response.status_code == 200, (
        "Create page should be available in development mode"
    )
    assert "Create Page" in response.text, (
        "Create page should contain 'Create Page' text"
    )

    # Check if the form is present
    assert "Author 1" in response.text, "Form should contain 'Author 1' as an option"


def test_create_page_post(test_client):
    """Test that a new page node is created."""
    response = test_client.post(
        "/create-page/",
        data={
            "title": "Test Create Page Post",
            "slug": "test-create-page-post",
            "content": "This is a test page content.",
            "author": "Author 1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert b"Test Create Page Post" in response.data
    assert b"This is a test page content." in response.data
    assert b"Author 1" in response.data, "Page should be linked to Author 1"
