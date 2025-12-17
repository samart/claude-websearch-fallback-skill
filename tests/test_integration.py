"""Integration tests for fetch and search scripts.

These tests require Chrome and network access.
Run with: pytest tests/test_integration.py -v --run-integration

NOTE: Search tests may fail due to bot detection (CAPTCHA) when run
in automated/headless mode. This is expected behavior - the skill is
designed to work with the user's real browser profile which has
legitimate cookies and browsing history.
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
BACKENDS = ["selenium", "zendriver"]


def run_script(script_name: str, args: list[str], timeout: int = 60) -> dict:
    """Run a script and parse JSON output."""
    script_path = SKILL_DIR / script_name
    cmd = [sys.executable, str(script_path)] + args

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": f"Failed to parse output: {result.stdout[:500]}",
            "stderr": result.stderr[:500],
        }


@pytest.fixture
def check_chrome():
    """Skip if Chrome is not available."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=options)
        driver.quit()
    except Exception as e:
        pytest.skip(f"Chrome not available: {e}")


class TestFetchScript:
    """Tests for fetch.py script."""

    @pytest.mark.integration
    @pytest.mark.parametrize("backend", BACKENDS)
    def test_fetch_simple_url(self, check_chrome, backend):
        """Test fetching a simple public URL with each backend."""
        result = run_script("fetch.py", [
            "--url", "https://example.com",
            "--headless",
            "--backend", backend,
        ])

        assert result["success"] is True
        assert result["title"] is not None
        assert "Example Domain" in result["title"]
        assert result["content"] is not None
        assert len(result["content"]) > 0
        assert result["metadata"]["backend"] == backend

    @pytest.mark.integration
    @pytest.mark.parametrize("backend", BACKENDS)
    def test_fetch_with_redirect(self, check_chrome, backend):
        """Test fetching a URL that redirects with each backend."""
        result = run_script("fetch.py", [
            "--url", "http://example.com",
            "--headless",
            "--backend", backend,
        ])

        assert result["success"] is True
        assert "https" in result["final_url"]

    @pytest.mark.integration
    @pytest.mark.parametrize("backend", BACKENDS)
    def test_fetch_invalid_url(self, check_chrome, backend):
        """Test fetching an invalid URL with each backend."""
        result = run_script("fetch.py", [
            "--url", "https://this-domain-does-not-exist-12345.com",
            "--headless",
            "--timeout", "10",
            "--backend", backend,
        ])

        # Selenium raises exception (success=False), zendriver returns Chrome error page
        if result["success"] is False:
            assert result["error"] is not None
        else:
            # Zendriver returns Chrome's error page as content
            assert "can't be reached" in result["content"] or "DNS" in result["content"]

    @pytest.mark.integration
    @pytest.mark.parametrize("backend", BACKENDS)
    def test_fetch_returns_metadata(self, check_chrome, backend):
        """Test that fetch returns proper metadata for each backend."""
        result = run_script("fetch.py", [
            "--url", "https://example.com",
            "--headless",
            "--backend", backend,
        ])

        assert "metadata" in result
        assert "fetch_time_ms" in result["metadata"]
        assert "content_length" in result["metadata"]
        assert result["metadata"]["fetch_time_ms"] > 0
        assert result["metadata"]["backend"] == backend


class TestSearchScript:
    """Tests for search.py script.

    NOTE: Search engines aggressively block automated/headless access.
    These tests verify the script runs and returns proper JSON structure,
    but may not return actual results due to bot detection.
    """

    @pytest.mark.integration
    @pytest.mark.parametrize("backend", BACKENDS)
    def test_search_returns_valid_json(self, check_chrome, backend):
        """Test that search returns valid JSON structure for each backend."""
        result = run_script("search.py", [
            "--query", "test",
            "--engine", "bing",
            "--max-results", "3",
            "--headless",
            "--backend", backend,
        ], timeout=45)

        # Should always have these fields regardless of success
        assert "success" in result
        assert "query" in result
        assert "engine" in result
        assert "results" in result
        assert "metadata" in result
        assert isinstance(result["results"], list)

    @pytest.mark.integration
    @pytest.mark.parametrize("backend", BACKENDS)
    def test_search_metadata_structure(self, check_chrome, backend):
        """Test that search metadata has expected fields for each backend."""
        result = run_script("search.py", [
            "--query", "python",
            "--headless",
            "--backend", backend,
        ], timeout=45)

        assert "metadata" in result
        assert "search_time_ms" in result["metadata"]
        assert result["metadata"]["search_time_ms"] >= 0
        assert result["metadata"]["backend"] == backend

    @pytest.mark.integration
    @pytest.mark.parametrize("backend", BACKENDS)
    def test_search_results_structure_when_successful(self, check_chrome, backend):
        """Test result structure when search succeeds for each backend."""
        result = run_script("search.py", [
            "--query", "python",
            "--engine", "bing",
            "--headless",
            "--backend", backend,
        ], timeout=45)

        # Only validate structure if we got results
        if result["success"] and len(result["results"]) > 0:
            first_result = result["results"][0]
            assert "title" in first_result
            assert "url" in first_result
            assert "snippet" in first_result

    @pytest.mark.parametrize("backend", BACKENDS)
    def test_search_invalid_engine(self, backend):
        """Test with invalid search engine for each backend."""
        result = run_script("search.py", [
            "--query", "test",
            "--engine", "invalid_engine",
            "--backend", backend,
        ])

        # argparse should reject this - either error in result or stderr
        assert result.get("success") is False or "error" in str(result)

    @pytest.mark.integration
    def test_search_zendriver_fallback_to_selenium(self, check_chrome):
        """Test zendriver falls back to selenium for duckduckgo."""
        result = run_script("search.py", [
            "--query", "test",
            "--engine", "duckduckgo",
            "--backend", "zendriver",
            "--max-results", "3",
            "--headless",
        ], timeout=45)

        # Should work (falls back to selenium)
        assert "success" in result
        assert "results" in result
        # Fallback uses selenium backend
        assert result["metadata"]["backend"] == "selenium"


