# Claude WebSearch Fallback

Use this skill when `WebSearch` or `WebFetch` tools fail with HTTP errors (403, 404, proxy blocks).

This skill controls your local Chrome browser, which inherits your:
- Authenticated sessions (logged into sites)
- Corporate proxy settings
- Cookies and permissions

## Backends

| Backend | Anti-Bot Success | Best For |
|---------|-----------------|----------|
| **zendriver** | 75% | Sites with aggressive bot detection |
| selenium | 25% | General use, legacy compatibility |

## Installation

```bash
git clone https://github.com/samart/claude-websearch-fallback-skill.git .claude/skills/websearch-fallback
pip install -r .claude/skills/websearch-fallback/requirements.txt
```

## Commands

### Fetch a URL

```bash
# Default (zendriver backend - better anti-bot bypass)
python .claude/skills/websearch-fallback/fetch.py --url "URL_HERE" --headless

# Selenium backend (legacy)
python .claude/skills/websearch-fallback/fetch.py --url "URL_HERE" --headless --backend selenium
```

Options:
- `--backend zendriver|selenium` - Backend to use (default: zendriver)
- `--headless` - Run without visible browser window (recommended)
- `--timeout 30` - Page load timeout in seconds
- `--wait 2.0` - Seconds to wait for JavaScript to render

### Search the Web

```bash
# Default (zendriver backend - better anti-bot bypass)
python .claude/skills/websearch-fallback/search.py --query "SEARCH_QUERY" --headless

# Selenium backend (legacy)
python .claude/skills/websearch-fallback/search.py --query "SEARCH_QUERY" --headless --backend selenium
```

Options:
- `--backend zendriver|selenium` - Backend to use (default: zendriver)
- `--engine google|bing|duckduckgo` - Search engine (default: bing)
- `--max-results 10` - Maximum results to return
- `--headless` - Run without visible browser window (recommended)

## When to Use Selenium

Use `--backend selenium` when:
- Zendriver has compatibility issues
- You need DuckDuckGo search (auto-fallback)
- Legacy compatibility is required

Zendriver (default) bypasses more anti-bot systems by communicating directly with Chrome via DevTools Protocol instead of WebDriver.

## Output Format

Both scripts output JSON to stdout:

### Fetch Output
```json
{
  "success": true,
  "url": "https://example.com",
  "final_url": "https://example.com/",
  "title": "Page Title",
  "content": "# Page Title\n\nMarkdown content...",
  "metadata": {"fetch_time_ms": 2340, "content_length": 4521, "backend": "zendriver"},
  "error": null
}
```

### Search Output
```json
{
  "success": true,
  "query": "search terms",
  "engine": "google",
  "results": [
    {"title": "Result Title", "url": "https://example.com", "snippet": "Description..."}
  ],
  "metadata": {"search_time_ms": 2800, "result_count": 3, "backend": "zendriver"},
  "error": null
}
```

## Requirements

- Python 3.8+
- Chrome or Chromium browser
- ChromeDriver (auto-managed)
