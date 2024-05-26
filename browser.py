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

token = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjJGNUQxNzI3NEQ3NjREQzlERENGNDRBOEI3NzE5QUY2NjlCRjc4RTAiLCJ4NXQiOiJMMTBYSjAxMlRjbmR6MFNvdDNHYTltbV9lT0EiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FscGhhLnVpcGF0aC5jb20vaWRlbnRpdHlfIiwibmJmIjoxNzE2Njk0NDM3LCJpYXQiOjE3MTY2OTQ3MzcsImV4cCI6MTcxNjY5ODMzNywiYXVkIjpbIk9yY2hlc3RyYXRvckFwaVVzZXJBY2Nlc3MiLCJNYW5hZ2VMaWNlbnNlIiwiT01TIiwiQWlGYWJyaWMiLCJCdXNpbmVzc1VzZXJQb3J0YWxQcm94eUFwaSIsIkRhdGFTZXJ2aWNlQXBpVXNlckFjY2VzcyIsIkNvbm5lY3Rpb25TZXJ2aWNlIiwiQ29ubmVjdGlvblNlcnZpY2VVc2VyIiwiSmFtSmFtQXBpIiwiSW5zaWdodHMiLCJJbnNpZ2h0cy5JbnRlZ3JhdGlvbnMiLCJQcm9jZXNzTWluaW5nIiwiVGFza01pbmluZyIsIlNlcnZlcmxlc3NDb250cm9sUGxhbmUiLCJJZGVudGl0eVNlcnZlckFwaSIsIkRvY3VtZW50VW5kZXJzdGFuZGluZyIsIkRvY3VtZW50VW5kZXJzdGFuZGluZ1MyUyIsIlVpUGF0aC5PcmNoZXN0cmF0b3IiLCJTdHVkaW9XZWJCYWNrZW5kIiwiU3R1ZGlvV2ViVHlwZUNhY2hlU2VydmljZSIsIkN1c3RvbWVyUG9ydGFsIiwiQXVkaXQiLCJVaVBhdGguRG9jdW1lbnRVbmRlcnN0YW5kaW5nIiwiQXV0b21hdGlvblNvbHV0aW9ucyIsIlJlaW5mZXIiLCJSZXNvdXJjZUNhdGFsb2dTZXJ2aWNlQXBpIiwiU2VhcmNoUmVjb21tZW5kYXRpb25zU2VydmljZSIsIkluc2lnaHRzLlJlYWxUaW1lRGF0YSIsIkdsb2JhbENsaWVudE1hbmFnZW1lbnQuSW50ZXJuYWwiLCJBY2FkZW15Il0sInNjb3BlIjpbIkFjYWRlbXkiLCJBaUZhYnJpYyIsIkF1ZGl0LlJlYWQiLCJBdXRvbWF0aW9uU29sdXRpb25zIiwiQnVzaW5lc3NVc2VyUG9ydGFsUHJveHlBcGkiLCJDb25uZWN0aW9uU2VydmljZSIsIkNvbm5lY3Rpb25TZXJ2aWNlVXNlciIsIkN1c3RvbWVyUG9ydGFsIiwiRGF0YVNlcnZpY2VBcGlVc2VyQWNjZXNzIiwiRGlyZWN0b3J5IiwiRG9jdW1lbnRVbmRlcnN0YW5kaW5nIiwiRHUuQWlQcm94eSIsIkR1LkNsYXNzaWZpY2F0aW9uLkFwaSIsIkR1LkRpZ2l0aXphdGlvbi5BcGkiLCJEdS5FeHRyYWN0aW9uLkFwaSIsIkR1Lk1ldGVyaW5nIiwiRHUuU3RvcmFnZS5QcmVzaWduZWRVcmwiLCJEdS5UcmFpbmluZy5TZXJ2aWNlIiwiRHUuVmFsaWRhdGlvbi5BcGkiLCJlbWFpbCIsIkdsb2JhbENsaWVudE1hbmFnZW1lbnQuSW50ZXJuYWwiLCJJZGVudGl0eVNlcnZlckFwaSIsIkluc2lnaHRzIiwiSW5zaWdodHMuSW50ZWdyYXRpb25zIiwiSW5zaWdodHMuUmVhbFRpbWVEYXRhIiwiSmFtSmFtQXBpIiwiTWFuYWdlTGljZW5zZSIsIk9NUyIsIm9wZW5pZCIsIk9SLkFkbWluaXN0cmF0aW9uLlJlYWQiLCJPcmNoZXN0cmF0b3JBcGlVc2VyQWNjZXNzIiwiUHJvY2Vzc01pbmluZyIsInByb2ZpbGUiLCJSQ1MuRm9sZGVyQXV0aG9yaXphdGlvbiIsIlJDUy5UYWdzTWFuYWdlbWVudCIsIlJlZmVyZW5jZVRva2VuIiwiUmVpbmZlciIsIlNDUC5Kb2JzLlJlYWQiLCJTQ1AuUnVudGltZXMiLCJTQ1AuUnVudGltZXMuUmVhZCIsIlNSUy5FdmVudHMiLCJTUlMuUmVjb21tZW5kYXRpb25zIiwiU3R1ZGlvV2ViQmFja2VuZCIsIlN0dWRpb1dlYlR5cGVDYWNoZVNlcnZpY2UiLCJUYXNrTWluaW5nIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbImV4dGVybmFsIl0sInN1Yl90eXBlIjoidXNlciIsImNsaWVudF9pZCI6IjExMTlhOTI3LTEwYWItNDU0My1iZDFhLWFkNmJmYmJjMjdmNCIsInN1YiI6ImZkMjI0ZWViLTZlOTUtNDNlNS1hOGIwLTM2MWQzYjViYWYzYSIsImF1dGhfdGltZSI6MTcxNjY2MTEyNCwiaWRwIjoib2lkYyIsImVtYWlsIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIkFzcE5ldC5JZGVudGl0eS5TZWN1cml0eVN0YW1wIjoiQ0dVSVhXRFUzWVNYN0w0NDdQMzVSRzdLRUI2WEFUQ1giLCJhdXRoMF9jb24iOiJnb29nbGUtb2F1dGgyIiwiY291bnRyeSI6IiIsImV4dF9zdWIiOiJnb29nbGUtb2F1dGgyfDEwNTA4NDU0MTE4MTUwNjU0OTk2MyIsIm1hcmtldGluZ0NvbmRpdGlvbkFjY2VwdGVkIjoiRmFsc2UiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jTDJGTU9EcTk1T2lic1hsbFdwamZRSXhJLUQwWndUUV92TVpiNFhYSGhKTmc4enVnPXM5Ni1jIiwicHJ0X2lkIjoiOTU2OGJlYmEtNTBhOC00OWQxLTgwMWUtZjJkMTcxMTA4OWZkIiwiaG9zdCI6IkZhbHNlIiwiZmlyc3RfbmFtZSI6Ikpvc2giLCJsYXN0X25hbWUiOiIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIm5hbWUiOiJqb3NodWEucGFya0B1aXBhdGguY29tIiwiZXh0X2lkcF9pZCI6IjEiLCJleHRfaWRwX2Rpc3BfbmFtZSI6Ikdsb2JhbElkcCIsInNpZCI6IjJGOUYwNUZDRUZBMkRDMjk1QkEyNUZCQTgyMDY1NkRDIiwianRpIjoiNDhDNkZGOTdEMjgzQTdGREJGQzQ3RTI0MUM0MTQ5OEYifQ.Qfy0MoDTCOXvVoDFA2cRa1she-2MSWrWbk-FXNtNppxvveg0_AUdyuMRCL8O9DexsjzQ8p6nIYJ9GG-YVjIKo7ynyz2IT0bGC7ekNq5NeRp4wCFCw8zOd2_C6OM_RW987DxWcEN1pAt2ExhmkMenxL-66-NjEqMxLDeqQRJv9cC_yFeCmbpMo2hVSwS5sCUWc3ltSFSe4ygJSsrgnzZk5reIty8BsKlaIJGXtlFS8hOkoYk-dsrDjPnTVt9eYr6tp4JVBryaLKhKhwlRubE-oewPoRtyjRUOrTD7aKQK9e_2InAQTqbBu-l1rQUGjZuGfc5QLh6A5O2MjIKDrg38gQ"

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

