"""HTML content extraction and markdown conversion."""

import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag


# Elements to remove (navigation, ads, etc.)
REMOVE_TAGS = [
    "script", "style", "nav", "header", "footer", "aside",
    "noscript", "iframe", "form", "button", "input",
]

# IDs/classes that typically indicate non-content
REMOVE_PATTERNS = [
    r"nav", r"menu", r"sidebar", r"footer", r"header", r"cookie",
    r"banner", r"advertisement", r"social", r"comment", r"related",
]


def extract_main_content(html: str) -> str:
    """
    Extract the main content area from HTML.

    Tries semantic elements first, then falls back to heuristics.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for tag_name in REMOVE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Remove elements with nav/menu/sidebar-like IDs or classes
    for pattern in REMOVE_PATTERNS:
        regex = re.compile(pattern, re.I)
        for tag in soup.find_all(id=regex):
            tag.decompose()
        for tag in soup.find_all(class_=regex):
            tag.decompose()

    # Try to find main content container
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(role="main")
        or soup.find(id="content")
        or soup.find(id="main")
        or soup.find(id="main-content")
        or soup.find(class_="content")
        or soup.find(class_="post")
        or soup.find(class_="article")
    )

    if main:
        return str(main)

    # Fallback: return body or full soup
    body = soup.find("body")
    return str(body) if body else str(soup)


def html_to_markdown(html: str, base_url: Optional[str] = None) -> str:
    """
    Convert HTML to clean markdown.

    Args:
        html: HTML content to convert.
        base_url: Base URL for resolving relative links.

    Returns:
        Markdown string.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Resolve relative URLs if base_url provided
    if base_url:
        for tag in soup.find_all("a", href=True):
            tag["href"] = urljoin(base_url, tag["href"])
        for tag in soup.find_all("img", src=True):
            tag["src"] = urljoin(base_url, tag["src"])

    # Use markdownify if available, otherwise simple conversion
    try:
        from markdownify import markdownify as md
        markdown = md(str(soup), heading_style="ATX", strip=["img"])
    except ImportError:
        markdown = _simple_html_to_markdown(soup)

    # Clean up whitespace
    lines = markdown.split("\n")
    cleaned = []
    prev_empty = False

    for line in lines:
        line = line.rstrip()
        is_empty = not line.strip()

        # Skip consecutive empty lines
        if is_empty and prev_empty:
            continue

        cleaned.append(line)
        prev_empty = is_empty

    return "\n".join(cleaned).strip()


def _simple_html_to_markdown(soup: BeautifulSoup) -> str:
    """Simple fallback HTML to markdown converter."""
    result = []

    for element in soup.descendants:
        if isinstance(element, str):
            text = element.strip()
            if text:
                result.append(text)
        elif isinstance(element, Tag):
            name = element.name

            if name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(name[1])
                text = element.get_text(strip=True)
                if text:
                    result.append(f"\n{'#' * level} {text}\n")
            elif name == "p":
                text = element.get_text(strip=True)
                if text:
                    result.append(f"\n{text}\n")
            elif name == "a":
                href = element.get("href", "")
                text = element.get_text(strip=True)
                if text and href:
                    result.append(f"[{text}]({href})")
            elif name == "li":
                text = element.get_text(strip=True)
                if text:
                    result.append(f"- {text}")
            elif name == "pre" or name == "code":
                text = element.get_text()
                if text:
                    result.append(f"\n```\n{text}\n```\n")
            elif name == "br":
                result.append("\n")

    return "\n".join(result)


def truncate_content(content: str, max_length: int = 50000) -> str:
    """Truncate content intelligently at paragraph boundaries."""
    if len(content) <= max_length:
        return content

    # Find a good breakpoint
    truncated = content[:max_length]

    # Try to break at paragraph
    last_para = truncated.rfind("\n\n")
    if last_para > max_length * 0.8:
        truncated = truncated[:last_para]
    else:
        # Break at sentence
        last_sentence = max(
            truncated.rfind(". "),
            truncated.rfind(".\n"),
            truncated.rfind("? "),
            truncated.rfind("! "),
        )
        if last_sentence > max_length * 0.8:
            truncated = truncated[:last_sentence + 1]

    return truncated + "\n\n[Content truncated...]"
