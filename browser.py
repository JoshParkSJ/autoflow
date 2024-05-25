import dataclasses
import openai
import random
import re
import subprocess
import time
from pathlib import Path

from bs4 import BeautifulSoup
from icecream import ic
from playwright.sync_api import Browser, BrowserContext, Page, SyncPlaywright, expect
from langchain_openai import AzureChatOpenAI

token = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjJGNUQxNzI3NEQ3NjREQzlERENGNDRBOEI3NzE5QUY2NjlCRjc4RTAiLCJ4NXQiOiJMMTBYSjAxMlRjbmR6MFNvdDNHYTltbV9lT0EiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FscGhhLnVpcGF0aC5jb20vaWRlbnRpdHlfIiwibmJmIjoxNzE2NjYwODE5LCJpYXQiOjE3MTY2NjExMTksImV4cCI6MTcxNjY2NDcxOSwiYXVkIjpbIklkZW50aXR5U2VydmVyQXBpIiwiU2VhcmNoUmVjb21tZW5kYXRpb25zU2VydmljZSJdLCJzY29wZSI6WyJvcGVuaWQiLCJwcm9maWxlIiwiZW1haWwiLCJJZGVudGl0eVNlcnZlckFwaSIsIlNSUy5FdmVudHMiLCJTUlMuUmVjb21tZW5kYXRpb25zIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbImV4dGVybmFsIl0sInN1Yl90eXBlIjoidXNlciIsImNsaWVudF9pZCI6IjczYmE2MjI0LWQ1OTEtNGE0Zi1iM2FiLTUwOGU2NDZmMjkzMiIsInN1YiI6ImZkMjI0ZWViLTZlOTUtNDNlNS1hOGIwLTM2MWQzYjViYWYzYSIsImF1dGhfdGltZSI6MTcxNjU5MjAzNiwiaWRwIjoib2lkYyIsImVtYWlsIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIkFzcE5ldC5JZGVudGl0eS5TZWN1cml0eVN0YW1wIjoiQ0dVSVhXRFUzWVNYN0w0NDdQMzVSRzdLRUI2WEFUQ1giLCJhdXRoMF9jb24iOiJnb29nbGUtb2F1dGgyIiwiY291bnRyeSI6IiIsImV4dF9zdWIiOiJnb29nbGUtb2F1dGgyfDEwNTA4NDU0MTE4MTUwNjU0OTk2MyIsIm1hcmtldGluZ0NvbmRpdGlvbkFjY2VwdGVkIjoiRmFsc2UiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jTDJGTU9EcTk1T2lic1hsbFdwamZRSXhJLUQwWndUUV92TVpiNFhYSGhKTmc4enVnPXM5Ni1jIiwicHJ0X2lkIjoiOTU2OGJlYmEtNTBhOC00OWQxLTgwMWUtZjJkMTcxMTA4OWZkIiwiaG9zdCI6IkZhbHNlIiwiZmlyc3RfbmFtZSI6Ikpvc2giLCJsYXN0X25hbWUiOiIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIm5hbWUiOiJqb3NodWEucGFya0B1aXBhdGguY29tIiwiZXh0X2lkcF9pZCI6IjEiLCJleHRfaWRwX2Rpc3BfbmFtZSI6Ikdsb2JhbElkcCIsInNpZCI6IkY4NDQzMkRGNTA3MDAwQkFCMDJERjk0Q0ZFNzExMDAyIiwianRpIjoiMUIyNjg0MDFCMTRBQTlERjkzMjAzNzkxNTc3MEQyNEUifQ.uaYKNZq-H4Ym1T3cGsCuwRl4kAAWysF1nk--qSbjVxnNe5lycyfEKe_Bx4SX4gQX3d1EImhUnukeNgg4BGbDYPtMUh-ngPMKECCKjZTfXQIiEP3v21MTwr6FC_eVAJ7jivF82kneLDYQYJV0YVUuNaNKFAKfioCNWTu8C_l8XVQ4g9J9QVxTLlpUPnHw4usA2hWntgV_tNunTy8At1LqjpNR3sOVVTIDAxykLuXVWZ7Aekbv6vlYhYrVfoKGOMqV4fKXxIStxxzRpn_-_illbE3B2DM_OmxR3KGNg_5H5VFq9_ZlItb1kTtHpAbLNxGp6sNuwx9y4-35fL-hmf4DUg"