chat_history = [
    {
        "role": "system",
        "content": """
You are a navigator that can browse the internet. You will be given a simplified HTML view of a website you are currently located in. Given the user's request, your goal is to select an action to complete that request.
Select 1 action from the <action> list that you think will accomplish the user's ask.

Here are the actions you can use:
<actions>
    <action key="ClickButton" description="clicks a button with a specific id" parameters=[targetTag] />
    <action key="FillInputField" description="fills in an input field with a specific id" parameters=[targetTag, value] />
    <action key="GoToUrl" description="Navigates to URL" parameters=[url] />
    <action key="GoBack" description="Navigates to previously visited URL" />
    <action key="Done" description="Indicates user their request is completed" />
</actions>

Answer the following questions in the format "A:answer,B:answer,C:answer" etc 
A) What HTML tag NOT listed in website HTML you are currently in would you make up to accomplish the user's request?: (make up HTML tag or N)
B) What HTML tag listed in website HTML you are currently in would you make up to accomplish the user's request?: (list first 10 letters of tag or N)
C) Which of the non made-up, listed HTML tag would you use to trigger your action if any? (or N)

Here are examples of valid complete responses with example data from different chat conversations: 
A:<button id='fakeButton'>B:<button id='myButtonId'>C:<button id='myButtonId'>[ClickButton][targetTag: button[id='myButtonId']]
A:<button aria-label='add activity'>B:<button aria-label='Add an activity'>C:<button aria-label='Add an activity'>[ClickButton][targetTag: button[aria-label='Add an activity']]
A:<a aria-label: 'button-class-123'>B:<button class='button-class-123'>C:<button class='button-class-123'>[ClickButton][targetTag: button[class='button-class-123']]
A:<input aria-label='search activity'>B:<input aria-label='Search for an activity'>C:<input aria-label='Search for an activity'>[FillInputField][targetTag: input[aria-label='Search for an activity']][value: "asana"]
A:<input id='activity-search'>B:<input id='activity-searchbar-123'>C:<input id='activity-searchbar-123'>[FillInputField][targetTag: input[id='activity-searchbar-123']][value: "activity name"]
A:<input aria-label='search term'>B:<input placeholder='Search term...'>C:<input placeholder='Search term...'>[FillInputField][targetTag: input[placeholder='Search term...']][value: "microsoft"]
A:NB:NC:N[GoToUrl][url: "https://www.google.com"]
A:NB:NC:N[GoToUrl][url: "https://www.linkedin.com"]
A:NB:NC:N[GoBack]
A:NB:NC:N[Done]

You must format the output exactly in the format specified above.
        """
    },
]

