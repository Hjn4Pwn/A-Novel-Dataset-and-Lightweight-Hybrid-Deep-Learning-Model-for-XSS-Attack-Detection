import re
import requests
from collections import defaultdict
import esprima
import csv
import zipfile
import io
from bs4 import BeautifulSoup
import logging
from collections import deque
import pandas as pd
import numpy as np
import urllib.parse
import html5lib
from urllib import parse as urlparse


def parse_html(web_page):
    return BeautifulSoup(web_page, 'html5lib')


def create_html_feature_vector(page_content):
    TG = ["main", "section", "script", "iframe", "meta", "applet", "object", "embed",
          "link", "svg", "frame", "form", "div", "style", "video", "img", "input", "textarea"]
    AT = ["selected", "disabled", "target", "class", "action", "archive", "background", "cite", "classid", "codebase", "data",
          "dsync", "formaction", "href", "icon", "longdesc", "manifest", "poster", "profile", "src", "usemap", "http-equiv", "lowsrc"]
    EV = ["abort", "activate", "afterprint", "afterupdate", "beforeactivate", "beforecopy", "beforecut", "beforedeactivate", "beforeeditfocus", "beforepaste", "beforeprint", "beforeunload", "blur", "change", "click", "contextmenu", "copy", "cut", "datasetcomplete", "dblclick", "deactivate", "drag", "dragend", "dragenter", "dragleave", "dragover", "dragstart", "drop",
          "error", "focus", "focusin", "focusout", "hashchange", "help", "input", "keydown", "keypress", "keyup", "load", "mousedown", "mouseenter", "mouseleave", "mousemove", "mouseout", "mouseover", "mouseup", "mousewheel", "paste", "propertychange", "readystatechange", "reset", "resize", "resizestart", "scroll", "search", "select", "selectstart", "start", "submit", "unload"]

    HFV = defaultdict(int)

    P = parse_html(page_content)

    for node in P.find_all():
        for ti in TG:
            HFV["html_tag_" + ti] += len(node.find_all(ti))

        for ai in AT:
            HFV["html_attr_" + ai] += len(node.attrs.get(ai, []))

        for ei in EV:
            HFV["html_event_on" + ei] += len(node.attrs.get("on" + ei, []))

    HFV['hl'] = len(page_content)
    return HFV


def parse_url_address(page_url):
    AT = ["selected", "disabled", "target", "class", "action", "archive", "background", "cite", "classid", "codebase", "data",
          "dsync", "formaction", "href", "icon", "longdesc", "manifest", "poster", "profile", "src", "usemap", "http-equiv", "lowsrc"]
    TG = ["script", "iframe", "meta", "applet", "object", "embed", "link", "svg", "frame", "form", "div",
          "style", "video", "img", "input", "textarea", "table", "footer", "main", "section", "article", "aside"]
    EV = ["onblur", "onclick", "onerror", "onfocus", "onload", "onmousemove", "onmouseout",
          "onmouseover", "onsearch", "onsubmit", "onunload", "ondblclick", "onscroll", "oninput"]

    url_redirections = ['document.URL',
                        'document.URLUnencoded',
                        'document.baseURI',
                        'document.documentURI',
                        'location',
                        'window.location',
                        'window.history',
                        'window.navigate',
                        'window.open',
                        'self.location',
                        'top.location']
    url_number_keywords_param = ['search', 'login',
                                 'signup', 'query', 'contact', 'URL', 'redirect']
    url_number_keywords_evil = ["<", ">", "javascript", "alert", "script",
                                "onerror", "iframe", "cookie", "sCrIpT", "marquee", "fromCharCode"]

    UFV = {}

    url_str = urllib.parse.unquote(page_url)
    UFV['url_length'] = len(url_str)

    UFV['url_duplicated_characters'] = int(
        any(url_str.count(char) > 1 for char in set(url_str)))

    special_characters = set("!@#$%^&*()_+[]{}|;':\",.<>?/~`")
    UFV['url_special_characters'] = int(
        any(char in special_characters for char in url_str))

    for tag in TG:
        UFV[f'url_tag_{tag}'] = int(tag in url_str)

    for attribute in AT:
        UFV[f'url_attr_{attribute}'] = int(attribute in url_str)

    for event in EV:
        UFV[f'url_event_{event}'] = int(event in url_str)

    UFV['url_redirection'] = 0
    UFV['url_number_keywords_param'] = 0
    UFV['url_number_keywords_evil'] = 0

    UFV['url_redirection'] = int(
        any(param in url_str for param in url_redirections))

    for param in url_number_keywords_param:
        UFV['url_number_keywords_param'] += int(param in url_str)

    for keyword in url_number_keywords_evil:
        UFV['url_number_keywords_evil'] += int(keyword in url_str)

    cookie_pattern = re.compile(
        r'(document\s*\.\s*cookie|document\s*\[\s*"cookie"\s*\])', re.IGNORECASE)

    UFV['url_cookie'] = int(bool(cookie_pattern.search(url_str)))

    domains = re.findall(r'(?P<url>https?://\S+)', url_str)
    UFV['url_number_domain'] = len(domains)

    ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_str)
    UFV['url_number_ip'] = len(ips)

    return UFV


