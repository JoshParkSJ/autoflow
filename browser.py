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

token = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjJGNUQxNzI3NEQ3NjREQzlERENGNDRBOEI3NzE5QUY2NjlCRjc4RTAiLCJ4NXQiOiJMMTBYSjAxMlRjbmR6MFNvdDNHYTltbV9lT0EiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FscGhhLnVpcGF0aC5jb20vaWRlbnRpdHlfIiwibmJmIjoxNzE2NzY5ODU2LCJpYXQiOjE3MTY3NzAxNTYsImV4cCI6MTcxNjc3Mzc1NiwiYXVkIjpbIk9yY2hlc3RyYXRvckFwaVVzZXJBY2Nlc3MiLCJNYW5hZ2VMaWNlbnNlIiwiT01TIiwiQWlGYWJyaWMiLCJCdXNpbmVzc1VzZXJQb3J0YWxQcm94eUFwaSIsIkRhdGFTZXJ2aWNlQXBpVXNlckFjY2VzcyIsIkNvbm5lY3Rpb25TZXJ2aWNlIiwiQ29ubmVjdGlvblNlcnZpY2VVc2VyIiwiSmFtSmFtQXBpIiwiSW5zaWdodHMiLCJJbnNpZ2h0cy5JbnRlZ3JhdGlvbnMiLCJQcm9jZXNzTWluaW5nIiwiVGFza01pbmluZyIsIlNlcnZlcmxlc3NDb250cm9sUGxhbmUiLCJJZGVudGl0eVNlcnZlckFwaSIsIkRvY3VtZW50VW5kZXJzdGFuZGluZyIsIkRvY3VtZW50VW5kZXJzdGFuZGluZ1MyUyIsIlVpUGF0aC5PcmNoZXN0cmF0b3IiLCJTdHVkaW9XZWJCYWNrZW5kIiwiU3R1ZGlvV2ViVHlwZUNhY2hlU2VydmljZSIsIkN1c3RvbWVyUG9ydGFsIiwiQXVkaXQiLCJVaVBhdGguRG9jdW1lbnRVbmRlcnN0YW5kaW5nIiwiQXV0b21hdGlvblNvbHV0aW9ucyIsIlJlaW5mZXIiLCJSZXNvdXJjZUNhdGFsb2dTZXJ2aWNlQXBpIiwiU2VhcmNoUmVjb21tZW5kYXRpb25zU2VydmljZSIsIkluc2lnaHRzLlJlYWxUaW1lRGF0YSIsIkdsb2JhbENsaWVudE1hbmFnZW1lbnQuSW50ZXJuYWwiLCJBY2FkZW15Il0sInNjb3BlIjpbIkFjYWRlbXkiLCJBaUZhYnJpYyIsIkF1ZGl0LlJlYWQiLCJBdXRvbWF0aW9uU29sdXRpb25zIiwiQnVzaW5lc3NVc2VyUG9ydGFsUHJveHlBcGkiLCJDb25uZWN0aW9uU2VydmljZSIsIkNvbm5lY3Rpb25TZXJ2aWNlVXNlciIsIkN1c3RvbWVyUG9ydGFsIiwiRGF0YVNlcnZpY2VBcGlVc2VyQWNjZXNzIiwiRGlyZWN0b3J5IiwiRG9jdW1lbnRVbmRlcnN0YW5kaW5nIiwiRHUuQWlQcm94eSIsIkR1LkNsYXNzaWZpY2F0aW9uLkFwaSIsIkR1LkRpZ2l0aXphdGlvbi5BcGkiLCJEdS5FeHRyYWN0aW9uLkFwaSIsIkR1Lk1ldGVyaW5nIiwiRHUuU3RvcmFnZS5QcmVzaWduZWRVcmwiLCJEdS5UcmFpbmluZy5TZXJ2aWNlIiwiRHUuVmFsaWRhdGlvbi5BcGkiLCJlbWFpbCIsIkdsb2JhbENsaWVudE1hbmFnZW1lbnQuSW50ZXJuYWwiLCJJZGVudGl0eVNlcnZlckFwaSIsIkluc2lnaHRzIiwiSW5zaWdodHMuSW50ZWdyYXRpb25zIiwiSW5zaWdodHMuUmVhbFRpbWVEYXRhIiwiSmFtSmFtQXBpIiwiTWFuYWdlTGljZW5zZSIsIk9NUyIsIm9wZW5pZCIsIk9SLkFkbWluaXN0cmF0aW9uLlJlYWQiLCJPcmNoZXN0cmF0b3JBcGlVc2VyQWNjZXNzIiwiUHJvY2Vzc01pbmluZyIsInByb2ZpbGUiLCJSQ1MuRm9sZGVyQXV0aG9yaXphdGlvbiIsIlJDUy5UYWdzTWFuYWdlbWVudCIsIlJlZmVyZW5jZVRva2VuIiwiUmVpbmZlciIsIlNDUC5Kb2JzLlJlYWQiLCJTQ1AuUnVudGltZXMiLCJTQ1AuUnVudGltZXMuUmVhZCIsIlNSUy5FdmVudHMiLCJTUlMuUmVjb21tZW5kYXRpb25zIiwiU3R1ZGlvV2ViQmFja2VuZCIsIlN0dWRpb1dlYlR5cGVDYWNoZVNlcnZpY2UiLCJUYXNrTWluaW5nIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbImV4dGVybmFsIl0sInN1Yl90eXBlIjoidXNlciIsImNsaWVudF9pZCI6IjExMTlhOTI3LTEwYWItNDU0My1iZDFhLWFkNmJmYmJjMjdmNCIsInN1YiI6ImZkMjI0ZWViLTZlOTUtNDNlNS1hOGIwLTM2MWQzYjViYWYzYSIsImF1dGhfdGltZSI6MTcxNjc0ODgwOCwiaWRwIjoib2lkYyIsImVtYWlsIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIkFzcE5ldC5JZGVudGl0eS5TZWN1cml0eVN0YW1wIjoiQ0dVSVhXRFUzWVNYN0w0NDdQMzVSRzdLRUI2WEFUQ1giLCJhdXRoMF9jb24iOiJnb29nbGUtb2F1dGgyIiwiY291bnRyeSI6IiIsImV4dF9zdWIiOiJnb29nbGUtb2F1dGgyfDEwNTA4NDU0MTE4MTUwNjU0OTk2MyIsIm1hcmtldGluZ0NvbmRpdGlvbkFjY2VwdGVkIjoiRmFsc2UiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jTDJGTU9EcTk1T2lic1hsbFdwamZRSXhJLUQwWndUUV92TVpiNFhYSGhKTmc4enVnPXM5Ni1jIiwicHJ0X2lkIjoiOTU2OGJlYmEtNTBhOC00OWQxLTgwMWUtZjJkMTcxMTA4OWZkIiwiaG9zdCI6IkZhbHNlIiwiZmlyc3RfbmFtZSI6Ikpvc2giLCJsYXN0X25hbWUiOiIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIm5hbWUiOiJqb3NodWEucGFya0B1aXBhdGguY29tIiwiZXh0X2lkcF9pZCI6IjEiLCJleHRfaWRwX2Rpc3BfbmFtZSI6Ikdsb2JhbElkcCIsInNpZCI6IjhFRTRFQUUyNDU1MDUxMDlCMkUzRUYyQTM4RDE4ODcxIiwianRpIjoiRDgxOTc5NjVCRTU0QjY2NEU1QzNBRDRGM0RFQjExMTIifQ.WL8aS-R4A-ynkeiJMai3946uaZxl7NtTBQI372MNa8c3etv1kAUr7CQZVdiCCMPpiyleYdgWmdfCXKyt3r9XWMrz1LMuXng0A9KcW63riEn5Y9osm0WBhqtMNlddrEzdXqQHtKdj3jj6RV7eyoBBLTjGt6gKTbzYU0DCQJAZZIM_5MuGs9U8VtJuD3zrEpXwCEKzwkfmFIQArSNoFkMAkWtbVwKorluOqGpMdp2PKBmPA_miv9K04ETNI5YHcDgBgnBjPNyRYPWR25nt25-TZbNVgFtYcrTDKp_XCR0ZFa1oNTnr6RSjLY5jujM72JVt2ouurOdHU-AGI21As4FYAA"

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

