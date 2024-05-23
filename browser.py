import dataclasses
import subprocess
import time
from pathlib import Path
import random
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Playwright as SyncPlaywright, Page, BrowserContext, Browser
from playwright.sync_api import expect
from icecream import ic
import openai
from langchain_openai import AzureChatOpenAI
from bs4 import BeautifulSoup

token = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkE2MkMzQ0E5MEYyMzNBMDMzNEMxNEM0MDVDNDJCMEQyRUQ3ODQ3OTYiLCJ4NXQiOiJwaXc4cVE4ak9nTTB3VXhBWEVLdzB1MTRSNVkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FscGhhLnVpcGF0aC5jb20vaWRlbnRpdHlfIiwibmJmIjoxNzE2NDk5MDU5LCJpYXQiOjE3MTY0OTkzNTksImV4cCI6MTcxNjUwMjk1OSwiYXVkIjpbIk9yY2hlc3RyYXRvckFwaVVzZXJBY2Nlc3MiLCJNYW5hZ2VMaWNlbnNlIiwiT01TIiwiQWlGYWJyaWMiLCJCdXNpbmVzc1VzZXJQb3J0YWxQcm94eUFwaSIsIkRhdGFTZXJ2aWNlQXBpVXNlckFjY2VzcyIsIkNvbm5lY3Rpb25TZXJ2aWNlIiwiQ29ubmVjdGlvblNlcnZpY2VVc2VyIiwiSmFtSmFtQXBpIiwiSW5zaWdodHMiLCJJbnNpZ2h0cy5JbnRlZ3JhdGlvbnMiLCJQcm9jZXNzTWluaW5nIiwiVGFza01pbmluZyIsIlNlcnZlcmxlc3NDb250cm9sUGxhbmUiLCJJZGVudGl0eVNlcnZlckFwaSIsIkRvY3VtZW50VW5kZXJzdGFuZGluZyIsIkRvY3VtZW50VW5kZXJzdGFuZGluZ1MyUyIsIlN0dWRpb1dlYkJhY2tlbmQiLCJTdHVkaW9XZWJUeXBlQ2FjaGVTZXJ2aWNlIiwiQ3VzdG9tZXJQb3J0YWwiLCJBdWRpdCIsIlVpUGF0aC5Eb2N1bWVudFVuZGVyc3RhbmRpbmciLCJBdXRvbWF0aW9uU29sdXRpb25zIiwiUmVpbmZlciIsIlJlc291cmNlQ2F0YWxvZ1NlcnZpY2VBcGkiLCJTZWFyY2hSZWNvbW1lbmRhdGlvbnNTZXJ2aWNlIiwiSW5zaWdodHMuUmVhbFRpbWVEYXRhIiwiR2xvYmFsQ2xpZW50TWFuYWdlbWVudC5JbnRlcm5hbCIsIkFjYWRlbXkiXSwic2NvcGUiOlsiQWNhZGVteSIsIkFpRmFicmljIiwiQXVkaXQuUmVhZCIsIkF1dG9tYXRpb25Tb2x1dGlvbnMiLCJCdXNpbmVzc1VzZXJQb3J0YWxQcm94eUFwaSIsIkNvbm5lY3Rpb25TZXJ2aWNlIiwiQ29ubmVjdGlvblNlcnZpY2VVc2VyIiwiQ3VzdG9tZXJQb3J0YWwiLCJEYXRhU2VydmljZUFwaVVzZXJBY2Nlc3MiLCJEaXJlY3RvcnkiLCJEb2N1bWVudFVuZGVyc3RhbmRpbmciLCJEdS5BaVByb3h5IiwiRHUuQ2xhc3NpZmljYXRpb24uQXBpIiwiRHUuRGlnaXRpemF0aW9uLkFwaSIsIkR1LkV4dHJhY3Rpb24uQXBpIiwiRHUuTWV0ZXJpbmciLCJEdS5TdG9yYWdlLlByZXNpZ25lZFVybCIsIkR1LlRyYWluaW5nLlNlcnZpY2UiLCJEdS5WYWxpZGF0aW9uLkFwaSIsImVtYWlsIiwiR2xvYmFsQ2xpZW50TWFuYWdlbWVudC5JbnRlcm5hbCIsIklkZW50aXR5U2VydmVyQXBpIiwiSW5zaWdodHMiLCJJbnNpZ2h0cy5JbnRlZ3JhdGlvbnMiLCJJbnNpZ2h0cy5SZWFsVGltZURhdGEiLCJKYW1KYW1BcGkiLCJNYW5hZ2VMaWNlbnNlIiwiT01TIiwib3BlbmlkIiwiT3JjaGVzdHJhdG9yQXBpVXNlckFjY2VzcyIsIlByb2Nlc3NNaW5pbmciLCJwcm9maWxlIiwiUkNTLkZvbGRlckF1dGhvcml6YXRpb24iLCJSQ1MuVGFnc01hbmFnZW1lbnQiLCJSZWZlcmVuY2VUb2tlbiIsIlJlaW5mZXIiLCJTQ1AuSm9icy5SZWFkIiwiU0NQLlJ1bnRpbWVzIiwiU0NQLlJ1bnRpbWVzLlJlYWQiLCJTUlMuRXZlbnRzIiwiU1JTLlJlY29tbWVuZGF0aW9ucyIsIlN0dWRpb1dlYkJhY2tlbmQiLCJTdHVkaW9XZWJUeXBlQ2FjaGVTZXJ2aWNlIiwiVGFza01pbmluZyIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJzdWJfdHlwZSI6InVzZXIiLCJjbGllbnRfaWQiOiIxMTE5YTkyNy0xMGFiLTQ1NDMtYmQxYS1hZDZiZmJiYzI3ZjQiLCJzdWIiOiJmZDIyNGVlYi02ZTk1LTQzZTUtYThiMC0zNjFkM2I1YmFmM2EiLCJhdXRoX3RpbWUiOjE3MTY0ODMyNjIsImlkcCI6Im9pZGMiLCJlbWFpbCI6Impvc2h1YS5wYXJrQHVpcGF0aC5jb20iLCJBc3BOZXQuSWRlbnRpdHkuU2VjdXJpdHlTdGFtcCI6IkNHVUlYV0RVM1lTWDdMNDQ3UDM1Ukc3S0VCNlhBVENYIiwiYXV0aDBfY29uIjoiZ29vZ2xlLW9hdXRoMiIsImNvdW50cnkiOiIiLCJleHRfc3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDUwODQ1NDExODE1MDY1NDk5NjMiLCJtYXJrZXRpbmdDb25kaXRpb25BY2NlcHRlZCI6IkZhbHNlIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0wyRk1PRHE5NU9pYnNYbGxXcGpmUUl4SS1EMFp3VFFfdk1aYjRYWEhoSk5nOHp1Zz1zOTYtYyIsInBydF9pZCI6Ijk1NjhiZWJhLTUwYTgtNDlkMS04MDFlLWYyZDE3MTEwODlmZCIsImhvc3QiOiJGYWxzZSIsImZpcnN0X25hbWUiOiJKb3NoIiwibGFzdF9uYW1lIjoiIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInByZWZlcnJlZF91c2VybmFtZSI6Impvc2h1YS5wYXJrQHVpcGF0aC5jb20iLCJuYW1lIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsImV4dF9pZHBfaWQiOiIxIiwiZXh0X2lkcF9kaXNwX25hbWUiOiJHbG9iYWxJZHAiLCJzaWQiOiJDODQ4ODk0NDBBQzRCQUU3MEUyN0U4MjhCMTgwQkE5QyIsImp0aSI6IjhBQkUyNDk3OTkyOEZBMTU4MzdBMjBFMDYxNEE3RjQ3In0.r6lfdxKZKPVTudhtyAsR8DLWPqAI_USzSeTIDr2-IHBo0YMd9x9eZ3gPhlOEAxssjRKTt_cuM-86T4dAXGGHOLHdb8rrF1YKvgg4oz4yUXmkxYDKTIsFhB7PPNpZcw7Nf0_NsPKvOfly6Fvfy9CxPhOf83jhu1GhGBSKQfXf7Ty3B1n3DOh3CS91JlC-6MIZDaNKvJcUJscQkp1sVP9MJarC32NtJni1G_tf00AUPIpbVQM3TkMViAAs_MMomnmlKAu851A_blmN9nRuGRvlmzodb5PdzYWmWFZxfxwBhAVEUyjmY6a61IrwBNmoWjq2nW8AXvEPXvL1BTijSNmTHg"

