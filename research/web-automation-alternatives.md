# Web Automation Alternatives Research

> Research conducted December 2024 for Claude WebSearch Fallback skill

## Executive Summary

When bypassing bot detection, there are three main categories of tools:

| Category | Best For | Anti-Bot Success Rate |
|----------|----------|----------------------|
| **CDP-Based** (Nodriver/Zendriver) | Advanced anti-bot bypass | 75% |
| **HTTP Clients** (curl_cffi) | Speed, no JavaScript needed | Moderate (basic protections) |
| **Browser Automation** (Playwright/Selenium) | Cross-browser, enterprise | 25% (without stealth plugins) |

**Key finding**: The Nodriver/Zendriver family currently achieves the highest success rates against anti-bot systems (75%), compared to 25% for vanilla Selenium/Playwright.

---

## 1. Browser Automation Tools (Full Browser)

### 1.1 Playwright

**Overview**: Microsoft's browser automation library using the Chrome DevTools Protocol (CDP) with persistent WebSocket connections.

**Pros**:
- 35% faster than Selenium on average (1.8s vs 2.7s page navigation)
- 20-30% less memory and CPU usage
- Native network interception
- Better parallel execution
- Multi-browser support (Chromium, Firefox, WebKit)

**Cons**:
- Only 25% success rate against anti-bot systems in default configuration
- CDP detection is a known fingerprint
- Requires stealth plugins for serious scraping

**Stealth Options**:
- `playwright-stealth` - Port of puppeteer-extra-plugin-stealth
- `undetected-playwright-python` - Achieved 90.5% trust score on CreepJS

**Best for**: Speed-critical scraping, modern JS-heavy sites, testing

