import dataclasses
import openai
import random
import re
import subprocess
import time
import base64
import time
from pathlib import Path

from bs4 import BeautifulSoup
from icecream import ic
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Playwright as SyncPlaywright, Page, BrowserContext, Browser
from playwright.sync_api import expect
from langchain_openai import AzureChatOpenAI

token = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjJGNUQxNzI3NEQ3NjREQzlERENGNDRBOEI3NzE5QUY2NjlCRjc4RTAiLCJ4NXQiOiJMMTBYSjAxMlRjbmR6MFNvdDNHYTltbV9lT0EiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FscGhhLnVpcGF0aC5jb20vaWRlbnRpdHlfIiwibmJmIjoxNzE2NzU5MTc3LCJpYXQiOjE3MTY3NTk0NzcsImV4cCI6MTcxNjc2MzA3NywiYXVkIjpbIk9yY2hlc3RyYXRvckFwaVVzZXJBY2Nlc3MiLCJNYW5hZ2VMaWNlbnNlIiwiT01TIiwiQWlGYWJyaWMiLCJCdXNpbmVzc1VzZXJQb3J0YWxQcm94eUFwaSIsIkRhdGFTZXJ2aWNlQXBpVXNlckFjY2VzcyIsIkNvbm5lY3Rpb25TZXJ2aWNlIiwiQ29ubmVjdGlvblNlcnZpY2VVc2VyIiwiSmFtSmFtQXBpIiwiSW5zaWdodHMiLCJJbnNpZ2h0cy5JbnRlZ3JhdGlvbnMiLCJQcm9jZXNzTWluaW5nIiwiVGFza01pbmluZyIsIlNlcnZlcmxlc3NDb250cm9sUGxhbmUiLCJJZGVudGl0eVNlcnZlckFwaSIsIkRvY3VtZW50VW5kZXJzdGFuZGluZyIsIkRvY3VtZW50VW5kZXJzdGFuZGluZ1MyUyIsIlVpUGF0aC5PcmNoZXN0cmF0b3IiLCJTdHVkaW9XZWJCYWNrZW5kIiwiU3R1ZGlvV2ViVHlwZUNhY2hlU2VydmljZSIsIkN1c3RvbWVyUG9ydGFsIiwiQXVkaXQiLCJVaVBhdGguRG9jdW1lbnRVbmRlcnN0YW5kaW5nIiwiQXV0b21hdGlvblNvbHV0aW9ucyIsIlJlaW5mZXIiLCJSZXNvdXJjZUNhdGFsb2dTZXJ2aWNlQXBpIiwiU2VhcmNoUmVjb21tZW5kYXRpb25zU2VydmljZSIsIkluc2lnaHRzLlJlYWxUaW1lRGF0YSIsIkdsb2JhbENsaWVudE1hbmFnZW1lbnQuSW50ZXJuYWwiLCJBY2FkZW15Il0sInNjb3BlIjpbIkFjYWRlbXkiLCJBaUZhYnJpYyIsIkF1ZGl0LlJlYWQiLCJBdXRvbWF0aW9uU29sdXRpb25zIiwiQnVzaW5lc3NVc2VyUG9ydGFsUHJveHlBcGkiLCJDb25uZWN0aW9uU2VydmljZSIsIkNvbm5lY3Rpb25TZXJ2aWNlVXNlciIsIkN1c3RvbWVyUG9ydGFsIiwiRGF0YVNlcnZpY2VBcGlVc2VyQWNjZXNzIiwiRGlyZWN0b3J5IiwiRG9jdW1lbnRVbmRlcnN0YW5kaW5nIiwiRHUuQWlQcm94eSIsIkR1LkNsYXNzaWZpY2F0aW9uLkFwaSIsIkR1LkRpZ2l0aXphdGlvbi5BcGkiLCJEdS5FeHRyYWN0aW9uLkFwaSIsIkR1Lk1ldGVyaW5nIiwiRHUuU3RvcmFnZS5QcmVzaWduZWRVcmwiLCJEdS5UcmFpbmluZy5TZXJ2aWNlIiwiRHUuVmFsaWRhdGlvbi5BcGkiLCJlbWFpbCIsIkdsb2JhbENsaWVudE1hbmFnZW1lbnQuSW50ZXJuYWwiLCJJZGVudGl0eVNlcnZlckFwaSIsIkluc2lnaHRzIiwiSW5zaWdodHMuSW50ZWdyYXRpb25zIiwiSW5zaWdodHMuUmVhbFRpbWVEYXRhIiwiSmFtSmFtQXBpIiwiTWFuYWdlTGljZW5zZSIsIk9NUyIsIm9wZW5pZCIsIk9SLkFkbWluaXN0cmF0aW9uLlJlYWQiLCJPcmNoZXN0cmF0b3JBcGlVc2VyQWNjZXNzIiwiUHJvY2Vzc01pbmluZyIsInByb2ZpbGUiLCJSQ1MuRm9sZGVyQXV0aG9yaXphdGlvbiIsIlJDUy5UYWdzTWFuYWdlbWVudCIsIlJlZmVyZW5jZVRva2VuIiwiUmVpbmZlciIsIlNDUC5Kb2JzLlJlYWQiLCJTQ1AuUnVudGltZXMiLCJTQ1AuUnVudGltZXMuUmVhZCIsIlNSUy5FdmVudHMiLCJTUlMuUmVjb21tZW5kYXRpb25zIiwiU3R1ZGlvV2ViQmFja2VuZCIsIlN0dWRpb1dlYlR5cGVDYWNoZVNlcnZpY2UiLCJUYXNrTWluaW5nIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbImV4dGVybmFsIl0sInN1Yl90eXBlIjoidXNlciIsImNsaWVudF9pZCI6IjExMTlhOTI3LTEwYWItNDU0My1iZDFhLWFkNmJmYmJjMjdmNCIsInN1YiI6ImZkMjI0ZWViLTZlOTUtNDNlNS1hOGIwLTM2MWQzYjViYWYzYSIsImF1dGhfdGltZSI6MTcxNjc0ODgwOCwiaWRwIjoib2lkYyIsImVtYWlsIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIkFzcE5ldC5JZGVudGl0eS5TZWN1cml0eVN0YW1wIjoiQ0dVSVhXRFUzWVNYN0w0NDdQMzVSRzdLRUI2WEFUQ1giLCJhdXRoMF9jb24iOiJnb29nbGUtb2F1dGgyIiwiY291bnRyeSI6IiIsImV4dF9zdWIiOiJnb29nbGUtb2F1dGgyfDEwNTA4NDU0MTE4MTUwNjU0OTk2MyIsIm1hcmtldGluZ0NvbmRpdGlvbkFjY2VwdGVkIjoiRmFsc2UiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jTDJGTU9EcTk1T2lic1hsbFdwamZRSXhJLUQwWndUUV92TVpiNFhYSGhKTmc4enVnPXM5Ni1jIiwicHJ0X2lkIjoiOTU2OGJlYmEtNTBhOC00OWQxLTgwMWUtZjJkMTcxMTA4OWZkIiwiaG9zdCI6IkZhbHNlIiwiZmlyc3RfbmFtZSI6Ikpvc2giLCJsYXN0X25hbWUiOiIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIm5hbWUiOiJqb3NodWEucGFya0B1aXBhdGguY29tIiwiZXh0X2lkcF9pZCI6IjEiLCJleHRfaWRwX2Rpc3BfbmFtZSI6Ikdsb2JhbElkcCIsInNpZCI6IjhFRTRFQUUyNDU1MDUxMDlCMkUzRUYyQTM4RDE4ODcxIiwianRpIjoiNjQxODAzOUM3NDIyNUM4MkJCMjhGQTNDQzk2RDlGQjAifQ.LtIjJ355wbwUeLH1YRnpr_2_Go8LnlKKQMCZFwVO9NzSrDsOMs_e9rvwSwKUuWpazxHVCfYzKIJGv_I0xDePwXR4OZ935wzXerzB-AUEmuzWNe09ilTt5GagqHLmcXmOeezNnU2QKf3V6scHg9uaViDOgDKuJZJo4RZPewzWjK3HcWcEmTiP4MfcK9DolGTcu9il0r8T_e9foNhetWOrkODG0DxetC7AA1rZ2eAPL0sUQ0zrw6a-jgPZMh_x3t3Ivo2WtzEyO10-yB6h9EDal95yTiD_3aPynOyhr8dK-bjADSJtjI6LycgCRrz6XqxlYV6oDKiZLhZx3zxsg_qfEA"

