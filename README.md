<img src="logo.svg" align="right" width="200" height="200" alt="Claude WebSearch Fallback Logo">

# Claude WebSearch Fallback

A Claude Code skill that ensures Claude's web research capabilities always work—even when the built-in tools fail.

## Why This Matters

Claude's ability to research, plan, and gather current information is core to its effectiveness as a coding assistant. When `WebSearch` or `WebFetch` tools fail (403 errors, proxy blocks, geo-restrictions), Claude loses access to:

- Current documentation and API references
- Stack Overflow solutions and community knowledge
- Latest library versions and changelogs
- Your internal wikis and documentation

**This skill ensures Claude can always research on your behalf.**

## How It Works

Instead of making requests from Anthropic's infrastructure (which can be blocked), this skill controls **your local Chrome browser**. This means:

- **Your access, your permissions** — Claude searches as you, with your authenticated sessions
- **Corporate firewall friendly** — Access internal wikis, documentation, and tools behind your VPN
- **No additional credentials needed** — Uses your existing browser cookies and logins
- **Appears as legitimate traffic** — Because it is—it's your browser

## Test Coverage

```
55 tests | 40% code coverage | All passing
```

## Quick Install

```bash
# Clone into your project's skills directory
mkdir -p .claude/skills && cd .claude/skills
git clone https://github.com/samart/claude-websearch-fallback-skill.git websearch-fallback

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
# Using zendriver (default - better anti-bot bypass)
python .claude/skills/websearch-fallback/fetch.py --url "https://example.com" --headless

# Using selenium (legacy)
python .claude/skills/websearch-fallback/fetch.py --url "https://example.com" --headless --backend selenium
```

| Option | Default |
|--------|---------|
| `--url` | required |
| `--backend` | zendriver |
| `--headless` | false |
| `--timeout` | 30s |
| `--wait` | 2.0s |

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
# Using zendriver (default - better anti-bot bypass)
python .claude/skills/websearch-fallback/search.py --query "your search" --headless

# Using selenium (legacy)
python .claude/skills/websearch-fallback/search.py --query "your search" --headless --backend selenium
```

| Option | Default |
|--------|---------|
| `--query` | required |
| `--backend` | zendriver |
| `--engine` | bing |
| `--max-results` | 10 |
| `--headless` | false |
| `--timeout` | 30s |

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

## Search Engines

| Engine | Reliability | Notes |
|--------|-------------|-------|
| **bing** | High | Default, most reliable |
| **google** | High | Best results quality |
| duckduckgo | Low | JS-heavy, often blocked |

## Using Your Authenticated Sessions

To access sites you're logged into (internal wikis, private repos, etc.):

1. **Close Chrome completely** (the profile is locked while Chrome runs)
2. Run without `--headless`:

   ```bash
   python search.py --query "internal docs" --engine google
   ```

This opens Chrome with your default profile—all your cookies, sessions, and logins work automatically.

## Backend Details

The skill includes two browser automation backends:

| Backend | Description |
|---------|-------------|
| **zendriver** (default) | Uses Chrome DevTools Protocol directly. Better anti-bot bypass, higher success rate against Cloudflare/Akamai. |
| selenium | Uses WebDriver with undetected-chromedriver patches. More mature, wider compatibility. |

## Running Tests

```bash
pip install pytest pytest-cov

# Unit tests only
pytest tests/test_converter.py tests/test_backends.py -v

# All tests including integration (requires Chrome)
pytest --run-integration -v

# With coverage
pytest --cov=lib --run-integration
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

| Issue | Solution |
|-------|----------|
| "session not created" error | Close Chrome completely—the profile is locked while Chrome runs |
| CAPTCHA appears | Try a different search engine, or wait a few minutes |
| ChromeDriver version mismatch | The skill auto-downloads the correct version via `webdriver-manager` |
| Zendriver fails to start | Ensure Chrome/Chromium is installed (not just ChromeDriver) |

## License

MIT License
