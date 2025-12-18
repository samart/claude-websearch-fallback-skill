---
name: websearch-fallback
description: Fetches web pages and performs web searches using local Chrome browser. Use when WebSearch or WebFetch tools fail with HTTP errors (403, 404, proxy blocks), when accessing sites behind corporate firewalls, or when the user needs to search using their authenticated browser sessions.
---

# WebSearch Fallback

Provides web access via local Chrome browser when built-in tools fail.

## Quick Start

**Fetch a URL:**
```bash
python .claude/skills/websearch-fallback/fetch.py --url "URL" --headless
```

**Search the web:**
```bash
python .claude/skills/websearch-fallback/search.py --query "QUERY" --headless
```

## Fetch Options

| Option | Default |
|--------|---------|
| `--url` | required |
| `--headless` | false |
| `--timeout` | 30 |
| `--wait` | 2.0 |

## Search Options

| Option | Default |
|--------|---------|
| `--query` | required |
| `--engine` | bing |
| `--max-results` | 10 |
| `--headless` | false |lets 

## Output

Both scripts return JSON to stdout:

```json
{
  "success": true,
  "content": "# Page content as markdown...",
  "metadata": {"fetch_time_ms": 2340},
  "error": null
}
```

## When to Use

- WebSearch/WebFetch returns 403, 404, or proxy errors
- Accessing internal wikis or documentation behind VPN
- Sites with aggressive bot detection
- User needs their authenticated sessions (cookies, logins)

## Installation

```bash
git clone https://github.com/samart/claude-websearch-fallback-skill.git .claude/skills/websearch-fallback
pip install -r .claude/skills/websearch-fallback/requirements.txt
```

Requires: Python 3.8+, Chrome/Chromium (ChromeDriver auto-managed)
