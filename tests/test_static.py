"""
Tests for static file serving endpoints.

Tests cover:
- GET /: Redirect to static/index.html
"""


class TestStaticFileServing:
    """Test suite for static file serving endpoints."""

    def test_root_redirect_status(self, test_client):
        """Verify that GET / returns a redirect response."""
        response = test_client.get("/", follow_redirects=False)
        assert response.status_code == 307

    def test_root_redirect_location(self, test_client):
        """Verify that GET / redirects to /static/index.html."""
        response = test_client.get("/", follow_redirects=False)
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_can_be_followed(self, test_client):
        """Verify that the redirect can be followed (static file exists)."""
        response = test_client.get("/", follow_redirects=True)
        assert response.status_code == 200