class TestZendriverSearches:
    """Extended tests specifically for zendriver backend searches."""

    @pytest.mark.integration
    def test_zendriver_google_search(self, check_chrome):
        """Test zendriver Google search returns results."""
        result = run_script("search.py", [
            "--query", "python programming language",
            "--engine", "google",
            "--max-results", "5",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        assert "success" in result
        assert "results" in result
        assert result["metadata"]["backend"] == "zendriver"
        # If successful, verify we got results
        if result["success"]:
            assert len(result["results"]) > 0
            assert len(result["results"]) <= 5

    @pytest.mark.integration
    def test_zendriver_bing_search(self, check_chrome):
        """Test zendriver Bing search returns results."""
        result = run_script("search.py", [
            "--query", "machine learning tutorial",
            "--engine", "bing",
            "--max-results", "5",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        assert "success" in result
        assert "results" in result
        assert result["metadata"]["backend"] == "zendriver"
        if result["success"]:
            assert len(result["results"]) > 0

    @pytest.mark.integration
    @pytest.mark.parametrize("query", [
        "weather today",
        "latest news",
        "how to cook pasta",
        "best programming languages 2024",
    ])
    def test_zendriver_various_queries(self, check_chrome, query):
        """Test zendriver with various search queries."""
        result = run_script("search.py", [
            "--query", query,
            "--engine", "bing",
            "--max-results", "3",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        assert "success" in result
        assert "query" in result
        assert result["query"] == query
        assert "results" in result
        assert isinstance(result["results"], list)

    @pytest.mark.integration
    def test_zendriver_search_max_results_limit(self, check_chrome):
        """Test that max-results parameter is respected."""
        result = run_script("search.py", [
            "--query", "python",
            "--engine", "bing",
            "--max-results", "2",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        assert "results" in result
        if result["success"] and len(result["results"]) > 0:
            assert len(result["results"]) <= 2

    @pytest.mark.integration
    def test_zendriver_search_special_characters(self, check_chrome):
        """Test zendriver handles queries with special characters."""
        result = run_script("search.py", [
            "--query", "C++ programming",
            "--engine", "bing",
            "--max-results", "3",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        assert "success" in result
        assert "results" in result
        # Query should be preserved
        assert "C++" in result["query"]

    @pytest.mark.integration
    def test_zendriver_search_quoted_query(self, check_chrome):
        """Test zendriver handles exact phrase queries."""
        result = run_script("search.py", [
            "--query", '"machine learning"',
            "--engine", "bing",
            "--max-results", "3",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        assert "success" in result
        assert "results" in result

    @pytest.mark.integration
    @pytest.mark.parametrize("engine", ["google", "bing"])
    def test_zendriver_result_urls_are_valid(self, check_chrome, engine):
        """Test that search results contain valid URLs."""
        result = run_script("search.py", [
            "--query", "python documentation",
            "--engine", engine,
            "--max-results", "5",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        if result["success"] and len(result["results"]) > 0:
            for item in result["results"]:
                assert "url" in item
                assert item["url"].startswith("http")
                # URL should not be a search engine URL
                assert "google.com/search" not in item["url"]
                assert "bing.com/search" not in item["url"]

    @pytest.mark.integration
    def test_zendriver_search_timing(self, check_chrome):
        """Test that search timing is recorded."""
        result = run_script("search.py", [
            "--query", "test query",
            "--engine", "bing",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        assert "metadata" in result
        assert "search_time_ms" in result["metadata"]
        # Search should complete in reasonable time (under 30 seconds)
        assert result["metadata"]["search_time_ms"] < 30000

    @pytest.mark.integration
    def test_zendriver_google_vs_bing_both_work(self, check_chrome):
        """Test that both Google and Bing work with zendriver."""
        google_result = run_script("search.py", [
            "--query", "test",
            "--engine", "google",
            "--max-results", "3",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        bing_result = run_script("search.py", [
            "--query", "test",
            "--engine", "bing",
            "--max-results", "3",
            "--headless",
            "--backend", "zendriver",
        ], timeout=60)

        # Both should return valid structure
        assert "success" in google_result
        assert "success" in bing_result
        assert google_result["engine"] == "google"
        assert bing_result["engine"] == "bing"


# Marker for integration tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
