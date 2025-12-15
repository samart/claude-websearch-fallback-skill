"""Zendriver backend for browser automation with superior anti-bot bypass."""

import asyncio
from typing import Optional

import zendriver as zd


async def create_browser(
    headless: bool = True,
    timeout: int = 30,
) -> zd.Browser:
    """
    Create a Zendriver browser instance.

    Args:
        headless: Run in headless mode (no visible window).
        timeout: Page load timeout in seconds.

    Returns:
        Configured Zendriver browser instance.
    """
    browser = await zd.start(
        headless=headless,
        sandbox=False,
    )
    return browser


async def fetch_page(
    url: str,
    headless: bool = True,
    timeout: int = 30,
    wait: float = 2.0,
) -> dict:
    """
    Fetch a URL using Zendriver.

    Args:
        url: URL to fetch.
        headless: Run in headless mode.
        timeout: Page load timeout in seconds.
        wait: Seconds to wait for JavaScript to render.

    Returns:
        Dictionary with page content and metadata.
    """
    import time
    from .converter import extract_main_content, html_to_markdown

    result = {
        "success": False,
        "url": url,
        "final_url": None,
        "title": None,
        "content": None,
        "metadata": {},
        "error": None,
    }

    start_time = time.time()
    browser = None

    try:
        browser = await create_browser(headless=headless, timeout=timeout)
        page = await browser.get(url)

        # Wait for page to render
        await asyncio.sleep(wait)

        # Get page info
        result["final_url"] = page.url
        result["title"] = await page.evaluate("document.title")

        # Get HTML content
        html = await page.evaluate("document.documentElement.outerHTML")

        # Convert to markdown
        main_content = extract_main_content(html)
        markdown = html_to_markdown(main_content)

        result["content"] = markdown
        result["success"] = True
        result["metadata"] = {
            "fetch_time_ms": int((time.time() - start_time) * 1000),
            "content_length": len(markdown),
            "backend": "zendriver",
        }

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["metadata"]["fetch_time_ms"] = int((time.time() - start_time) * 1000)

    finally:
        if browser:
            try:
                await browser.stop()
            except Exception:
                pass

    return result


async def search_google(
    query: str,
    max_results: int = 10,
    headless: bool = True,
    timeout: int = 30,
) -> dict:
    """
    Perform a Google search using Zendriver.

    Args:
        query: Search query.
        max_results: Maximum number of results to return.
        headless: Run in headless mode.
        timeout: Page load timeout in seconds.

    Returns:
        Dictionary with search results.
    """
    import time
    from urllib.parse import quote_plus

    result = {
        "success": False,
        "query": query,
        "engine": "google",
        "results": [],
        "metadata": {},
        "error": None,
    }

    start_time = time.time()
    browser = None
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"

    try:
        browser = await create_browser(headless=headless, timeout=timeout)
        page = await browser.get(search_url)

        # Wait for results to load
        await asyncio.sleep(2)

        # Parse results using JavaScript
        results = await page.evaluate("""
            (() => {
                const results = [];
                const h3s = document.querySelectorAll('h3');

                for (const h3 of h3s) {
                    const title = h3.textContent?.trim();
                    if (!title) continue;

                    // Find parent link
                    let link = h3.closest('a');
                    if (!link) {
                        link = h3.parentElement?.querySelector('a');
                    }
                    if (!link) continue;

                    const url = link.href;
                    if (!url || url.includes('google.com')) continue;

                    // Find snippet
                    let snippet = '';
                    const container = h3.closest('div[data-hveid]') || h3.closest('.g');
                    if (container) {
                        const snippetEl = container.querySelector('div[data-sncf], div.VwiC3b, span.aCOpRe');
                        if (snippetEl) {
                            snippet = snippetEl.textContent?.trim() || '';
                        }
                    }

                    results.push({ title, url, snippet });
                }

                return results;
            })()
        """)

        # Ensure results is a list
        if not isinstance(results, list):
            results = []
        result["results"] = results[:max_results]
        result["success"] = len(results) > 0
        result["metadata"] = {
            "search_time_ms": int((time.time() - start_time) * 1000),
            "result_count": len(result["results"]),
            "backend": "zendriver",
        }

        if not results:
            result["error"] = "No results found"

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["metadata"]["search_time_ms"] = int((time.time() - start_time) * 1000)

    finally:
        if browser:
            try:
                await browser.stop()
            except Exception:
                pass

    return result


async def search_bing(
    query: str,
    max_results: int = 10,
    headless: bool = True,
    timeout: int = 30,
) -> dict:
    """
    Perform a Bing search using Zendriver.

    Args:
        query: Search query.
        max_results: Maximum number of results to return.
        headless: Run in headless mode.
        timeout: Page load timeout in seconds.

    Returns:
        Dictionary with search results.
    """
    import time
    from urllib.parse import quote_plus

    result = {
        "success": False,
        "query": query,
        "engine": "bing",
        "results": [],
        "metadata": {},
        "error": None,
    }

    start_time = time.time()
    browser = None
    search_url = f"https://www.bing.com/search?q={quote_plus(query)}"

    try:
        browser = await create_browser(headless=headless, timeout=timeout)
        page = await browser.get(search_url)

        # Wait for results to load
        await asyncio.sleep(2)

        # Parse results using JavaScript
        results = await page.evaluate("""
            (() => {
                const results = [];
                const items = document.querySelectorAll('li.b_algo');

                for (const item of items) {
                    const titleEl = item.querySelector('h2 a');
                    if (!titleEl) continue;

                    const title = titleEl.textContent?.trim();
                    const url = titleEl.href;

                    if (!title || !url) continue;

                    let snippet = '';
                    const snippetEl = item.querySelector('p');
                    if (snippetEl) {
                        snippet = snippetEl.textContent?.trim() || '';
                    }

                    results.push({ title, url, snippet });
                }

                return results;
            })()
        """)

        # Ensure results is a list
        if not isinstance(results, list):
            results = []
        result["results"] = results[:max_results]
        result["success"] = len(results) > 0
        result["metadata"] = {
            "search_time_ms": int((time.time() - start_time) * 1000),
            "result_count": len(result["results"]),
            "backend": "zendriver",
        }

        if not results:
            result["error"] = "No results found"

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["metadata"]["search_time_ms"] = int((time.time() - start_time) * 1000)

    finally:
        if browser:
            try:
                await browser.stop()
            except Exception:
                pass

    return result


# Synchronous wrappers for CLI usage
def fetch_page_sync(url: str, headless: bool = True, timeout: int = 30, wait: float = 2.0) -> dict:
    """Synchronous wrapper for fetch_page."""
    return asyncio.run(fetch_page(url, headless, timeout, wait))


def search_google_sync(query: str, max_results: int = 10, headless: bool = True, timeout: int = 30) -> dict:
    """Synchronous wrapper for search_google."""
    return asyncio.run(search_google(query, max_results, headless, timeout))


def search_bing_sync(query: str, max_results: int = 10, headless: bool = True, timeout: int = 30) -> dict:
    """Synchronous wrapper for search_bing."""
    return asyncio.run(search_bing(query, max_results, headless, timeout))
