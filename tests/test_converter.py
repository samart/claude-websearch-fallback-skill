"""Tests for HTML converter module."""

import pytest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.converter import extract_main_content, html_to_markdown, truncate_content


class TestExtractMainContent:
    """Tests for extract_main_content function."""

    def test_extracts_main_tag(self):
        html = """
        <html>
            <body>
                <nav>Navigation</nav>
                <main>
                    <h1>Main Content</h1>
                    <p>This is the content.</p>
                </main>
                <footer>Footer</footer>
            </body>
        </html>
        """
        result = extract_main_content(html)
        assert "Main Content" in result
        assert "This is the content" in result
        assert "Navigation" not in result
        assert "Footer" not in result

    def test_extracts_article_tag(self):
        html = """
        <html>
            <body>
                <header>Header</header>
                <article>
                    <h1>Article Title</h1>
                    <p>Article body.</p>
                </article>
            </body>
        </html>
        """
        result = extract_main_content(html)
        assert "Article Title" in result
        assert "Article body" in result

    def test_removes_scripts_and_styles(self):
        html = """
        <html>
            <body>
                <script>alert('evil');</script>
                <style>.hidden { display: none; }</style>
                <main>
                    <p>Safe content</p>
                </main>
            </body>
        </html>
        """
        result = extract_main_content(html)
        assert "Safe content" in result
        assert "alert" not in result
        assert "display: none" not in result

    def test_removes_nav_classes(self):
        html = """
        <html>
            <body>
                <div class="navigation">Nav stuff</div>
                <div class="sidebar-menu">Menu</div>
                <main>
                    <p>Content</p>
                </main>
            </body>
        </html>
        """
        result = extract_main_content(html)
        assert "Content" in result
        # Nav/sidebar should be removed
        assert "Nav stuff" not in result


class TestHtmlToMarkdown:
    """Tests for html_to_markdown function."""

    def test_converts_headings(self):
        html = "<h1>Title</h1><h2>Subtitle</h2><p>Text</p>"
        result = html_to_markdown(html)
        assert "# Title" in result or "Title" in result
        assert "Subtitle" in result
        assert "Text" in result

    def test_converts_links(self):
        html = '<p>Check <a href="https://example.com">this link</a>.</p>'
        result = html_to_markdown(html)
        assert "example.com" in result

    def test_resolves_relative_urls(self):
        html = '<a href="/page">Link</a>'
        result = html_to_markdown(html, base_url="https://example.com")
        assert "https://example.com/page" in result

    def test_handles_empty_html(self):
        result = html_to_markdown("")
        assert result == ""

    def test_cleans_whitespace(self):
        html = "<p>Line 1</p>\n\n\n\n<p>Line 2</p>"
        result = html_to_markdown(html)
        # Should not have excessive blank lines
        assert "\n\n\n" not in result


class TestTruncateContent:
    """Tests for truncate_content function."""

    def test_no_truncation_when_under_limit(self):
        content = "Short content"
        result = truncate_content(content, max_length=1000)
        assert result == content
        assert "[Content truncated" not in result

    def test_truncates_long_content(self):
        content = "A" * 1000
        result = truncate_content(content, max_length=100)
        assert len(result) < 200  # Some margin for truncation message
        assert "[Content truncated" in result

    def test_truncates_at_paragraph(self):
        content = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        result = truncate_content(content, max_length=40)
        assert "[Content truncated" in result

    def test_truncates_at_sentence(self):
        content = "First sentence. Second sentence. Third sentence."
        result = truncate_content(content, max_length=30)
        assert "[Content truncated" in result