def get_llm():
    return AzureChatOpenAI(
        # deployment_name="gpt-4-32k",
        # deployment_name="gpt-4-vision-preview",
        deployment_name="gpt-4",
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

chat_history = [
    {
        "role": "system",
        "content": """
You are a navigator that can browse the internet. You will be given a simplified HTML view of a website you are currently located in. Given the user's request, your goal is to select an action to complete that request.
Select 1 action from the <action> list that you think will accomplish the user's ask.

Here are the only actions you can use:
<actions>
    <action key="ClickButton" description="clicks a button with a specific id" parameters=[targetTag] />
    <action key="FillInputField" description="fills in an input field with a specific id" parameters=[targetTag, value] />
    <action key="GoToUrl" description="Navigates to URL" parameters=[url] />
    <action key="GoBack" description="Navigates to previously visited URL" />
    <action key="Done" description="Indicates user their request is completed" />
</actions>

Here are examples of valid complete responses with example data from different chat conversations: 
[ClickButton][targetTag: button[id='myButtonId']]
[ClickButton][targetTag: button[aria-label='Add an activity']]
[ClickButton][targetTag: button[class='button-class-123']]
[FillInputField][targetTag: input[aria-label='Search for an activity']][value: "asana"]
[FillInputField][targetTag: input[id='activity-searchbar-123']][value: "activity name"]
[FillInputField][targetTag: input[placeholder='Search term...']][value: "microsoft"]
[GoToUrl][url: "https://www.google.com"]
[GoToUrl][url: "https://www.linkedin.com"]
[GoBack]
[Done]

You must format the output exactly in the format specified above. DO NOT UNDER ANY CIRCUMSTANCES, MAKE UP A HTML TAG
        """
    },
]

def isRelevantAttrValue(x):
    return 0 < len(x) < 50 and not x[0].isdigit()

def isRelevantAttrKey(x):
    return 0 < len(x) < 20

def prune_html(browser):
    # general purpose
    # html_content = browser.page.content()

    # for uipath studio (demo only)
    html_content = browser.page.query_selector('mat-drawer-content.mat-drawer-content')
    html_content = html_content.inner_html()

    if (browser.page.query_selector('.mdc-dialog__container')): # if popup exists, show popup only
        html_content = browser.page.query_selector('.mdc-dialog__container').inner_html()
    if (browser.page.query_selector('.mat-mdc-dialog-surface')): # if dropdown exists, show dropdown only
        html_content = browser.page.query_selector('.mat-mdc-dialog-surface').inner_html()

    soup = BeautifulSoup(html_content, 'html.parser')
    simplifiedHTML = ""

    def construct_new_tag(orig_tag):
        new_tag = soup.new_tag(orig_tag.name)
        for k, v in orig_tag.attrs.items():
            if isRelevantAttrKey(k) and isRelevantAttrValue(v):
                # If value is a list (i.e class="msg-overlay artdeco-button artdeco-button...") only take the first element (i.e class="msg-overlay")
                value = v
                if isinstance(v, list):
                    value = v[0]
                new_tag.attrs[k] = value
        for child in orig_tag:
            if child.name:
                # html tag children
                child_new = construct_new_tag(child)
                new_tag.append(child_new)
            else:
                # non-html tags, just text
                new_tag.append(str(child))
        return new_tag

    for tag in soup.find_all(["button", "input", "a"]):
        new_tag = construct_new_tag(tag)
        if new_tag.attrs or new_tag.contents:
            simplifiedHTML += str(new_tag.prettify()) + "\n"
    
    return simplifiedHTML


def parse_and_execute_action(browser, response):
    print("response: ", response)

    # parses [<action>][<targetTag>: <target>][<value key>: "<value>"]
    action_search = re.search(r'\[(\w+)\]', response)
    action = action_search.group(1) if action_search else ""

    target_search = re.search(r'targetTag\: (.*?\])', response)
    target = target_search.group(1) if target_search else ""

    value_search = re.search(r'value\: "(.*?)"', response)
    value = value_search.group(1) if value_search else ""

    url_search = re.search(r'url\: "(.*?)"', response)
    url = url_search.group(1) if url_search else ""

    print("parsed action: ", action, target, value, url)
    if (action == "ClickButton"):
        browser.page.click(target)

    if (action == "FillInputField"):
        browser.page.fill(target, value)
    
    if (action == "GoToUrl"):
        browser.page.goto(url)
        time.sleep(1)

    if (action == "GoBack"):
        browser.page.goBack()

    if (action == "PressEnterKey"):
        browser.page.keyboard.press('Enter')

    if (action == "PressEscKey"):
        browser.page.keyboard.press("Escape")

    if (action == "Done"):
        global current_iteration
        current_iteration = MAX_ITERATION

MAX_ITERATION = 10
current_iteration = 0
def start_agent(browser, model):
    global current_iteration

    # prune HTML content
    simplifiedHTML = prune_html(browser)

    # show agent HTML
    response = model.invoke([
        *chat_history,
        {
            "role": "system",
            "content": """You are in URL {url}. Select the next appropriate action to accomplish the user's goal. 

            Here is a simplified view of the website HTML you are currently in:
            {html}""".format(url=browser.page.url, html=simplifiedHTML)
        } 
    ])

    # GPT4 vision
    # screenshot_bytes = browser.page.screenshot()
    # base64_image = base64.b64encode(screenshot_bytes).decode()
    # chat_history.append(
    #     {
    #         "role": "system",
    #         "content": [
    #             {
    #                 "type": "text",
    #                 "text": "Status update: an action has been triggered. You are in URL " + browser.page.url + ". This is the state of the current UI. Select the next appropriate action to accomplish the user's goal. Do NOT make up your own HTML tags. TargetTags must be one of the simplified HTML tags provided"                    
    #             },
    #             {
    #                 "type": "image_url",
    #                 "image_url": {
    #                     "url": f"data:image/jpeg;base64,{base64_image}"
    #                 }                
    #             }
    #         ]
    #     }
    # )

    # debugging purposes
    with open(str(current_iteration) + 'output.txt', 'w') as f:
        f.write(simplifiedHTML)

    # execute action
    parse_and_execute_action(browser, response.content)

    # optional; let the page load
    time.sleep(0.5)

    # update agent on progress
    chat_history.append({
        "role": "system",
        "content": "Status update: you have triggerd an action {response}. Do not repeat the same action twice in a row.".format(response=response.content)
    })

    print("current_iteration: ", current_iteration)
    current_iteration += 1
    if (current_iteration < MAX_ITERATION):
        start_agent(browser, model)

if __name__ == '__main__':
    with sync_playwright() as p:
        browser = SinglePageBrowser(BrowserProcess(), p)
        browser.page.goto("https://alpha.uipath.com/joshparktest/studio_/designer/be99476e-f6a6-465e-a60c-0bcc479c5fbf?fileId=ca159ebc-7722-42c1-af85-183c5143f326", wait_until="networkidle")

        # user prompt
        user_request = input("What would you like to automate?")
        chat_history.append({
            "role": "user",
            "content": user_request
        })

        model = get_llm()
        
        start_agent(browser, model)
        start_agent(browser, model)
