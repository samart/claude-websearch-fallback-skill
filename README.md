# Claude WebSearch Fallback

A Claude Code skill that provides fallback web access when `WebSearch` and `WebFetch` tools fail due to HTTP errors (403, 404, proxy blocks, etc.).

## Why This Skill?

Claude Code's built-in `WebSearch` and `WebFetch` tools make requests from Anthropic's infrastructure, which can be blocked by:
- Corporate proxies and firewalls
- Geo-restrictions
- Sites with aggressive bot detection

This skill controls your local Chrome browser, which:
- Has your authenticated sessions (logged into sites)
- Works within your corporate firewall, were you have all your internal information (wikis, documentation sites, etc) needed by your agent to accomplish your work.
- Passes through your corporate proxy correctly, so that research can be informed with the latest search, all within your access profile
- Has your cookies and permissions
- Appears as legitimate browser traffic

## Backends

This skill supports two browser automation backends:

| Backend | Anti-Bot Success Rate | Architecture | Best For |
|---------|----------------------|--------------|----------|
| **zendriver** | **75%** | Chrome DevTools Protocol | Sites with bot detection, Cloudflare |
| selenium | 25% | WebDriver Protocol | General use, cross-browser |

**Recommendation**: Use `--backend zendriver` for sites that block automated requests.

## Quick Install

```bash
# Clone into your project's skills directory
mkdir -p .claude/skills && cd .claude/skills
git clone https://github.com/YOUR_USERNAME/websearch-fallback.git

# Install dependencies
cd websearch-fallback
pip install -r requirements.txt
```

## Requirements

- **Python 3.8+**
- **Chrome or Chromium browser** installed
- **ChromeDriver** (auto-managed by the skill)

## Usage

### Fetch a URL

```bash
# Using selenium (default)
python .claude/skills/websearch-fallback/fetch.py --url "https://example.com" --headless

# Using zendriver (better anti-bot bypass)
python .claude/skills/websearch-fallback/fetch.py --url "https://example.com" --headless --backend zendriver
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--url` | URL to fetch (required) | - |
| `--backend` | `selenium` or `zendriver` | selenium |
| `--headless` | Run without visible browser | false |
| `--timeout` | Page load timeout in seconds | 30 |
| `--wait` | Seconds to wait for JS to render | 2.0 |

**Output:**
```json
{
  "success": true,
  "url": "https://example.com",
  "final_url": "https://example.com/",
  "title": "Example Domain",
  "content": "# Example Domain\n\nMarkdown content...",
  "metadata": {"fetch_time_ms": 2340, "content_length": 167, "backend": "zendriver"},
  "error": null
}
```

### Search the Web

```bash
# Using selenium (default)
python .claude/skills/websearch-fallback/search.py --query "your search" --headless

# Using zendriver (better anti-bot bypass)
python .claude/skills/websearch-fallback/search.py --query "your search" --headless --backend zendriver
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--query` | Search query (required) | - |
| `--backend` | `selenium` or `zendriver` | selenium |
| `--engine` | `google`, `bing`, or `duckduckgo` | bing |
| `--max-results` | Maximum results to return | 10 |
| `--headless` | Run without visible browser | false |
| `--timeout` | Page load timeout in seconds | 30 |

**Output:**
```json
{
  "success": true,
  "query": "your search",
  "engine": "google",
  "results": [
    {"title": "Result Title", "url": "https://...", "snippet": "Description..."}
  ],
  "metadata": {"search_time_ms": 2800, "result_count": 3, "backend": "zendriver"},
  "error": null
}
```

## Search Engine Notes

| Engine | Headless Mode | Notes |
|--------|---------------|-------|
| **google** | Works | Best results, anti-detection enabled |
| **bing** | Works | Reliable fallback |
| duckduckgo | Unreliable | JS-heavy, sometimes blocked |

## How the Backends Work

### Selenium Backend
Uses `undetected-chromedriver` to patch standard Selenium WebDriver:
- Removes automation indicators (`navigator.webdriver`)
- Sets realistic user-agent and window size
- Disables automation-revealing Chrome flags

### Zendriver Backend
Successor to undetected-chromedriver, communicates directly via Chrome DevTools Protocol:
- Completely bypasses WebDriver architecture
- Async-first design for better performance
- Higher success rate against Cloudflare, Akamai, and other anti-bot systems
- No WebDriver/Selenium dependency in the request chain

## Using with Your Browser Profile

To use your logged-in sessions (cookies, authentication):

1. **Close Chrome completely** (the profile is locked while Chrome runs)
2. Run without `--headless` flag:
   ```bash
   python search.py --query "internal docs" --engine google
   ```

This opens a visible Chrome window using your default profile with all your cookies and sessions.

## Running Tests

```bash
pip install pytest

# Unit tests
pytest tests/test_converter.py -v

# Integration tests (requires Chrome)
pytest tests/test_integration.py -v --run-integration
```

## Project Structure

```
websearch-fallback/
├── fetch.py                    # URL fetching CLI
├── search.py                   # Web search CLI
├── skill.md                    # Claude Code skill manifest
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── lib/
│   ├── driver.py               # Selenium backend (undetected-chromedriver)
│   ├── zendriver_backend.py    # Zendriver backend (CDP-based)
│   └── converter.py            # HTML → Markdown conversion
└── tests/
    ├── test_converter.py       # Unit tests
    └── test_integration.py     # Integration tests
```

## Troubleshooting

### "session not created" error
Chrome is already running with your profile. Close Chrome and try again.

### CAPTCHA appears
Try `--backend zendriver` for better anti-bot bypass. If still blocked, wait a few minutes or use a different search engine.

### ChromeDriver version mismatch
The skill auto-downloads the correct ChromeDriver version via `webdriver-manager`.

### Zendriver fails to start
Ensure Chrome is installed. Zendriver requires Chrome/Chromium (not just ChromeDriver).

## License

MIT License - See LICENSE file for details.
