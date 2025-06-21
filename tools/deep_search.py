"""
This module is responsible for performing deep web and dark web searches using .onion search engines.
All traffic is routed through the Tor network to preserve user anonymity.

Features:
- Query multiple dark web search engines
- Automatic detection and skipping of unreachable or invalid links
- Optional result saving with metadata (title, description, URL)
- Safe usage warnings and connection validations

WARNING:
Use responsibly. Only for ethical, research or educational purposes.
Never attempt to access unauthorized or illegal content.
"""

from core.save_data import save_data
from core.agents import agents
from bs4 import BeautifulSoup
from core.display import (
    prRed, prGreen, prYellow, prCyan, maGreen, maYellow, maCyan,
    maOrange, maRed, maBlue, maMagenta, maBlack, maPink,
    maLightGreen, maLightBlue, maLightYellow, maBrown, maTeal,
    maSkyBlue, maBold, maUnderline, backRed, display_info,
    display_extra, display_validate, display_error, display_question,
    happy, angry, sad, pointing, waiting, nervous, surprised,
    write_effect, wait_out, space_between, between_tag, check_key
)

deep_warning = f"""
{display_error} {maMagenta("Warning – Deep Search Mode Activated")}

This module performs searches that may include results from the deep or dark web.

Make sure to:
1. Use a {maBold("VPN")} or anonymity tools ({maUnderline("like Tor or ProxyChains")})
2. Avoid clicking unknown or suspicious links
3. Never perform searches without proper {maRed("authorization")}

{maYellow("Use responsibly and only for educational or ethical purposes.")}
"""

no_info = "Unknown"
no_response = "data/deep_results/list_no_response.txt"

"""
You can add more searchers if you want to, at least you need the url
of the searcher and, it needs to ends something like this:
?p= ?query= ?=q, this means to searcher the query are you performing.
"""

searchers = {
    1: ("Torch", "http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/cgi-bin/omega/omega?P="),
    2: ("VormWeb", "http://volkancfgpi4c7ghph6id2t7vcntenuly66qjt6oedwtjmyj4tkk5oqd.onion/search?q="),
    3: ("Tordex", "http://tordexpmg4xy32rfp4ovnz7zq5ujoejwq2u26uxxtkscgo5u3losmeid.onion/search?query=")
}



def list_response(url):
    """
    Check if a URL has already failed connection in past attempts.

    Parameters:
        url (str): The URL to check against the failed list.

    Returns:
        bool: True if it failed before, else False
    """

    try:
        with open(no_response, "r") as arch:
            res = arch.read()
            if url in res: return True
    except FileNotFoundError:
        save_data(no_response, "", None, "a", False)



def save_info(query, list):
    """
    Save the successfully collected results to a file.

    Parameters:
        query (str): The original user query.
        list (list): List of tuples (title, description, URL).
    """

    file = f"data/deep_results/results_{query}_file.txt"
    save_data(file, f"\nResults of '{query}':\n", None, "a", False)

    for st, ds, url in list:
        if st != no_info:
            save_data(file, None, f"Site: {st}", "a", False)
        if ds != no_info:
            save_data(file, None, f"Description: {ds}", "a", False)
        save_data(file, f"URL: {url}", f"{'~'*50}", "a", False)
    save_data(file, None, None, "a", True)



def get_searcher():
    """
    Displays search engine options and collects user input for query and result amount.

    Returns:
        tuple: (query, search_url, result_count)
    """

    write_effect(f"\n{display_info} {maGreen('Available options:')}\n", 0.05)
    for num, (searcher, url) in searchers.items():
        write_effect(f"{maRed('[')}{maBold(num)}{maRed(']')}: {maRed(searcher)}", 0.005)

    sel = int(input(f"\n×××{maRed('[')}{maBold('SELECT-SEARCHER')}{maRed(']')}---> "))
    if sel in searchers:
        searcher, url = searchers[sel]
        print(f"\n{display_info} Searcher selected: {maBold(searcher)}")

        query = str(input(f"\n×××{maRed('[')}{maBold('QUERY')}{maRed(']')}---> ")).strip()
        if len(query) <= 0: raise Exception(f"{display_error} The query can't be empty!")

        res = int(input(f"×××{maRed('[')}{maBold('RESULTS')}{maRed(']')}---> "))
        if res <= 0: raise Exception(f"{display_error} The amount of results can't be equals or below than 0!")
        wait_out(3)
        write_effect(maYellow(f'\nSearching "{query}" in the dark web...\n'), 0.05)

        url += query
        return query, url, res
    else:
        raise Exception(f"{display_error} There's not valid option such as {maBold(sel)}!")