def get_llm():
    return AzureChatOpenAI(
        deployment_name="gpt-4-32k",
        # deployment_name="gpt-4-vision-preview",
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


system_prompt = """
You are a skilled RPA developer. You will be given a simplified HTML view of a website that can build automations. Given the user's request to build a certain type of automation, your goal is to select an action to build that automation.
Select 1 action from the <action> list that you think will accomplish the automation the user is looking to build.

Here are the ONLY actions you can use. Avoid making up new actions:
<actions>
    <action key="ClickButton" description="clicks a button with a specific id" parameters=[id] />
    <action key="FillInputField" description="fills in an input field with a specific id" parameters=[id, value] />
</actions>

Here are examples of valid complete responses with example data from different chat conversations: 
[ClickButton][id: "Add activity"]
[ClickButton][id: "Actions"]
[FillInputField][id: "Search for an activity"][value: "your text"]
[FillInputField][id: "Name an activity"][value: "activity name"]

You must format the output exactly in the format specified above.

"""

def automationUnit(browser):
    # user prompt
    user_request = input("What would you like to automate?")

    # specific for uipath studio web
    # html_content = browser.page.query_selector('mat-drawer-content.mat-drawer-content')
    # html_content = html_content.inner_html()

    # general purpose
    html_content = browser.page.content()
    
    # parse html using bs4
    soup = BeautifulSoup(html_content, 'html.parser')
    
    simplifiedHTML = ""
    for tag in soup.body.find_all():
        if tag.name not in ["style", "script", "head", "title", "meta", "[document]"]:
            if tag.name in ["button", "input"]:
                # new_tag = soup.new_tag(tag.name)
                # new_tag['id'] = tag.get('id')

                # if (tag.get('placeholder')):
                #     new_tag['placeholder'] = tag.get('placeholder')

                simplifiedHTML += str(tag) + "\n"

    print(simplifiedHTML)

    user_prompt = """
    {user_request}

    Here is a simplified HTML view of a website that can build automations:
    {simplifiedHTML}
    """.format(user_request=user_request, simplifiedHTML=simplifiedHTML)

    model = get_llm()
    response = model.invoke(
        [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    print(response.content)

    match = re.match(r'\[(\w+)\]\[id: "([^"]+)"(?:\]\[value: "([^"]+)")?\]', response.content)

    action = match.group(1)
    ariaLabel = match.group(2)
    value = match.group(3) if match.group(3) is not None else ""

    if (action == "ClickButton"):
        target = """button[id={}]""".format("'" + ariaLabel + "'")
        print(target)
        browser.page.click(target)

    if (action == "FillInputField"):
        target = """input[id="{}"]""".format(ariaLabel)
        print(target, value)
        browser.page.fill(target, value)


if __name__ == '__main__':
    # Example usage
    with sync_playwright() as p:
        browser = SinglePageBrowser(BrowserProcess(), p)
        browser.page.goto("https://alpha.uipath.com/joshparktest/studio_/designer/ca65ba20-1b78-41c2-ab4c-9188f8b37827?fileId=adaa4c39-e417-4a4f-ab34-18ff60c38393", wait_until="networkidle")
        # browser.page.goto("https://www.google.com", wait_until="networkidle")
        
        automationUnit(browser)
        automationUnit(browser)
        automationUnit(browser)
        automationUnit(browser)
        automationUnit(browser)
        automationUnit(browser)
        automationUnit(browser)





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


# if youre interested in particular html element, you can see it via screenshot => action