def isRelevantAttrValue(x):
    return 0 < len(x) < 50 and not x[0].isdigit()

def isRelevantAttrKey(x):
    return 0 < len(x) < 20

def prune_html(browser):
    html_content = browser.page.content()
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
        browser.page.goto(url, wait_until="networkidle")
        time.sleep(1)

    if (action == "GoBack"):
        browser.page.goBack(wait_until="networkidle")

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
    with open(str(current_iteration) + 'HTML.txt', 'w') as f:
        f.write(simplifiedHTML)

    # execute action
    parse_and_execute_action(browser, response.content)

    # GPT4 vision
    # screenshot_bytes = browser.page.screenshot()
    # base64_image = base64.b64encode(screenshot_bytes).decode()
    # chat_history.append(
    #     {
    #         "role": "system",
    #         "content": "Status update: an action has been triggered. You are in URL " + browser.page.url + ". This is the state of the current UI. Select the next appropriate action to accomplish the user's goal. You may only select ONE action and perform ONE action at a time. Do NOT make up your own HTML tags. TargetTags must be one of the simplified HTML tags provided. If you are done, simply say DONE" 
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

    print("current_iteration: ", current_iteration)
    current_iteration += 1
    if (current_iteration < MAX_ITERATION):
        start_agent(browser, model)

if __name__ == '__main__':
    with sync_playwright() as p:
        browser = SinglePageBrowser(BrowserProcess(), p)
        browser.page.goto("https://alpha.uipath.com/joshparktest/studio_/designer/ca65ba20-1b78-41c2-ab4c-9188f8b37827?fileId=adaa4c39-e417-4a4f-ab34-18ff60c38393", wait_until="networkidle")
        # browser.page.goto("https://www.google.com")
        
        # user prompt
        user_request = input("What would you like to automate?")
        chat_history.append({
            "role": "user",
            "content": user_request
        })

        model = get_llm()
        
        start_agent(browser, model)
