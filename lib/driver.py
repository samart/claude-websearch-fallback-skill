"""Chrome WebDriver management."""

import platform
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Try to use undetected-chromedriver for anti-bot detection
try:
    import undetected_chromedriver as uc
    HAS_UNDETECTED = True
except ImportError:
    HAS_UNDETECTED = False


def get_default_chrome_profile() -> Path:
    """Get the default Chrome user data directory for the current OS."""
    system = platform.system()
    home = Path.home()

    if system == "Darwin":  # macOS
        return home / "Library/Application Support/Google/Chrome"
    elif system == "Windows":
        return home / "AppData/Local/Google/Chrome/User Data"
    elif system == "Linux":
        return home / ".config/google-chrome"

    raise RuntimeError(f"Unsupported platform: {system}")


def create_driver(
    profile_path: Optional[str] = None,
    headless: bool = False,
    timeout: int = 30,
    use_profile: bool = True,
    use_undetected: bool = True,
) -> webdriver.Chrome:
    """
    Create a Chrome WebDriver instance.

    Args:
        profile_path: Path to Chrome user data directory. If None, uses default.
        headless: Run in headless mode (no visible window).
        timeout: Page load timeout in seconds.
        use_profile: Whether to use existing Chrome profile. If headless=True and
                     profile is locked (Chrome running), this is auto-disabled.
        use_undetected: Use undetected-chromedriver to bypass bot detection.

    Returns:
        Configured Chrome WebDriver instance.

    Note:
        If Chrome is already running with your profile, close it first or
        the script will fail to access the locked profile.
    """
    # Try undetected-chromedriver first (bypasses bot detection)
    if use_undetected and HAS_UNDETECTED:
        try:
            return _create_undetected_driver(
                profile_path=profile_path,
                headless=headless,
                timeout=timeout,
                use_profile=use_profile,
            )
        except Exception as e:
            # If undetected fails (e.g., profile locked), try standard driver
            if "session not created" in str(e).lower() or "cannot connect" in str(e).lower():
                # Profile likely locked - try without profile
                return _create_standard_driver(
                    profile_path=profile_path,
                    headless=headless,
                    timeout=timeout,
                    use_profile=False,  # Skip profile to avoid lock
                )
            raise

    # Fall back to standard Selenium
    return _create_standard_driver(
        profile_path=profile_path,
        headless=headless,
        timeout=timeout,
        use_profile=use_profile,
    )


def _create_undetected_driver(
    profile_path: Optional[str],
    headless: bool,
    timeout: int,
    use_profile: bool,
) -> webdriver.Chrome:
    """Create driver using undetected-chromedriver."""
    options = uc.ChromeOptions()

    # Anti-detection: Set realistic window size (headless often has weird sizes)
    options.add_argument("--window-size=1920,1080")

    # Anti-detection: Realistic user-agent
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Anti-detection: Disable automation indicators
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Anti-detection: Set language
    options.add_argument("--lang=en-US,en")

    if headless:
        options.add_argument("--headless=new")

    # Profile handling for undetected-chromedriver
    user_data_dir = None
    if use_profile and not headless:
        if profile_path and profile_path != "auto":
            user_data_dir = profile_path
        else:
            try:
                default_profile = get_default_chrome_profile()
                if default_profile.exists():
                    user_data_dir = str(default_profile)
            except RuntimeError:
                pass

    # Performance settings
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = uc.Chrome(
        options=options,
        user_data_dir=user_data_dir,
        headless=headless,
    )
    driver.set_page_load_timeout(timeout)

    # Anti-detection: Override navigator.webdriver and other properties
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = {runtime: {}};
        """
    })

    return driver


def _create_standard_driver(
    profile_path: Optional[str],
    headless: bool,
    timeout: int,
    use_profile: bool,
) -> webdriver.Chrome:
    """Create driver using standard Selenium."""
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    # In headless mode, don't use existing profile by default (avoids lock issues)
    should_use_profile = use_profile and (not headless or profile_path)

    if should_use_profile:
        if profile_path and profile_path != "auto":
            options.add_argument(f"--user-data-dir={profile_path}")
        elif not headless:
            try:
                default_profile = get_default_chrome_profile()
                if default_profile.exists():
                    options.add_argument(f"--user-data-dir={default_profile}")
            except RuntimeError:
                pass

    # Reduce detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Performance/stability settings
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=0")

    # Try to use webdriver-manager for auto ChromeDriver management
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
    except ImportError:
        service = Service()

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(timeout)

    return driver
