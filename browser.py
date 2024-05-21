import dataclasses
import subprocess
import time
from pathlib import Path
import random

from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Playwright as SyncPlaywright, Page, BrowserContext, Browser
from playwright.sync_api import expect

from icecream import ic


###############
# Setup Steps #
###############
# 1. pip install -r requirements.txt
# 2. playwright install
# 3. Launch chrome to setup the profile


class BrowserProcess:
    def __init__(self, port: int | None = None, profile_dir: str | None = None):
        self._port = port or random.randint(9100, 9300)
        self._process = None
        self._profile_dir = profile_dir or (Path(__file__).parent / Path(f'chrome_profile')).absolute()

    def _launch(self):
        self._process = subprocess.Popen([
            "C:\Program Files\Google\Chrome\Application\chrome.exe",
            f"--remote-debugging-port={self._port}",
            rf"--user-data-dir={self._profile_dir}"
        ])
        time.sleep(5)

    def ensure_launched(self):
        if self._process is None:
            self._launch()

    @property
    def port(self):
        return self._port

    def __del__(self):
        if self._process is not None:
            self._process.kill()
            self._process.wait()


class SinglePageBrowser:
    def __init__(self, browser_process: BrowserProcess, playwright: SyncPlaywright):
        self._browser_process = browser_process
        self._playwright = playwright
        self._page_context = None

    def _setup(self):
        self._browser_process.ensure_launched()
        browser = self._playwright.chromium.connect_over_cdp(f"http://localhost:{self._browser_process.port}")
        self._page_context = PageContext(
            browser=browser,
            context=browser.contexts[0],
            page=browser.contexts[0].new_page()
        )

    @property
    def page(self) -> Page:
        if self._page_context is None:
            self._setup()
        return self._page_context.page

    def __del__(self):
        self._page_context = None
        self._browser_process = None


@dataclasses.dataclass
class PageContext:
    browser: Browser
    context: BrowserContext
    page: Page

    def __del__(self):
        self.page.close()
        self.context.close()
        self.browser.close()


if __name__ == '__main__':
    # Example usage
    with sync_playwright() as p:
        browser = SinglePageBrowser(BrowserProcess(), p)

        browser.page.goto("https://www.google.com")

        time.sleep(3)
        del browser

    # List of actions on a page: https://playwright.dev/docs/input