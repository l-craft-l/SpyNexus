"""
This module allows you to search for usernames across a wide list of social media, gaming,
professional, entertainment, and NSFW websites. The tool also supports optional TOR usage
and deep analysis using Google Dorking techniques.

Core Features:
- Username checks on over 150 websites (including NSFW sites optionally)
- Optional TOR proxy support for anonymity
- Automatic saving of results to a text file
- Option to extend analysis with Google Dorking
"""

import requests
import threading
import random
import time
import json
import re
import os
from core.save_data import save_data
from tools.g_dorking import multi_search, gg_connection
from core.agents import agents
from core.display import (
    prRed, prGreen, prCyan, prYellow, maRed, maBlue, maCyan,
    maYellow, maOrange, maMagenta, maGreen, maPink,
    maBold, maUnderline, maBlack, maLightBlue, maLightGreen, maLightYellow,
    maBrown, maTeal, maSkyBlue,
    backRed, display_extra, display_error,
    display_validate, display_info, display_question, happy, sad,
    angry, pointing, nervous, surprised, waiting, write_effect,
    wait_out, space_between, between_tag, check_key
)

cf_us = []
nc_us = []
fr_us = []
lock = threading.Lock()

def ask_connect():
    """
    Asks the user whether they want to use the Tor network for anonymity.

    Returns:
        requests or requests.Session: A requests session, optionally configured with Tor proxy.
    """

    sel = str(input(f"\n{display_question} Do you want to use a Tor network for this module? ({maGreen('y')}/{maRed('n')}): ")).strip()
    if check_key(sel):
        from core.socks_connect import get_tor_connection
        ses = get_tor_connection()
        return ses
    else: return requests


def make_search(connection, nickname, ls):
    """
    Perform HTTP requests on a list of URLs using the specified nickname to determine if user exists.

    Parameters:
        connection (requests or Session): HTTP client to use.
        nickname (str): The username to search for.
        list (list): List of (site_name, url) tuples.
    """

    equals = True
    for title, url in ls:
        try:
            select_agent = agents()
            web = connection.get(url=url, headers=select_agent, timeout=20)
        except requests.exceptions.RequestException: continue

        if web.status_code == 404: continue
        elif web.status_code == 403:
            with lock: fr_us.append((title, url))

        elif web.status_code == 200:
            if equals:
                equals = False

            find = re.search(rf"\b{re.escape(nickname)}\b", web.text, re.IGNORECASE)

            if web.url != url and not find: continue
            if find:
                with lock: cf_us.append((title, url))
            else:
                with lock: nc_us.append((title, url))

def execute_thr(connection, nickname, ls, main):
    max_core = 10

    cf_us.clear()
    write_effect(maYellow("Collecting the users... this could take a few seconds."), 0.03)

    with open(ls, "r", encoding="utf-8") as file: json_data = json.load(file)

    raw_websites = json_data[main]
    data = [(entry["site"], entry["url"].format(nickname)) for entry in raw_websites]

    k, m = divmod(len(data), max_core)
    parts = [data[x * k + min(x, m):(x + 1) * k + min(x + 1, m)] for x in range(max_core)]
    thr = []

    begin = time.time()

    for x in range(max_core):
        t = threading.Thread(target=make_search, args=(connection, nickname, parts[x]))
        thr.append(t)
        t.start()
    for t in thr: t.join()

    end = round(time.time() - begin, 2)

    write_effect(f"\n{display_validate} {maGreen(surprised)} {maGreen('Confirmed users of:')} {maGreen(nickname)}\n", 0.03)

    for tl, url in cf_us:
        mess = f"""{display_extra} {maBold('Site:')} {maBold(tl)}
{display_info} {maCyan('URL:')} {maUnderline(url)}
{display_validate} {maGreen('The user')} "{maGreen(nickname)}" {maGreen('was found on the website')}"""
        write_effect(mess, 0.0005)
        space_between()
    write_effect(f"\n{display_info} The user {maBold(nickname)} was found on {maGreen(len(cf_us))} of {maMagenta(len(data))} websites", 0.03)
    write_effect(f"{display_validate} Finished on: '{maGreen(end)}' seconds {maGreen(happy)}", 0.03)

    return len(cf_us), end