def obtain_results(query, lk, results):
    """
    Requests and parses dark web search results using Tor connection.

    Parameters:
        query (str): Search query.
        lk (str): Full URL to perform search.
        results (int): Maximum number of valid result pages to retrieve.
    """

    from core.socks_connect import get_tor_connection
    connect = get_tor_connection()
    main_agent = agents()
    try:
        main_query = connect.get(lk, headers=main_agent, timeout=20)
    except requests.exceptions.ConnectionError:
        raise Exception(f"{display_error} Error, can't connect to the Searcher... Are you connected to Tor Network{display_question}")
    except requests.exceptions.RequestException as err:
        raise Exception(f"{display_error} Another error has ocurred in the query: {maRed(err)}")
    if main_query.status_code != 200:
        raise Exception(f"{display_error} Another error has ocurred, status code: {maRed(main_query.status_code)}, query: {maRed(query)}")

    try:
        get_info = BeautifulSoup(main_query.text, "html.parser")
    except Exception as err: raise Exception(f"{display_error} Error, can't get the page info: {maRed(err)}")

    count = 0
    visited_urls = set()
    save_list = []

    for href in get_info.find_all('a'):
        if count >= results: break

        link = href.get('href')
        if link and '.onion' in link and link.startswith('http://'):
            if link in visited_urls: continue
            if list_response(link): continue

            visited_urls.add(link)
            link_agent = agents()

            try:
                get_link = connect.get(link, headers=link_agent, timeout=15)
                if not query in get_link.text: continue
            except requests.exceptions.ConnectionError:
                save_data(no_response, None, link, "a", False)
                continue
            except requests.exceptions.RequestException:
                write_effect(f"{display_error} Another error has ocurred in the next link: {maRed(err)}", 0.02)
                space_between()
                continue
            if get_link.status_code != 200:
                write_effect(f"{display_error} Error in the link, status code: {maRed(get_link.status_code)}, link: {maRed(link)}", 0.02)
                space_between()
                continue

            try:
                info_link = BeautifulSoup(get_link.text, "html.parser")

                title = info_link.title.text if info_link.text else no_info
                ds = info_link.find("meta", attrs={"name": "description"})
                description = ds["content"] if ds else no_info

            except Exception as err:
                write_effect(f"{display_error} Another error has ocurred in the link: {maRed(err)}", 0.02)
                space_between()
                continue

            count += 1
            if title != no_info:
                write_effect(f"{display_info} {maBold('Site:')} {maCyan(title)}", 0.005)
            else:
                write_effect(f"{display_question} {maBold('Site:')} {maYellow(no_info)}", 0.005)
            if description != no_info:
                write_effect(f"{display_extra} {maBold('Description:')} {maGreen(description)}", 0.005)
            else:
                write_effect(f"{display_question} {maBold('Description:')} {maYellow(no_info)}", 0.005)
            write_effect(f"{display_info} {maCyan('URL')}: {maUnderline(link)}", 0.005)

            space_between()
            save_list.append((title, description, link))

    sv_conf = str(input(f"\n{display_question} Do you want to save the results? ({maGreen('y')}/{maRed('n')}): "))
    if check_key(sv_conf): save_info(query, save_list)


def ex_deep():
    """
    Entry point to execute the deep search process.
    Displays warnings, selects searcher, and triggers the result collector.
    """

    write_effect(deep_warning, 0.005)

    query, url, results = get_searcher()
    obtain_results(query, url, results)
