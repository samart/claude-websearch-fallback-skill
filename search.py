#!/usr/bin/env python3
"""
Perform web search using browser automation and return structured results.

Usage:
    python search.py --query "python tutorial" --headless
    python search.py --query "python tutorial" --engine google --headless --backend zendriver

Zendriver backend has 75% anti-bot success rate vs 25% for Selenium.
"""

import argparse
import json
import sys

# Add lib to path
sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

BACKENDS = ["selenium", "zendriver"]
ENGINES = ["google", "bing", "duckduckgo"]


def search_with_selenium(query: str, engine: str, max_results: int, headless: bool, timeout: int) -> dict:
    """Run search using selenium backend."""
    from lib import selenium_backend

    if engine == "google":
        return selenium_backend.search_google(query, max_results, headless, timeout)
    elif engine == "bing":
        return selenium_backend.search_bing(query, max_results, headless, timeout)
    elif engine == "duckduckgo":
        return selenium_backend.search_duckduckgo(query, max_results, headless, timeout)
    else:
        return {"success": False, "error": f"Unknown engine: {engine}"}


def search_with_zendriver(query: str, engine: str, max_results: int, headless: bool, timeout: int) -> dict:
    """Run search using zendriver backend."""
    from lib import zendriver_backend

    if engine == "google":
        return zendriver_backend.search_google_sync(query, max_results, headless, timeout)
    elif engine == "bing":
        return zendriver_backend.search_bing_sync(query, max_results, headless, timeout)
    else:
        # Fallback to selenium for unsupported engines
        return search_with_selenium(query, engine, max_results, headless, timeout)


def main():
    parser = argparse.ArgumentParser(description="Web search via browser automation")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--backend", choices=BACKENDS, default="zendriver",
                        help="Backend to use (default: zendriver)")
    parser.add_argument("--engine", choices=ENGINES, default="bing",
                        help="Search engine (default: bing)")
    parser.add_argument("--max-results", type=int, default=10, help="Max results")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout seconds")

    args = parser.parse_args()

    if args.backend == "zendriver":
        result = search_with_zendriver(
            args.query, args.engine, args.max_results, args.headless, args.timeout
        )
    else:
        result = search_with_selenium(
            args.query, args.engine, args.max_results, args.headless, args.timeout
        )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
