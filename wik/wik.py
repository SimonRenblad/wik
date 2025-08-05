#!/usr/bin/env python3
import argparse
import enum
import os
import random

import requests
from bs4 import BeautifulSoup

try:
    WIDTH, HEIGHT = os.get_terminal_size()
    COLOR_SUPPORT = True
except OSError:
    WIDTH = 120
    HEIGHT = 80
    COLOR_SUPPORT = False


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


COLORS = [Color.GREEN, Color.PURPLE, Color.CYAN, Color.BLUE, Color.DARKCYAN]


def req(term, lang="en"):
    global wikiurl
    wikiurl = "https://" + lang + ".wikipedia.org/wiki/" + term
    r = requests.get(wikiurl, timeout=15)
    return r.text


def get_summary(term, lang="en"):
    final_content = []
    content = req(term, lang)
    soup = BeautifulSoup(content, "html.parser")
    content = soup.find_all("p")
    print("\n" + (Color.BOLD + str(term)).center(WIDTH, "-") + "\n" + Color.END)
    for i in content:
        if i.get_text() == "\n":
            continue
        if i("sup"):
            for tag in i("sup"):
                tag.decompose()

        data = i.get_text()
        final_content.append(data)
        if len(final_content) == 3:
            break

    if "Other reasons this message may be displayed" in str(i):
        print("Did you mean: ")
        term = searchInfo(term, called=True)
    else:
        print(COLORS[random.randrange(len(COLORS) - 1)])
        print(*final_content, sep="\n\n")
        print(Color.END)


def get_info(term, lang="en"):
    final_content = []
    content = req(term, lang)
    soup = BeautifulSoup(content, "html.parser")
    content = []
    for a in soup.find_all(["p", "span"]):
        try:
            if a["class"] and "mw-headline" in a["class"]:
                content.append(a)
        except KeyError:
            if a.name == "p":
                content.append(a)

    for i in content:
        if i("sup"):
            for tag in i("sup"):
                tag.decompose()

        data = i.get_text()
        if i.name == "span":
            final_content.append("!" + str(data))
        else:
            final_content.append(data)

    if "may refer to:" in str(final_content[0]):
        term = searchInfo(term)
    else:
        if COLOR_SUPPORT:
            print("\n" + (Color.BOLD + str(term)).center(WIDTH, "-") + Color.END + "\n")
            print(Color.BLUE + str(wikiurl).center(WIDTH, " ") + Color.END + "\n")
        else:
            print("\n" + str(term).center(WIDTH, "-"))
            print("\n" + str(wikiurl).center(WIDTH, " ") + "\n")
        for i in final_content:
            if i == "\n":
                continue
            if i in [
                "!See also",
                "!Notes",
                "!References",
                "!External links",
                "!Further reading",
            ]:
                continue
            if COLOR_SUPPORT:
                if str(i[0]) == "!":
                    print(
                        Color.BOLD
                        + COLORS[random.randrange(len(COLORS) - 1)]
                        + i[1:]
                        + Color.END
                        + Color.END
                    )
                    print("-" * (len(i) + 1))
                else:
                    if "Other reasons this message may be displayed:" in i:
                        searchInfo(term)
                    else:
                        print(
                            Color.YELLOW
                            + "[-] "
                            + Color.END
                            + COLORS[random.randrange(len(COLORS) - 1)]
                            + i
                            + "\n"
                            + Color.END
                        )
            else:
                print(str(i) + "\n")


def search_info(term, lang="en", called=False):
    r = requests.get(
        "https://" + lang + ".wikipedia.org/w/index.php?fulltext=Search&search=" + term,
        timeout=15,
    )
    if "/wiki/" in r.url:
        get_info(term)
    else:
        content = r.text
        soup = BeautifulSoup(content, "html.parser")
        content = soup.find_all("a", {"data-serp-pos": True})
        dym = soup.find("em")
        if called is False:
            print("Result: \n")
        for i in content:
            if dym is not None:
                print(dym.get_text())
            print(i.get("title"))


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--search", help="Search any topic")
parser.add_argument("-i", "--info", help="Get info on any topic")
parser.add_argument("-q", "--quick", help="Get the summary on any topic")
parser.add_argument(
    "-l", "--lang", help="Get info in your native language (default english)"
)

a = parser.parse_args()
if not a.lang:
    a.lang = "EN"


def arguments():
    if a.quick:
        get_summary(a.quick, a.lang)
    if a.info:
        get_info(a.info, a.lang)
    if a.search:
        search_info(a.search, a.lang)