def get_llm():
    return AzureChatOpenAI(
        deployment_name="gpt-4-32k",
        openai_api_version="2023-06-01-preview",
        azure_endpoint="https://alpha.uipath.com/dcfa21f1-a818-4fab-a05d-4fd4292c9ccd/bdd155c1-6ae5-4088-acdd-4cb6bb58e267/llmgateway_/", # Standard Url routing(org/tenant) for LLM Gateway. You do not need to specify a resource name, as the LLM Gateway will route the request to the correct resource.
        openai_api_type="azure",
        openai_api_key="none",
        max_tokens="250",
        default_headers= {
            "X-UIPATH-STREAMING-ENABLED": "false",
            "X-UiPath-LlmGateway-RequestingProduct": "hackathon",
            "X-UiPath-LlmGateway-RequestingFeature": "autoflow",
            "Authorization": token
        }
    )

###############
# Setup Steps #
###############
# 1. pip install -r requirements.txt
# 2. playwright install
# 3. Launch chrome to setup the profile

# List of actions on a page: https://playwright.dev/docs/input

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

    # def __del__(self):
    #     if self._process is not None:
    #         self._process.kill()
    #         self._process.wait()


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

    # def __del__(self):
    #     self._page_context = None
    #     self._browser_process = None


@dataclasses.dataclass
class PageContext:
    browser: Browser
    context: BrowserContext
    page: Page

    # def __del__(self):
    #     self.page.close()
    #     self.context.close()
    #     self.browser.close()