def create_js_feature_vector(page_content):

    DO = ["document", "window", "navigator", "location", "localStorage",
          "sessionStorage", "history", "console", "alert", "confirm", "prompt"]
    JP = ["cookie", "document", "referrer", "innerHTML", "innerText", "textContent",
          "value", "href", "src", "classList", "getAttribute", "setAttribute"]
    JM = ["write", "getElementsByTagName", "getElementById", "alert",
          "eval", "fromCharCode", "prompt", "confirm", "fetch"]

    P = parse_html(page_content)

    JS_strings = []

    for script_tag in P.find_all("script"):
        if not script_tag.attrs.get("src"):
            js = script_tag.string
            if js:
                JS_strings.append(js)

    for a_tag in P.find_all("a", href=True):
        if a_tag.attrs["href"].startswith("javascript:"):
            js = a_tag.attrs["href"][len("javascript:"):]
            if js:
                JS_strings.append(js)

    for form_tag in P.find_all("form", action=True):
        js = form_tag.attrs["action"]
        if js:
            JS_strings.append(js)

    for iframe_tag in P.find_all("iframe", src=True):
        js = iframe_tag.attrs["src"]
        if js:
            JS_strings.append(js)

    for frame_tag in P.find_all("frame", src=True):
        js = frame_tag.attrs["src"]
        if js:
            JS_strings.append(js)

    all_tokens = []
    for js_code in JS_strings:
        tokens = esprima.tokenize(js_code)
        all_tokens.extend(tokens)

    JSFV = {}

    for do in DO:
        JSFV[f'js_dom_{do}'] = 0
    for jp in JP:
        JSFV[f'js_prop_{jp}'] = 0
    for jm in JM:
        JSFV[f'js_method_{jm}'] = 0

    Stringlist = []
    for token in all_tokens:
        if token.type == 'Identifier':
            value = token.value
            if value in DO:
                JSFV[f'js_dom_{value}'] += 1
            elif value in JP:
                JSFV[f'js_prop_{value}'] += 1
            elif value in JM:
                JSFV[f'js_method_{value}'] += 1
        elif token.type == 'String':
            string_value = token.value
            Stringlist.append(string_value)

    if Stringlist:
        JSFV['js_min_length'] = min(len(s) for s in Stringlist)
        JSFV['js_max_length'] = max(len(s) for s in Stringlist)
    else:
        JSFV['js_min_length'] = 0
        JSFV['js_max_length'] = 0

    JSFV['html_length'] = len(page_content)

    # define function
    JSFV['js_define_function'] = 0
    JSFV['js_function_calls'] = 0
    soup = BeautifulSoup(page_content, 'html.parser')
    script_tags = soup.find_all('script')
    function_definition_pattern = r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('

    for script_tag in script_tags:
        script_code = script_tag.get_text()
        function_definitions = re.findall(
            function_definition_pattern, script_code)
        JSFV['js_define_function'] += len(function_definitions)

    # call_function
    function_call_pattern = r'(\w+)\s*\('
    function_call_counts = {}

    for script_tag in script_tags:
        script_code = script_tag.get_text()
        function_calls = re.findall(function_call_pattern, script_code)

        for function_name in function_calls:
            if function_name in function_call_counts:
                function_call_counts[function_name] += 1
            else:
                function_call_counts[function_name] = 1

    for function_name, call_count in function_call_counts.items():
        JSFV['js_function_calls'] += call_count - 1

    # js file
    js_file_pattern = re.compile(r'\.js')

    if js_file_pattern.search(page_content):
        JSFV['js_file'] = 1
    else:
        JSFV['js_file'] = 0

    # js_pseudo_protocol
    strings_to_check = [
        '<img src="javascript:',
        '<form aaction="javascript:',
        '<object adata="javascript:',
        '<button formaction="javascript:',
        '<video src="javascript:',
        '<a href="javascript:',
        '<iframe src="javascript:'
    ]

    regex_pattern = '|'.join(re.escape(string) for string in strings_to_check)

    matches = re.search(regex_pattern, page_content)

    if matches:
        JSFV['js_pseudo_protocol'] = 1
    else:
        JSFV['js_pseudo_protocol'] = 0

    return JSFV


def get_top_urls():
    url = "https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
    urls = []

    with requests.get(url) as r:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        data = z.read('top-1m.csv').decode()

        for line in data.splitlines():
            urls.append(line.split(',')[1])
    return urls[325000:340000]


crawled_data = []
data_html = []
data_js = []
data_url = []


def crawl(url):
    try:
        if not urlparse.urlparse(url).scheme:
            url = "http://" + url

        with requests.get(url, timeout=10) as r:
            html_content = r.text

        page_url = url

        url_feature_vector = parse_url_address(page_url)
        html_feature_vectors = create_html_feature_vector(html_content)
        js_feature_vector = create_js_feature_vector(html_content)

        data_html.append(html_feature_vectors)
        data_url.append(url_feature_vector)
        data_js.append(js_feature_vector)

    except Exception as e:
        pass

# Save page data (if needed)


def save_page(url, html_content, js_content):
    with open('crawl.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([url, html_content, js_content])


def save_crawled_html_data_to_csv(filename, data):
    with open('html_crawl.csv', mode='w', newline='') as csv_file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)


def save_crawled_js_data_to_csv(filename, data):
    with open('js_crawl.csv', mode='w', newline='') as csv_file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)


def save_crawled_url_data_to_csv(filename, data):
    with open('url_crawl.csv', mode='w', newline='') as csv_file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)


# Main crawler
if __name__ == '__main__':
    urls = deque(get_top_urls())
    processed = set()

    while urls:
        url = urls.popleft()
        if url in processed:
            continue
        else:
            processed.add(url)
        print(f"{len(processed)}")
        crawl(url)

    df_html = pd.DataFrame(data_html)
    df_url = pd.DataFrame(data_url)
    df_js = pd.DataFrame(data_js)
    crawled_data = pd.concat([df_html, df_js, df_url], axis=1)

    crawled_data['label'] = np.zeros(crawled_data.shape[0])

    crawled_data.to_csv('./Crawl_normal_325k_340k.csv', index=False)