# ui-tree-item is for demo only
chat_history = [
    {
        "role": "system",
        "content": """
You are a navigator that can browse the internet. You will be given a simplified HTML view of a website you are currently located in. Given the user's request, your goal is to select an action to complete that request.
Select 1 action from the <action> list that you think will accomplish the user's ask.

Here are the only actions you can use:
<actions>
    <action key="Click" description="clicks on a specific <button>, <div>, <ui-tree-item>, or <input> tag" parameters=[targetTag] />
    <action key="FillInputField" description="fills in an input field with a specific id" parameters=[targetTag, value] />
    <action key="GoToUrl" description="Navigates to URL" parameters=[url] />
    <action key="GoBack" description="Navigates to previously visited URL" />
    <action key="PressEscapeKey" description="Presses escape key on keyboard" />
    <action key="Test" description="Tests workflow done so far" />
    <action key="Done" description="Indicates user their request is completed" />
</actions>

Here are examples of valid complete responses with example data from different chat conversations: 
[Click][targetTag: button[id='myButtonId']]
[Click][targetTag: button[aria-label='Add an activity']]
[Click][targetTag: ui-tree-item[id='tree-item']]
[Click][targetTag: input[aria-label='Click to use a variable']]
[Click][targetTag: div[class='div-class-123']]
[FillInputField][targetTag: input[aria-label='Search for an activity']][value: "asana"]
[FillInputField][targetTag: input[id='activity-searchbar-123']][value: "activity name"]
[FillInputField][targetTag: input[placeholder='Search term...']][value: "microsoft"]
[FillInputField][targetTag: div[contenteditable="true"]][value: ""CAD""]
[GoToUrl][url: "https://www.google.com"]
[GoToUrl][url: "https://www.linkedin.com"]
[PressEscapeKey]
[Test]
[GoBack]
[Done]

You must format the output exactly in the format specified above.

DO NOT UNDER ANY CIRCUMSTANCES, MAKE UP A HTML TAG
        """
    },
]

