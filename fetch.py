#!/usr/bin/env python3
"""
Fetch a URL using browser automation and return content as markdown.

Usage:
    python fetch.py --url "https://example.com" --headless
    python fetch.py --url "https://example.com" --headless --backend zendriver
"""

import argparse
import json
import sys

# Add lib to path
sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

# Backend registry
BACKENDS = {
    "selenium": "lib.selenium_backend",
    "zendriver": "lib.zendriver_backend",
}


def get_backend(name: str):
    """Import and return the backend module."""
    if name == "selenium":
        from lib import selenium_backend
        return selenium_backend
    elif name == "zendriver":
        from lib import zendriver_backend
        return zendriver_backend
    else:
        raise ValueError(f"Unknown backend: {name}. Use: {list(BACKENDS.keys())}")


def main():
    parser = argparse.ArgumentParser(description="Fetch URL via browser automation")
    parser.add_argument("--url", required=True, help="URL to fetch")
    parser.add_argument("--backend", choices=list(BACKENDS.keys()), default="selenium",
                        help="Backend to use (default: selenium)")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout seconds")
    parser.add_argument("--wait", type=float, default=2.0, help="JS wait seconds")
    parser.add_argument("--max-length", type=int, default=50000, help="Max content length")

    args = parser.parse_args()

    backend = get_backend(args.backend)

    # Zendriver uses fetch_page_sync, selenium uses fetch_page
    if args.backend == "zendriver":
        result = backend.fetch_page_sync(
            url=args.url,
            headless=args.headless,
            timeout=args.timeout,
            wait=args.wait,
        )
        # Apply truncation
        if result.get("content"):
            from lib.converter import truncate_content
            result["content"] = truncate_content(result["content"], args.max_length)
    else:
        result = backend.fetch_page(
            url=args.url,
            headless=args.headless,
            timeout=args.timeout,
            wait=args.wait,
            max_content_length=args.max_length,
        )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
