"""
Tests for static file serving and frontend functionality.
"""

import pytest
from fastapi.testclient import TestClient


class TestStaticFiles:
    """Test static file serving."""
    
    def test_static_index_html_accessible(self, client):
        """Test that static/index.html is accessible."""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # Check that it contains expected content
        content = response.text
        assert "Mergington High School" in content
        assert "Extracurricular Activities" in content
        assert '<div id="activities-list">' in content
    
    def test_static_css_accessible(self, client):
        """Test that static/styles.css is accessible."""
        response = client.get("/static/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
        
        # Check that it contains expected CSS
        content = response.text
        assert ".activity-card" in content
        assert ".participants-list" in content
        assert ".delete-icon" in content
    
    def test_static_js_accessible(self, client):
        """Test that static/app.js is accessible."""
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert "javascript" in response.headers.get("content-type", "") or "text/plain" in response.headers.get("content-type", "")
        
        # Check that it contains expected JavaScript
        content = response.text
        assert "fetchActivities" in content
        assert "unregisterParticipant" in content
        assert "addEventListener" in content
    
    def test_nonexistent_static_file_returns_404(self, client):
        """Test that non-existent static files return 404."""
        response = client.get("/static/nonexistent.txt")
        assert response.status_code == 404