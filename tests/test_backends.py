"""Unit tests for backend modules."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSeleniumBackendFunctions:
    """Tests for selenium_backend module functions."""

    def test_fetch_page_returns_expected_structure(self):
        """Test that fetch_page returns dict with expected keys."""
        from lib import selenium_backend

        # Mock the driver to avoid actual browser
        with patch.object(selenium_backend, 'create_driver') as mock_create:
            mock_driver = Mock()
            mock_driver.current_url = "https://example.com"
            mock_driver.title = "Test Page"
            mock_driver.page_source = "<html><body><main><p>Content</p></main></body></html>"
            mock_create.return_value = mock_driver

            result = selenium_backend.fetch_page(
                url="https://example.com",
                headless=True,
                timeout=10,
            )

            assert "success" in result
            assert "url" in result
            assert "final_url" in result
            assert "title" in result
            assert "content" in result
            assert "metadata" in result
            assert "error" in result

    def test_fetch_page_handles_exceptions(self):
        """Test that fetch_page handles exceptions gracefully."""
        from lib import selenium_backend

        with patch.object(selenium_backend, 'create_driver') as mock_create:
            mock_create.side_effect = Exception("Browser failed")

            result = selenium_backend.fetch_page(
                url="https://example.com",
                headless=True,
            )

            assert result["success"] is False
            assert result["error"] is not None
            assert "Browser failed" in result["error"]

    def test_search_google_returns_expected_structure(self):
        """Test that search_google returns dict with expected keys."""
        from lib import selenium_backend

        with patch.object(selenium_backend, 'create_driver') as mock_create:
            mock_driver = Mock()
            mock_driver.find_elements.return_value = []
            mock_create.return_value = mock_driver

            result = selenium_backend.search_google(
                query="test",
                max_results=5,
                headless=True,
            )

            assert "success" in result
            assert "query" in result
            assert "engine" in result
            assert result["engine"] == "google"
            assert "results" in result
            assert isinstance(result["results"], list)
            assert "metadata" in result

    def test_search_bing_returns_expected_structure(self):
        """Test that search_bing returns dict with expected keys."""
        from lib import selenium_backend

        with patch.object(selenium_backend, 'create_driver') as mock_create:
            mock_driver = Mock()
            mock_driver.find_elements.return_value = []
            mock_create.return_value = mock_driver

            result = selenium_backend.search_bing(
                query="test",
                max_results=5,
                headless=True,
            )

            assert "success" in result
            assert "query" in result
            assert "engine" in result
            assert result["engine"] == "bing"
            assert "results" in result
            assert isinstance(result["results"], list)

    def test_search_duckduckgo_returns_expected_structure(self):
        """Test that search_duckduckgo returns dict with expected keys."""
        from lib import selenium_backend

        with patch.object(selenium_backend, 'create_driver') as mock_create:
            mock_driver = Mock()
            mock_driver.find_elements.return_value = []
            mock_create.return_value = mock_driver

            result = selenium_backend.search_duckduckgo(
                query="test",
                max_results=5,
                headless=True,
            )

            assert "success" in result
            assert "query" in result
            assert "engine" in result
            assert result["engine"] == "duckduckgo"
            assert "results" in result


class TestZendriverBackendFunctions:
    """Tests for zendriver_backend module functions."""

    def test_fetch_page_sync_returns_expected_structure(self):
        """Test that fetch_page_sync returns dict with expected keys."""
        from lib import zendriver_backend

        # Mock the async functions
        mock_result = {
            "success": True,
            "url": "https://example.com",
            "final_url": "https://example.com/",
            "title": "Test",
            "content": "# Test",
            "metadata": {"backend": "zendriver"},
            "error": None,
        }

        with patch.object(zendriver_backend, 'fetch_page', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_result

            result = zendriver_backend.fetch_page_sync(
                url="https://example.com",
                headless=True,
            )

            assert "success" in result
            assert "url" in result
            assert "metadata" in result
            assert result["metadata"]["backend"] == "zendriver"

    def test_search_google_sync_returns_expected_structure(self):
        """Test that search_google_sync returns dict with expected keys."""
        from lib import zendriver_backend

        mock_result = {
            "success": True,
            "query": "test",
            "engine": "google",
            "results": [{"title": "Test", "url": "http://example.com", "snippet": "..."}],
            "metadata": {"backend": "zendriver"},
            "error": None,
        }

        with patch.object(zendriver_backend, 'search_google', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_result

            result = zendriver_backend.search_google_sync(
                query="test",
                max_results=5,
            )

            assert "success" in result
            assert "query" in result
            assert "engine" in result
            assert result["engine"] == "google"
            assert "results" in result

    def test_search_bing_sync_returns_expected_structure(self):
        """Test that search_bing_sync returns dict with expected keys."""
        from lib import zendriver_backend

        mock_result = {
            "success": True,
            "query": "test",
            "engine": "bing",
            "results": [],
            "metadata": {"backend": "zendriver"},
            "error": None,
        }

        with patch.object(zendriver_backend, 'search_bing', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_result

            result = zendriver_backend.search_bing_sync(
                query="test",
                max_results=5,
            )

            assert "success" in result
            assert result["engine"] == "bing"


class TestBackendSelection:
    """Tests for backend selection in main scripts."""

    def test_fetch_backend_selection(self):
        """Test that fetch.py correctly imports backends."""
        # Test selenium backend import
        from lib import selenium_backend
        assert hasattr(selenium_backend, 'fetch_page')

        # Test zendriver backend import
        from lib import zendriver_backend
        assert hasattr(zendriver_backend, 'fetch_page_sync')

    def test_search_backend_functions_exist(self):
        """Test that search backend functions exist."""
        from lib import selenium_backend
        from lib import zendriver_backend

        # Selenium backend
        assert hasattr(selenium_backend, 'search_google')
        assert hasattr(selenium_backend, 'search_bing')
        assert hasattr(selenium_backend, 'search_duckduckgo')

        # Zendriver backend (sync wrappers)
        assert hasattr(zendriver_backend, 'search_google_sync')
        assert hasattr(zendriver_backend, 'search_bing_sync')


class TestMetadataBackendField:
    """Test that metadata includes backend identifier."""

    def test_selenium_metadata_includes_backend(self):
        """Test selenium results include backend field."""
        from lib import selenium_backend

        with patch.object(selenium_backend, 'create_driver') as mock_create:
            mock_driver = Mock()
            mock_driver.current_url = "https://example.com"
            mock_driver.title = "Test"
            mock_driver.page_source = "<html><body>Test</body></html>"
            mock_create.return_value = mock_driver

            result = selenium_backend.fetch_page("https://example.com", headless=True)

            assert result["metadata"].get("backend") == "selenium"

    def test_zendriver_metadata_includes_backend(self):
        """Test zendriver results include backend field."""
        from lib import zendriver_backend

        mock_result = {
            "success": True,
            "url": "https://example.com",
            "final_url": "https://example.com/",
            "title": "Test",
            "content": "Test",
            "metadata": {"backend": "zendriver", "fetch_time_ms": 100},
            "error": None,
        }

        with patch.object(zendriver_backend, 'fetch_page', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_result

            result = zendriver_backend.fetch_page_sync("https://example.com")

            assert result["metadata"].get("backend") == "zendriver"
