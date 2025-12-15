"""Selenium backend for browser automation using undetected-chromedriver."""

import time
from typing import Any

from .driver import create_driver
from .converter import extract_main_content, html_to_markdown, truncate_content


def fetch_page(
    url: str,
    headless: bool = False,
    timeout: int = 30,
    wait: float = 2.0,
    max_content_length: int = 50000,
) -> dict[str, Any]:
    """
    Fetch a URL using Selenium + undetected-chromedriver.

    Args:
        url: URL to fetch.
        headless: Run in headless mode.
        timeout: Page load timeout in seconds.
        wait: Seconds to wait for JavaScript to render.
        max_content_length: Maximum content length before truncation.

    Returns:
        Dictionary with page content and metadata.
    """
    result = {
        "success": False,
        "url": url,
        "final_url": None,
        "title": None,
        "content": None,
        "metadata": {},
        "error": None,
    }

    driver = None
    start_time = time.time()

    try:
        driver = create_driver(headless=headless, timeout=timeout)
        driver.get(url)

        if wait > 0:
            time.sleep(wait)

        result["final_url"] = driver.current_url
        result["title"] = driver.title

        html = driver.page_source
        main_content = extract_main_content(html)
        markdown = html_to_markdown(main_content, base_url=result["final_url"])
        markdown = truncate_content(markdown, max_content_length)

        result["content"] = markdown
        result["success"] = True
        result["metadata"] = {
            "fetch_time_ms": int((time.time() - start_time) * 1000),
            "content_length": len(markdown),
            "html_length": len(html),
            "backend": "selenium",
        }

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["metadata"]["fetch_time_ms"] = int((time.time() - start_time) * 1000)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return result


def search_google(
    query: str,
    max_results: int = 10,
    headless: bool = False,
    timeout: int = 30,
) -> dict[str, Any]:
    """Perform Google search using Selenium."""
    from urllib.parse import quote_plus
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    result = {
        "success": False,
        "query": query,
        "engine": "google",
        "results": [],
        "metadata": {},
        "error": None,
    }

    driver = None
    start_time = time.time()
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"

    try:
        driver = create_driver(headless=headless, timeout=timeout)
        driver.get(search_url)

        # Wait for results
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h3"))
            )
            time.sleep(1)
        except Exception:
            pass

        # Parse results
        results = []
        h3_elements = driver.find_elements(By.CSS_SELECTOR, "h3")

        for h3 in h3_elements[:max_results * 2]:
            try:
                title = h3.text.strip()
                if not title:
                    continue

                try:
                    link_elem = h3.find_element(By.XPATH, "./ancestor::a")
                    url = link_elem.get_attribute("href")
                except Exception:
                    try:
                        parent = h3.find_element(By.XPATH, "./..")
                        link_elem = parent.find_element(By.CSS_SELECTOR, "a")
                        url = link_elem.get_attribute("href")
                    except Exception:
                        continue

                if not url or "google.com" in url:
                    continue

                snippet = ""
                try:
                    container = h3.find_element(By.XPATH, "./ancestor::div[contains(@class, 'g') or contains(@data-hveid, '')]")
                    for selector in ["div[data-sncf]", "div.VwiC3b", "span.aCOpRe", "div > span"]:
                        try:
                            snippet_elem = container.find_element(By.CSS_SELECTOR, selector)
                            snippet = snippet_elem.text.strip()
                            if snippet and len(snippet) > 20:
                                break
                        except Exception:
                            continue
                except Exception:
                    pass

                results.append({"title": title, "url": url, "snippet": snippet})
                if len(results) >= max_results:
                    break
            except Exception:
                continue

        result["results"] = results
        result["success"] = len(results) > 0
        result["metadata"] = {
            "search_time_ms": int((time.time() - start_time) * 1000),
            "result_count": len(results),
            "backend": "selenium",
        }

        if not results:
            result["error"] = "No results found"

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["metadata"]["search_time_ms"] = int((time.time() - start_time) * 1000)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return result


def search_bing(
    query: str,
    max_results: int = 10,
    headless: bool = False,
    timeout: int = 30,
) -> dict[str, Any]:
    """Perform Bing search using Selenium."""
    from urllib.parse import quote_plus
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    result = {
        "success": False,
        "query": query,
        "engine": "bing",
        "results": [],
        "metadata": {},
        "error": None,
    }

    driver = None
    start_time = time.time()
    search_url = f"https://www.bing.com/search?q={quote_plus(query)}"

    try:
        driver = create_driver(headless=headless, timeout=timeout)
        driver.get(search_url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.b_algo"))
            )
        except Exception:
            pass

        results = []
        elements = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")

        for elem in elements[:max_results]:
            try:
                title_elem = elem.find_element(By.CSS_SELECTOR, "h2 a")
                title = title_elem.text.strip()
                url = title_elem.get_attribute("href")

                snippet = ""
                try:
                    snippet_elem = elem.find_element(By.CSS_SELECTOR, "p")
                    snippet = snippet_elem.text.strip()
                except Exception:
                    pass

                if title and url:
                    results.append({"title": title, "url": url, "snippet": snippet})
            except Exception:
                continue

        result["results"] = results
        result["success"] = len(results) > 0
        result["metadata"] = {
            "search_time_ms": int((time.time() - start_time) * 1000),
            "result_count": len(results),
            "backend": "selenium",
        }

        if not results:
            result["error"] = "No results found"

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["metadata"]["search_time_ms"] = int((time.time() - start_time) * 1000)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return result


def search_duckduckgo(
    query: str,
    max_results: int = 10,
    headless: bool = False,
    timeout: int = 30,
) -> dict[str, Any]:
    """Perform DuckDuckGo search using Selenium."""
    from urllib.parse import quote_plus
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    result = {
        "success": False,
        "query": query,
        "engine": "duckduckgo",
        "results": [],
        "metadata": {},
        "error": None,
    }

    driver = None
    start_time = time.time()
    search_url = f"https://duckduckgo.com/?q={quote_plus(query)}"

    try:
        driver = create_driver(headless=headless, timeout=timeout)
        driver.get(search_url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
            )
            time.sleep(1)
        except Exception:
            pass

        results = []
        elements = driver.find_elements(By.CSS_SELECTOR, "article")

        for elem in elements[:max_results]:
            try:
                title_elem = elem.find_element(By.CSS_SELECTOR, "h2")
                link_elem = elem.find_element(By.CSS_SELECTOR, "a")

                title = title_elem.text.strip()
                url = link_elem.get_attribute("href")

                snippet = ""
                try:
                    snippet_elem = elem.find_element(By.CSS_SELECTOR, "div[data-result='snippet']")
                    snippet = snippet_elem.text.strip()
                except Exception:
                    pass

                if title and url:
                    results.append({"title": title, "url": url, "snippet": snippet})
            except Exception:
                continue

        result["results"] = results
        result["success"] = len(results) > 0
        result["metadata"] = {
            "search_time_ms": int((time.time() - start_time) * 1000),
            "result_count": len(results),
            "backend": "selenium",
        }

        if not results:
            result["error"] = "No results found"

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["metadata"]["search_time_ms"] = int((time.time() - start_time) * 1000)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return result