if __name__ == '__main__':
    # Example usage
    with sync_playwright() as p:
        browser = SinglePageBrowser(BrowserProcess(), p)
        browser.page.goto("https://alpha.uipath.com/joshparktest/studio_/designer/ca65ba20-1b78-41c2-ab4c-9188f8b37827?fileId=adaa4c39-e417-4a4f-ab34-18ff60c38393")
        # browser.page.wait_for_load_state("networkidle")
        
        response = input("ready?")

        html_content = browser.page.content()
        soup = BeautifulSoup(html_content, 'html.parser')

        for tag in soup.body.find_all(text=True):
            if tag.parent.name not in ["style", "script", "head", "title", "meta", "[document]"]:
                print(tag)

        # model = get_llm()
        # response = model.invoke(
        #     [
        #         {
        #             "role": "system",
        #             "content": "You are a helpful assistant"
        #         },
        #         {
        #             "role": "user",
        #             "content": "How are you?"
        #         }
        #     ]
        # )
 
        # print(response.content)


'''
one big prompt "Jarvis"
    - feed it HTML (cleaned) + screenshot
    - prompt has many actions, 
    - agent picks 1 action [ACT: my_action] with desired html tags
    - parse the action in-code, execute action (browser.button.click())

[screenshot of full page]
This is my webpage,

here are the ui elements that corresponds to the html tags

<button>add activity</button>
[screenshot of button]

<button>add intergration</button>
[screenshot of button]

<input />
[screenshot of input]

'''