**Sources**:
- [Playwright vs. Selenium in 2025 - ZenRows](https://www.zenrows.com/blog/playwright-vs-selenium)
- [Playwright Stealth - Bright Data](https://brightdata.com/blog/how-tos/avoid-bot-detection-with-playwright-stealth)
- [How to Use Playwright Stealth - ZenRows](https://www.zenrows.com/blog/playwright-stealth)

---

### 1.2 Selenium + Undetected ChromeDriver

**Overview**: The established standard for browser automation, with patches to hide automation signals.

**Pros**:
- Largest community and ecosystem
- Supports 10+ programming languages
- Works with real devices
- Enterprise Grid infrastructure
- Extensive documentation

**Cons**:
- 25% success rate against anti-bot systems
- Slower than Playwright (HTTP-based WebDriver protocol)
- More resource-intensive
- `undetected-chromedriver` development has slowed

**Our Current Implementation**: The websearch-fallback skill uses `undetected-chromedriver` which:
- Patches ChromeDriver to remove automation indicators
- Overrides `navigator.webdriver`
- Sets realistic user-agent and window size
- Uses Chrome DevTools Protocol for additional cloaking

**Best for**: Cross-browser testing, enterprise setups, legacy compatibility

**Sources**:
- [Undetected ChromeDriver vs Selenium Stealth - ZenRows](https://www.zenrows.com/blog/undetected-chromedriver-vs-selenium-stealth)
- [Baseline Performance Comparison - Medium](https://medium.com/@dimakynal/baseline-performance-comparison-of-nodriver-zendriver-selenium-and-playwright-against-anti-bot-2e593db4b243)

---

### 1.3 Nodriver / Zendriver (Recommended for Anti-Bot)

**Overview**: Successor to Undetected ChromeDriver. Communicates directly with Chrome via CDP, completely bypassing WebDriver architecture.

**Nodriver**:
- Official successor to undetected-chromedriver
- Async-first design
- No WebDriver/Selenium dependencies
- Smart element lookup (works across iframes)
- 25% success rate in tests

**Zendriver** (Fork of Nodriver):
- More active development and community engagement
- Faster bug fixes
- First-class Docker support
- **75% success rate** against anti-bot systems (Cloudflare, Akamai, CloudFront)
- Automatic cookie/profile management

**Test Results**:
| Tool | Cloudflare | Datadome | CloudFront | Akamai | Success Rate |
|------|------------|----------|------------|--------|--------------|
| Zendriver | ✅ | ❌ | ✅ | ✅ | **75%** |
| Nodriver | ❌ | ❌ | ✅ | ❌ | 25% |
| Selenium | ❌ | ❌ | ❌ | ✅ | 25% |
| Playwright | ❌ | ❌ | ✅ | ❌ | 25% |

**Best for**: Maximum anti-bot bypass, async operations, new projects

**Installation**:
```bash
pip install zendriver
# or
pip install nodriver
```

**Sources**:
- [Zendriver GitHub](https://github.com/cdpdriver/zendriver)
- [Nodriver GitHub](https://github.com/ultrafunkamsterdam/nodriver)
- [How to Use Nodriver - ZenRows](https://www.zenrows.com/blog/nodriver)

---

## 2. HTTP Client Tools (No Browser)

### 2.1 curl-impersonate / curl_cffi

**Overview**: Modified curl that mimics browser TLS fingerprints (JA3/JA4) without running a full browser.

**How it works**:
- Uses BoringSSL (Chrome) or NSS (Firefox) instead of OpenSSL
- Matches browser TLS extensions and SSL options
- Customizes HTTP/2 handshake to match real browsers
- Supports Chrome 99-131, Firefox, Safari fingerprints

**Pros**:
- Much faster than browser automation (no browser overhead)
- Lower resource usage
- Can impersonate specific browser versions
- Python bindings via `curl_cffi`

**Cons**:
- Cannot execute JavaScript
- Struggles against advanced Cloudflare (Turnstile CAPTCHA)
- May lag behind latest browser versions
- Limited to what curl can do

**Best for**: High-volume scraping of static content, API calls, sites with basic bot detection

**Installation**:
```bash
pip install curl_cffi
```

**Usage**:
```python
from curl_cffi import requests

response = requests.get(
    "https://example.com",
    impersonate="chrome120"  # Impersonate Chrome 120
)
```

**Sources**:
- [Web Scraping With curl_cffi - Bright Data](https://brightdata.com/blog/web-data/web-scraping-with-curl-cffi)
- [Curl Impersonate - ZenRows](https://www.zenrows.com/blog/curl-impersonate)
- [Curl Impersonate - Scrapfly](https://scrapfly.io/blog/posts/curl-impersonate-scrape-chrome-firefox-tls-http2-fingerprint)

---

### 2.2 tls-requests

**Overview**: Python library using Go-based HTTP backend for browser-like TLS fingerprinting.

**Features**:
- Browser-like TLS client fingerprinting
- Anti-bot page bypass
- High performance (Go backend)
- Sync and async support

**Best for**: When you need requests-like API with TLS fingerprinting

**Source**: [tls-requests GitHub](https://github.com/thewebscraping/tls-requests)

---

### 2.3 Standard Python HTTP Libraries

**requests / httpx / aiohttp**:
- Produce predictable TLS fingerprints
- Easily detected and blocked
- **Not recommended** for scraping protected sites

**Why they fail**: Python HTTP clients can only configure cipher suites and TLS versions, leaving TLS extension fingerprints exposed.

**Source**: [TLS Fingerprinting in Web Scraping - Rayobyte](https://rayobyte.com/blog/tls-fingerprinting/)

---

## 3. Specialized Anti-Bot Tools

### 3.1 Cloudscraper

**Overview**: Python library specifically for bypassing Cloudflare.

**Pros**:
- Easy to use
- Handles basic Cloudflare challenges

**Cons**:
- Doesn't pass advanced fingerprinting
- Fails against Cloudflare Turnstile CAPTCHA
- May need to pair with CAPTCHA solvers and proxies

**Source**: [Cloudscraper GitHub](https://github.com/VeNoMouS/cloudscraper)

---

### 3.2 FlareSolverr

**Overview**: Proxy server that uses headless browsers to solve Cloudflare challenges.

**How it works**: Acts as a middleware that handles Cloudflare challenges and returns the unprotected content.

**Best for**: Integration with existing scrapers that can't handle Cloudflare

---

### 3.3 Botasaurus

**Overview**: Newer framework designed specifically for bypassing sophisticated anti-bot systems.

**Features**:
- High success rate against Cloudflare
- Purpose-built for anti-bot evasion

**Source**: [Open Source Web Scraping Libraries - ScrapingAnt](https://scrapingant.com/blog/open-source-web-scraping-libraries-bypass-anti-bot)

---

## 4. Commercial Solutions

When open-source tools fail, commercial APIs offer higher success rates:

| Service | Approach |
|---------|----------|
| **ZenRows** | API with built-in Cloudflare bypass |
| **ScrapFly** | Managed browser infrastructure |
| **ScrapingBee** | JavaScript rendering + proxy rotation |
| **Browserless** | Headless browser as a service |

**When to use**: Large-scale scraping, production systems, when you can't afford downtime due to detection.

---

## 5. Recommendations for websearch-fallback Skill

### Current State
Our skill uses **Selenium + undetected-chromedriver**, which achieves ~25% success rate against anti-bot systems.

### Potential Upgrades

#### Option A: Add Zendriver Backend (Recommended)
```
Pros: 75% success rate, async-first, active development
Cons: New dependency, different API
Effort: Medium (new backend, similar architecture)
```

#### Option B: Add curl_cffi for Non-JS Pages
```
Pros: Much faster, lower resources
Cons: No JavaScript execution
Effort: Low (add as alternative fetch method)
```

#### Option C: Add Playwright Backend
```
Pros: Faster than Selenium, better parallel execution
Cons: Still 25% success rate without extensive hardening
Effort: Medium (similar architecture to current)
```

### Recommended Architecture
```
websearch-fallback/
├── backends/
│   ├── selenium_uc.py    # Current (undetected-chromedriver)
│   ├── zendriver.py      # NEW: Best anti-bot bypass
│   ├── curl_cffi.py      # NEW: Fast HTTP-only fallback
│   └── playwright.py     # NEW: Alternative browser automation
├── fetch.py              # Route to best backend
└── search.py             # Route to best backend
```

---

## 6. Anti-Bot Techniques to Be Aware Of (2024-2025)

### Cloudflare Turnstile
- Replaced traditional CAPTCHAs in 2022
- Analyzes browser behavior passively
- Difficult to bypass programmatically

### AI Labyrinth
- Cloudflare's AI-powered honeypot
- Generates fake content dynamically
- Wastes scraper resources

### CDP Detection
- Websites detect Chrome DevTools Protocol usage
- Used by Playwright, Nodriver, and automation tools
- Newer tools try to hide CDP fingerprints

### IPv6 Exploitation
- IPv6 addresses may bypass some Cloudflare rules
- Emerging technique in 2025

---

## Sources

### Comparison Articles
- [Playwright vs Selenium - ZenRows](https://www.zenrows.com/blog/playwright-vs-selenium)
- [Playwright vs Selenium - Bright Data](https://brightdata.com/blog/web-data/playwright-vs-selenium)
- [Baseline Performance Comparison - Medium](https://medium.com/@dimakynal/baseline-performance-comparison-of-nodriver-zendriver-selenium-and-playwright-against-anti-bot-2e593db4b243)

### Anti-Bot Bypass
- [How to Bypass Cloudflare - ZenRows](https://www.zenrows.com/blog/bypass-cloudflare)
- [Bypass Cloudflare at Scale - ScrapingBee](https://www.scrapingbee.com/blog/how-to-bypass-cloudflare-antibot-protection-at-scale/)
- [Anti-Bot Tactics Playwright vs Selenium - Medium](https://medium.com/@minekayaa/scraping-101-anti-bot-tactics-in-playwright-vs-selenium-795c16cc352f)

### Tool Documentation
- [Zendriver GitHub](https://github.com/cdpdriver/zendriver)
- [Nodriver GitHub](https://github.com/ultrafunkamsterdam/nodriver)
- [curl_cffi - Bright Data](https://brightdata.com/blog/web-data/web-scraping-with-curl-cffi)
- [Playwright Stealth - ZenRows](https://www.zenrows.com/blog/playwright-stealth)