# def isRelevantTag(key, val):
#     return 0 < len(val) < 50 and not val[0].isdigit() and 0 < len(key) < 20

# for uipath studio (demo only)
def isRelevantTag(key, val, name):
    if name == "div" and key != "contenteditable":
        # only read contenteditable divs
        return False
    if not (0 < len(val) < 50 and not val[0].isdigit()):
        return False
    if not (0 < len(key) < 20):
        return False
    if key == "aria-label" and val in ["Actions", "See more"]:
        return False
    if key == "data-cy" and val in ["manual-trigger-add-argument", "dictionary-open", "remove-button"]:
        return False
    if key == "data-cy" and "sw-cp-package-UiPath" in val:
        return False
    return True

def prune_html(browser):
    # general purpose
    # html_content = browser.page.content()

    # for uipath studio (demo only)
    html_content = browser.page.query_selector('mat-drawer-content.mat-drawer-content')
    html_content = html_content.inner_html()
    if (browser.page.query_selector('.mdc-dialog__container')): # if popup exists, show popup only
        html_content = browser.page.query_selector('.mdc-dialog__container').inner_html()
    if (browser.page.query_selector('.mat-mdc-dialog-surface')): # if dropdown exists, append it to view (and truncate the background html since it's less relevant and expensive)
        html_content = browser.page.query_selector('.mat-mdc-dialog-surface').inner_html()

    soup = BeautifulSoup(html_content, 'html.parser')
    simplifiedHTML = ""

    def construct_new_tag(orig_tag):
        new_tag = soup.new_tag(orig_tag.name)

        for k, v in orig_tag.attrs.items():
            if isRelevantTag(k, v, orig_tag.name):
                value = v
                if isinstance(v, list):
                    # If value is a list (i.e class="msg-overlay artdeco-button artdeco-button...") 
                    # only take the first element (i.e class="msg-overlay")
                    value = v[0]
                new_tag.attrs[k] = value
        for child in orig_tag:
            if child.name and child.name != "ui-package-icon": # for uipath studio only ui-package-icon (demo only)
                # html tag children
                child_new = construct_new_tag(child)
                new_tag.append(child_new)
            else:
                # non-html tags, just text
                if len(str(child)) < 50:
                    new_tag.append(str(child))
        return new_tag

    for tag in soup.find_all(["button", "input", "a", "ui-input-widget", "ui-tree-item"]): # for uipath studio only (demo only) - ui-tree-item, ui-input-widget
        new_tag = construct_new_tag(tag)

        if new_tag.attrs or new_tag.contents:
            simplifiedHTML += str(new_tag.prettify()) + "\n"
    
    # for uipath studio only (demo only) - keep hitting into api quota
    if len(simplifiedHTML) > 15000:
        if len(simplifiedHTML) > 25000:
            simplifiedHTML = simplifiedHTML[:len(simplifiedHTML)//6]
        else:
            simplifiedHTML = simplifiedHTML[:len(simplifiedHTML)//3]

    return simplifiedHTML


def parse_and_execute_action(browser, response):
    # parses [<action>][<targetTag>: <target>][<value key>: "<value>"]
    action_search = re.search(r'\[(\w+)\]', response)
    action = action_search.group(1) if action_search else ""

    target_search = re.search(r'targetTag\: (.*?\])', response)
    target = target_search.group(1) if target_search else ""

    value_search = re.search(r'value\: "(\"?.*?\"?)"', response)
    value = value_search.group(1) if value_search else ""

    url_search = re.search(r'url\: "(.*?)"', response)
    url = url_search.group(1) if url_search else ""

    print("response: ", response)
    print("parsed action: ", action, target, value, url)
    if (action == "Click"):
        browser.page.click(target)

        # for demo only - @studio team, why are you not removing this popup after it is closed??!!?!
        if "Set Variable Value" in target:
            browser.page.evaluate('''() => {
                let elem = document.querySelector('div.mdc-dialog__container');
                if (elem) {
                    elem.parentNode.removeChild(elem);
                }
            }''')
            time.sleep(1)
        if "Currency" in target:
            browser.page.evaluate('''() => {
                let elem = document.querySelector('div.mat-mdc-dialog-surface');
                if (elem) {
                    elem.parentNode.removeChild(elem);
                }
            }''')
            time.sleep(1)

        time.sleep(0.5)

    if (action == "FillInputField"):
        browser.page.fill(target, value)
    
    if (action == "GoToUrl"):
        browser.page.goto(url)
        time.sleep(1)

    if (action == "GoBack"):
        browser.page.goBack()

    if (action == "PressEnterKey"):
        browser.page.keyboard.press('Enter')

    if (action == "PressEscapeKey"):
        # browser.page.keyboard.press("Escape")

        # for uipath studio only (demo only)
        browser.page.click("ui-ribbon[class='ng-star-inserted']")
        
    if (action == "Test"): # for uipath studio only (demo only)
        browser.page.click("button[aria-describedby='cdk-describedby-message-ng-1-122']")

    if (action == "Done"):
        global current_iteration
        current_iteration = MAX_ITERATION

MAX_ITERATION = 10
current_iteration = 0
def start_agent(browser, model):
    global current_iteration

    # prune HTML content
    simplifiedHTML = prune_html(browser)

    # debugging purposes
    with open(str(current_iteration) + 'output.txt', 'w') as f:
        f.write(simplifiedHTML)

    # show agent HTML
    response = model.invoke([
        *chat_history,
        {
            "role": "system",
            "content": """You are in URL {url}. Select the next appropriate action to accomplish the user's goal. DO NOT UNDER ANY CIRCUMSTANCES, MAKE UP A HTML TAG

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

    # execute action
    parse_and_execute_action(browser, response.content)

    # update agent on progress
    chat_history.append({
        "role": "system",
        "content": "Status update: you have triggerd an action {response}. Do not repeat the same action twice in a row.".format(response=response.content)
    })

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

        print("\n")

        model = get_llm()
        
        start_agent(browser, model)
