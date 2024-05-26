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

token = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjJGNUQxNzI3NEQ3NjREQzlERENGNDRBOEI3NzE5QUY2NjlCRjc4RTAiLCJ4NXQiOiJMMTBYSjAxMlRjbmR6MFNvdDNHYTltbV9lT0EiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FscGhhLnVpcGF0aC5jb20vaWRlbnRpdHlfIiwibmJmIjoxNzE2NjgwMTg1LCJpYXQiOjE3MTY2ODA0ODUsImV4cCI6MTcxNjY4NDA4NSwiYXVkIjpbIklkZW50aXR5U2VydmVyQXBpIiwiU2VhcmNoUmVjb21tZW5kYXRpb25zU2VydmljZSJdLCJzY29wZSI6WyJvcGVuaWQiLCJwcm9maWxlIiwiZW1haWwiLCJJZGVudGl0eVNlcnZlckFwaSIsIlNSUy5FdmVudHMiLCJTUlMuUmVjb21tZW5kYXRpb25zIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbImV4dGVybmFsIl0sInN1Yl90eXBlIjoidXNlciIsImNsaWVudF9pZCI6IjczYmE2MjI0LWQ1OTEtNGE0Zi1iM2FiLTUwOGU2NDZmMjkzMiIsInN1YiI6ImZkMjI0ZWViLTZlOTUtNDNlNS1hOGIwLTM2MWQzYjViYWYzYSIsImF1dGhfdGltZSI6MTcxNjY2MTEyNCwiaWRwIjoib2lkYyIsImVtYWlsIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIkFzcE5ldC5JZGVudGl0eS5TZWN1cml0eVN0YW1wIjoiQ0dVSVhXRFUzWVNYN0w0NDdQMzVSRzdLRUI2WEFUQ1giLCJhdXRoMF9jb24iOiJnb29nbGUtb2F1dGgyIiwiY291bnRyeSI6IiIsImV4dF9zdWIiOiJnb29nbGUtb2F1dGgyfDEwNTA4NDU0MTE4MTUwNjU0OTk2MyIsIm1hcmtldGluZ0NvbmRpdGlvbkFjY2VwdGVkIjoiRmFsc2UiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jTDJGTU9EcTk1T2lic1hsbFdwamZRSXhJLUQwWndUUV92TVpiNFhYSGhKTmc4enVnPXM5Ni1jIiwicHJ0X2lkIjoiOTU2OGJlYmEtNTBhOC00OWQxLTgwMWUtZjJkMTcxMTA4OWZkIiwiaG9zdCI6IkZhbHNlIiwiZmlyc3RfbmFtZSI6Ikpvc2giLCJsYXN0X25hbWUiOiIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiam9zaHVhLnBhcmtAdWlwYXRoLmNvbSIsIm5hbWUiOiJqb3NodWEucGFya0B1aXBhdGguY29tIiwiZXh0X2lkcF9pZCI6IjEiLCJleHRfaWRwX2Rpc3BfbmFtZSI6Ikdsb2JhbElkcCIsInNpZCI6IjJGOUYwNUZDRUZBMkRDMjk1QkEyNUZCQTgyMDY1NkRDIiwianRpIjoiNjZBODdGRjAwNTRFMzBEQzBEODc4MURBQjg2MjA2NDMifQ.wlXcKe5Mh_t7ICPv3mHb2RAaKHVRjY-_4qTKSUp0eVrN_Oae7hrE5sLsc3BHQ19_uu7FkcdeVBQB9ulNqlrEPCHsWFaPsdlpSyBWM1Lcnu69SeiUAgxOcffaVDbMCcSnoL-FFZSs2jgF18UuqCMlDA9rtCuFhDmc9WV0aBISOtLHRfdS2VAVBOPlPwt5sOJrfmtEJUII47n20q3pns01gSI37pvQV_YZgHQDeH5wZa0fi1HWiuhlHGktiCKGov4Yo3FDgJOS_Qsm5RVVFrgfozOmKH1rzE14Xx1zuFpvrKrCuihvZ_n0OzvUe0dhxPdrAcaSuvqrxKWu8EI9yd5kug"

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
    if isinstance(x, list):
        return all(0 < len(i) < 50 and not str(i)[0].isdigit() for i in x)
    elif isinstance(x, str):
        return 0 < len(x) < 50 and not x[0].isdigit()
    else:
        return False

def isRelevantAttrKey(x):
    return 0 < len(x) < 10

def prune_html(browser):
    html_content = browser.page.content()
    soup = BeautifulSoup(html_content, 'html.parser')
    simplifiedHTML = ""

    def construct_new_tag(orig_tag):
        new_tag = soup.new_tag(orig_tag.name)
        for k, v in orig_tag.attrs.items():
            if isRelevantAttrKey(k) and isRelevantAttrValue(v):
                value = v
                # If value is a list (i.e class="msg-overlay artdeco-button artdeco-button...") only take the first element (i.e class="msg-overlay")
                if isinstance(v, list):
                    value = v[0]
                new_tag.attrs[k] = value
        for child in orig_tag:
            if child.name:
                child_new = construct_new_tag(child)
                new_tag.append(child_new)
            else:
                new_tag.append(str(child))
        return new_tag

    for tag in soup.find_all(["button", "input", "a"]):
        new_tag = construct_new_tag(tag)
        if new_tag.attrs or new_tag.contents:
            simplifiedHTML += str(new_tag.prettify()) + "\n\n"
    
    print(simplifiedHTML)
    with open('output.txt', 'w') as f:
        f.write(simplifiedHTML)
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

    if (action == "Done"):
        global currecurrent_iteration
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

    current_iteration += 1
    if (current_iteration < MAX_ITERATION):
        start_agent(browser, model)

if __name__ == '__main__':
    with sync_playwright() as p:
        browser = SinglePageBrowser(BrowserProcess(), p)
        # browser.page.goto("https://alpha.uipath.com/joshparktest/studio_/designer/ca65ba20-1b78-41c2-ab4c-9188f8b37827?fileId=adaa4c39-e417-4a4f-ab34-18ff60c38393", wait_until="networkidle")
        browser.page.goto("https://www.linkedin.com")
        
        simplifiedHTML = prune_html(browser)

        # user prompt
        user_request = input("What would you like to automate?")
        chat_history.append({
            "role": "user",
            "content": user_request
        })

        model = get_llm()
        
        start_agent(browser, model)