def execute_user():
    """
    Entry point function to execute the user search process.
    Handles input of nickname, selection of TOR, regular and NSFW site search,
    and optional deep analysis using Google Dorking.
    """

    print(f"{display_info} Enter a user like: john_doe\n{display_info} Don't use spaces in the username!")

    nickname = input(f'\n×××{maRed("[")}{maBold("SPY-USERNAME")}{maRed("]")}---> ').strip()
    if not nickname: raise Exception(f"{display_error} You can't leave the username empty! {maRed(angry)}")
    if " " in nickname: raise Exception(f"{display_error} Error, the nickname can't have spaces! example: john_doe")
    file = f"data/users/users_{nickname}_results.md"
    save_data(file, f'\n# <center>👤 Search of the user {nickname} in 200+ websites</center>\n---', None, "a", False)

    type = ask_connect()

    wait_out(0.3)
    write_effect(f'\n{maYellow("Searching user:")} {maYellow(nickname)}{maYellow("...")}', 0.05)

    nrm_wb, tm = execute_thr(type, nickname, "tools/sites_user/websites.json", "websites")
    adult_search = str(input(f"\n{display_question} Do you want to search user {maBold(nickname)} in {maMagenta('NSFW')} websites? ({maGreen('y')}/{maRed('n')}): "))
    nsfw_wb = 0
    ns_tm = 0

    save_data(file, f"## 🖥️ Confirmed users of {nickname} on normal websites", "---\n", "a", False)
    for tl, url in cf_us: save_data(file, f"- [{tl}]({url})", None, "a", False)

    if check_key(adult_search):
        save_data(file, '\n---\n', f'## Confirmed users {nickname} in ~~NSFW~~ websites 🔞\n---\n', "a", False)
        wait_out(0.3)
        nsfw_wb, ns_tm = execute_thr(type, nickname, "tools/sites_user/nsfw_websites.json", "nsfw_websites")
        for tl, url in cf_us: save_data(file, f"- 🔞 [{tl}]({url})", None, "a", False)

    save_data(file, "\n---\n## ❓ Unconfirmed Users:\n", None, "a", False)
    for tl, url in nc_us: save_data(file, f"- ⚠️ [{tl}]({url})", None, "a", False)

    save_data(file, "\n---", "## 🎭 Manual user confirmation:\n", "a", False)
    for tl, url in fr_us: save_data(file, f"- 🔍 [{tl}]({url})", None, "a", False)

    mess = f"""
\n---
## 📑 Final Summary

- 👤 Total Confirmed Users: **{nrm_wb + nsfw_wb}**
- 🕒 Total amount of time has taken to process: **{tm + ns_tm} Seconds.**
- 🖥️ Total Confirmed Users on **"Normal Websites"**: **{nrm_wb}**
- 🔞 Total Confirmed Users on **"~~NSFW Websites~~"**: **{nsfw_wb}**
- ❓ Total **Unconfirmed** Users: **{len(nc_us)}**
- 🎭 Manual user verification: **{len(fr_us)}**
    """
    if type == requests:
        mess += "\n- 🧅 Tor used: ❌"
    else: mess +=  "\n- 🧄 Tor used: ✅"

    save_data(file, mess, "> Always check the websites one by one it's **NOT** 100% accurate\n> Check too the **Unconfirmed/Possible users**, it could have **False Positives**", "a", True)
    ask_input = str(input(f"\n{display_question} Do you want to make a search the user {maBold(nickname)} using Google Dorks? ({maGreen('y')}/{maRed('n')}): "))

    if check_key(ask_input):
        save_data(file, f'\n---\n## <center>🔍 Searching the user {nickname} using the Google Dorks module</center>\n', None, "a", False)

        sel = str(input(f"{display_question} Do you want to use a Tor network for this module? ({maGreen('y')}/{maRed('n')}): ")).strip()
        tor = check_key(sel)
        if tor: gg_connection(True)

        wait_out(0.5)

        ls_search_user = [
           (f'descr="{nickname}"', 10),
           (f'descr="{nickname}"&docs', 10),
           (f'descr="{nickname}"&email', 10),
           (f'descr="{nickname}"&phone', 10),
           (f'descr="{nickname}"&adr', 10),
           (f'descr="{nickname}"&dbase', 10),
           (f'descr="{nickname}"&cv', 10),
           (f'descr="{nickname}"&cv&docs', 10)
        ]

        multi_search(1, ls_search_user, file, tor)
