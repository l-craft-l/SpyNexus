"""
This module powers the Google Dorking capability of SpyNexus, providing
smart parsing and automated execution of advanced Google search queries.
It includes features for single and multi-search execution using Google Dorks,
a system of custom commands for convenience, and optional routing via the
Tor network for anonymity. The module also handles user input, query validation,
error handling, and formatted output to the terminal.

Key features:
- Custom command parser for simplified Google Dorking
- Support for single and multiple queries
- Optional Tor support for anonymous searching
- Dynamic terminal feedback and result saving
"""

import requests
import time
import random
from googlesearch import search as dorking_google
from bs4 import BeautifulSoup
from core.display import (
    prRed, prGreen, prCyan, prYellow, maRed, maBlue, maCyan, maYellow, maOrange,
    maMagenta, maGreen, maPink,
    maBold, maUnderline, maBlack, maLightBlue, maLightGreen, maLightYellow, maBrown,
    maTeal, maSkyBlue, backRed, display_extra, display_error,
    display_validate, display_info, display_question, happy, sad,
    angry, pointing, nervous, surprised, waiting, write_effect,
    wait_out, space_between, between_tag, check_key
)
from core.save_data import save_data
from core.agents import agents

no_info = 'Unknown'

all_operators = [
    ("site", 'Search on a specific website. Example: site="example.com"'),
    ("title", 'Search keywords in the title of pages. Example: title="login page"'),
    ("url", 'Search keywords in the URL. Example: url="admin"'),
    ("descr", 'Search keywords in the content/description. Example: descr="password"'),
    ("rel", 'Find websites related to a domain. Example: rel="github.com"'),
    ("a_title", 'Use allintitle operator. Example: a_title="login admin"'),
    ("a_url", 'Use allinurl operator. Example: a_url="dashboard index.php"'),
    ("a_descr", 'Use allintext operator. Example: a_descr="password leaked"'),
    ("loc", 'Search results by location. Example: loc="chicago"'),
    ("auth", 'Search for specific authors. Example: auth="john doe"'),
    ("src", 'Search within a specific source. Example: src="bbc.com"'),
    ("cache", 'Find cached pages from Google. Example: cache="site.com"'),

    ("doc", 'Search for specific filetypes. Example: doc="pdf", doc="xls,docx"'),
    ("docs", 'Search for a list of common document filetypes (pdf, xls, docx, etc.)'),

    ("kword", 'Search using multiple keywords. Example: kword="admin,password,login"'),
    ("dbase", 'Search for database file references in URLs. (auto-handled, just type dbase)'),
    ("breach", 'Search for breach-related keywords in URLs. (auto-handled, just type breach)'),

    ("pass", 'Search for exposed passwords. Use: pass'),
    ("email", 'Search for email leaks. Use: email'),
    ("phone", 'Search for leaked phone numbers. Use: phone'),
    ("adr", 'Search for exposed addresses. Use: adr'),
    ("keys", 'Search for leaked API keys. Use: keys'),
    ("leak", 'Search for leaks (data/files). Use: leak')
]

def gg_connection(value=False):
    """
    Determines the HTTP request method: either standard requests or Tor proxy.

    Parameters:
        value (bool): If True, initialize and return a requests.Session object
                      with SOCKS5 proxy routing via Tor. If False, return the
                      standard requests module.

    Returns:
        requests or requests.Session: Configured interface for HTTP requests.
    """

    if value:
        from core.socks_connect import get_tor_connection
        ses = get_tor_connection()
        return ses
    else:
        return requests

def make_search(query, num_of_results, pause, file, tor=False):
    """
    Executes a Google Dork search based on the final parsed query.
    Handles request retries, result formatting, and optional Tor usage.

    Parameters:
        query (str): A final Google Dork query string.
        num_of_results (int): How many search results to retrieve.
        pause (int): Delay in seconds between each request.
        file (str): Destination filepath to save formatted results.
        tor (bool): Whether to route requests through the Tor network.

    Side Effects:
        - Results are printed to the terminal.
        - Results are saved to a text file.
        - Prints errors or warnings for invalid links or failed requests.
    """

    total_search_results = 0
    num_of_no_results = 0
    first_result = False
    for url in dorking_google(query, num_results=num_of_results):

        if num_of_no_results >= 5 or first_result == None:
            write_effect(f'{display_error} There are not enough results for this search {maBlue(sad)}', 0.05)
            break

        if not url or not url.startswith(('http://', 'https://')):
            write_effect(f'{display_error} Error, the url is invalid: {maRed(url)}', 0.02)
            num_of_no_results += 1
            if first_result == False and url == '':
                first_result = None
            space_between()
            continue

        select_agent = agents()
        time.sleep(pause)
        try:
            connection = gg_connection(tor)
            result_dork = connection.get(url, headers=select_agent, timeout=30)

            if result_dork.status_code != 200:
                write_effect(f"{display_error} Error, can't check the url, status code: {maRed(result_dork.status_code)}, {maRed(url)}", 0.02)
                space_between()
                continue

            try:
                soup = BeautifulSoup(result_dork.text, 'html.parser')
                title_url = soup.title.text if soup.title else f"{no_info}"
                description_tag = soup.find('meta', attrs={'name': 'description'})
                description_url = description_tag["content"] if description_tag else f"{no_info}"
            except AssertionError:
                write_effect(f'{display_error} Assertion Error in the site. {maRed(url)}', 0.05)
                space_between()
                continue
            except Exception as err:
                write_effect(f"{display_error} Another error has ocurred, {maRed(err)}\n{display_info} {maBold('URL:')} {maUnderline(url)}", 0.02)
                space_between()
                continue

            if file:
                if title_url != no_info:
                    write_effect(f'{display_info} {maBold("Site")}: {maSkyBlue(title_url)}', 0.005)
                    save_data(file, None, f"Site: {title_url}", 'a', False)
                else:
                    write_effect(f"{display_question} {maBold('Site')}: {maYellow(no_info)}", 0.005)

                if description_url != no_info:
                    write_effect(f"{display_extra} {maBold('Description')}: {maGreen(description_url)}", 0.005)
                    save_data(file, None, f"Description: {description_url}", 'a', False)
                else:
                    write_effect(f"{display_question} {maBold('Description')}: {maYellow(no_info)}", 0.005)

                write_effect(f"{display_info} {maCyan('URL')}: {maUnderline(url)}", 0.005)
                space_between()
                URL = f'URL: {url}'
                save_data(file, URL, f"{'~'*50}", 'a', False)

            num_of_no_results = 0
            first_result = True
            total_search_results += 1

        except requests.exceptions.RequestException as url_err:
            write_effect(f'{display_error} Another error has ocurred, {maRed(url_err)}', 0.02)
            num_of_no_results += 1
            space_between()

        except requests.exceptions.HTTPError as http_err:
            write_effect(f'{display_error} Error in HTTP, {maRed(http_err)}', 0.02)
            space_between()

        except requests.exceptions.ConnectionError:
            write_effect(f"{display_error} Error, can't connect to url... {maYellow(waiting)}", 0.02)
            space_between()

        except requests.exceptions.ReadTimeout as rd_error:
            write_effect(f'{display_error} Error, read timeout exceeded, {maRed(rd_error)}', 0.02)
            space_between()

    if total_search_results <= 0:
        write_effect(f'\n{display_extra} There were a total of "{total_search_results}" confirmed searches {maBlue(sad)}', 0.05)
    else:
        write_effect(f'\n{display_info} There were a total of "{total_search_results}" confirmed searches {maGreen(happy)}', 0.02)


#########################
# special search of google/dorking
#########################

def search_dork(dork_query, results, delay, file, tor=False):
    """
    Converts a user-friendly query containing smart keywords into a valid
    Google Dork query, then triggers a search.

    Parameters:
        dork_query (str): Raw search string using simplified custom syntax.
        results (int): Number of search results desired.
        delay (int): Time in seconds to pause between results.
        file (str): Path to a file where results are saved.
        tor (bool): Whether to use the Tor proxy session for anonymity.

    Behavior:
        - Automatically converts special terms into valid search operators.
        - Validates and handles malformed or empty commands.
        - Delegates execution to make_search().
    """

    final_search = ''

    site_search = 'site:'
    related_search = 'related:'
    intext_search = 'intext:'
    title_search = 'intitle:'
    url_search = 'inurl:'
    file_tp = 'filetype:'
    aut_search = 'inauthor:'
    src_search = 'source:'
    loc_search = 'location:'
    cac_search = 'cache:'

    allintitle_search = 'allintitle:'
    allinurl_search = 'allinurl:'
    allintext_search = 'allintext:'

    all_pass = ['password', 'passwd', 'admin_password', 'user_password',
    'login_password', 'contraseña', 'contrasena', 'clave']

    all_email = ['email', 'e-mail', 'correo', '@gmail.com', '@hotmail.com',
    '@protonmail.com', '@yahoo.com', '@outlook.com', '@edu', '@gov']

    all_ph = ['phone', 'phone number', 'mobile', 'telefono', 'movil', 'celular',
    'numero', 'contacto']

    all_adr = ['address', 'billing address', 'shipping address', 'direccion',
    'residencia', 'ubicacion', 'direccion postal']

    all_doc = ['pdf', 'txt', 'xlsx', 'docx', 'pptx', 'json', 'log', 'xls', 'sql', 'env', 'db', 'bak',
    'xml', 'csv', 'ini', 'yml', 'conf']

    possible_breaches = ['admin', 'phpMyAdmin', 'DB_PASSWORD', 'cpanel',
    'dashboard', 'adminpanel', 'administrator', 'admin/login', 'config.php', '.env',
    'wp-admin', 'login.php', 'root', 'index of /admin', 'ftp', 'ssh']

    all_db = ['database', 'sql dump', 'mysql', 'postgres', 'mongodb', 'oracle',
    'DB_USER', 'DB_HOST', 'DB_NAME']

    all_ky = ['api_key', 'api-token', 'secret', 'client_secret', 'private_key',
    'auth_token', 'access_token', 'github_token']

    all_sn = ['confidential', 'internal use only', 'do not distribute', 'restricted',
    'private', 'classified', 'sensitive', 'top secret', 'confidencial', 'clasificado',
    'restringido', 'privado', 'no distribuir', 'sensible']

    dork_query.lower()
    parts = dork_query.split('&')

    def command_search(cmd, dork, part, final_search):
        if part.startswith(f'{cmd}='):
            ext = part.split('=')[1].strip('" ')
            if ext:
                final_search += f'{dork}{ext} '
            else:
                write_effect(f"{display_error} You can't leave the command '{cmd}' empty!", 0.03)
                final_search = ''
        elif part == cmd:
            write_effect(f"{display_error} Error, the command '{cmd}' can't be empty!", 0.02)
        return final_search

    def special_command(cmd, dork, part, list, final_search):
        if part == cmd:
            if dork != None:
                final_search += "OR".join([f' {dork}{ext} ' for ext in list])
            else:
                final_search += "OR".join([f' "{ext}" ' for ext in list])
        return final_search

    for part in parts:
        part = part.strip()

        final_search = command_search('site', site_search, part, final_search)
        final_search = command_search('title', title_search, part, final_search)
        final_search = command_search('url', url_search, part, final_search)
        final_search = command_search('descr', intext_search, part, final_search)
        final_search = command_search('rel', related_search, part, final_search)
        final_search = command_search('a_title', allintitle_search, part, final_search)
        final_search = command_search('a_url', allinurl_search, part, final_search)
        final_search = command_search('a_descr', allintext_search, part, final_search)
        final_search = command_search('loc', loc_search, part, final_search)
        final_search = command_search('auth', aut_search, part, final_search)
        final_search = command_search('src', src_search, part, final_search)
        final_search = command_search('cache', cac_search, part, final_search)

        final_search = special_command('docs', file_tp, part, all_doc, final_search)

        if part == 'dbase':
            final_search += "OR".join([f' {url_search}"{ex}" ' for ex in all_db])
        if part == 'breach':
            final_search += "OR".join([f' {url_search}"{ex}" ' for ex in possible_breaches])

        if part.startswith('doc='):
            cont = part.split("=")[1].strip('" ')
            if cont:
                files = [fl.strip() for fl in cont.split(",") if fl.strip() in all_doc]
                if files: final_search += "OR".join(f" {file_tp}{file} " for file in files)
                else: final_search += f" {file_tp}{cont} "
            else: write_effect(f"{display_error} The command 'doc' can't be empty!", 0.005)

        if part.startswith('kword='):
            cont = part.split("=")[1].strip('" ')
            if cont:
                kwr = [keyword.strip() for keyword in cont.split(",")]
                if kwr: final_search += "OR".join(f' "{ky}" ' for ky in kwr)
                else: final_search += f' "{cont}" '
            else: write_effect(f"{display_error} The command 'kword' can't be empty!", 0.005)

        final_search = special_command('pass', None, part, all_pass, final_search)
        final_search = special_command('email', None, part, all_email, final_search)
        final_search = special_command('phone', None, part, all_ph, final_search)
        final_search = special_command('adr', None, part, all_adr, final_search)
        final_search = special_command('keys', None, part, all_ky, final_search)
        final_search = special_command('leak', None, part, all_sn, final_search)


    if final_search == '':
        write_effect(f"{display_error} Error, the query is empty! {maRed(angry)}", 0.03)
    else:
        space_between()
        print(f"{display_extra} Command converted: {maBold(final_search)}")
        space_between()
        make_search(final_search, results, delay, file, tor)



def multi_search(num, main_ls, file, tor=False):
    """
    Executes a batch of multiple search queries sequentially.
    Used for automating user-profile searches, leak detection, etc.

    Parameters:
        num (int): Number of separate search commands to execute.
        main_ls (list or None): Optional list of prebuilt search tuples.
                                Each tuple contains (query, result count, delay).
        file (str): Path to save combined output of all searches.
        tor (bool): Enables Tor for the entire batch if set True.

    Notes:
        If no list is passed, the function will prompt the user to enter
        each command manually making the custom option.
    """

    if not num or num <= 0:
        raise Exception(f"{display_error} Error, the multiple search is {maBold('0')} or not given!")

    list_src = []
    num_av = 0
    if not main_ls or main_ls == None:
        for avail in range(0, num):
            num_av += 1
            srch = str(input(f"\n×××{maRed('[')}{maBold('SEARCH')}-{maBold(num_av)}{maRed(']')}---> ")).strip().lower()

            if len(srch) <= 0:
                raise Exception(f"{display_error} Error, the search can't be empty! {maRed(angry)}")
            rets = int(input(f"×××{maRed('[')}{maBold('RESULTS-OF-SEARCH')}-{maBold(num_av)}{maRed(']')}---> "))
            if rets <= 0:
                raise Exception(f"{display_error} Error, the results can't be 0!")
            dly = int(input(f"×××{maRed('[')}{maBold('DELAY-OF-SEARCH')}-{maBold(num_av)}{maRed(']')}---> "))
            if dly <= 0:
                raise Exception(f"{display_error} Error, the delay can't be below or equals to 0!")

            list_src.append((srch, rets, dly))
        main_ls = list_src

    num_cmds = 0
    for srch, rets, dly in main_ls:
        num_cmds += 1
        messg = f'\nMaking search number "{num_cmds}"...\nThe command is: {srch}\n'

        save_data(file, f"\nResults of command: {srch}\n", None, "a", False)
        write_effect(maYellow(messg), 0.05)
        search_dork(srch, rets, dly, file, tor)
    save_data(file, None, None, "a", True)



def three_pr(sh):
    """
    Utility function to prompt user for three core search parameters:
    search string, number of results, and delay between queries.

    Parameters:
        sh (str): Short label shown in the prompt UI.

    Returns:
        tuple: (search_term: str, number_of_results: int, delay: int)

    Raises:
        Exception: If the input is empty or invalid (e.g. delay = 0).
    """

    main1 = input(f'\n×××{maRed("[")}{maBold(sh)}{maRed("]")}---> ').strip().lower()
    if len(main1) <= 0:
        raise Exception(f"{display_error} Error, you can't leave the {maBold(sh)} empty! {maRed(angry)}")

    results = int(input(f'×××{maRed("[")}{maBold("RESULTS")}{maRed("]")}---> '))
    if results <= 0:
        raise Exception(f"{display_error} You can't leave the number of results below or equals to 0! {maRed(angry)}")

    delay = int(input(f'×××{maRed("[")}{maBold("DELAY")}{maRed("]")}---> '))
    if delay <= 0:
        raise Exception(f"{display_error} You can't leave the time of delay below or equals to 0! {maRed(angry)}")
    return main1, results, delay



def available_commands():
    """
    Presents a menu of high-level Google Dorking presets (user search,
    email leaks, custom queries, etc.)

    After user selection, this function handles:
    - Asking for inputs (keywords, targets)
    - Prebuilding related queries with smart operators
    - Invoking multi_search or search_dork with parsed data

    Prompts:
        - Tor connection option
        - Type of dork to perform
        - Inputs for filename, delays, result limits
    """

    sel = str(input(f"{display_question} Do you want to use a Tor network for this module? ({maGreen('y')}/{maRed('n')}): ")).strip()
    tor = check_key(sel)
    if tor: gg_connection(True)

    help_commands = [
        ('User', 'Search info from a user or a person in the internet.'),
        ('Profile-user', 'Search info from a user in a website in specific.'),
        ('Site-search', 'Search info from a website.'),
        ('Email', 'Search info from a email.'),
        ('Phone', 'Search info from a phone number.'),
        ('Custom', 'You can search for whatever you want(using dorks).'),
    ]
    num_commands = 0
    print()
    for cmds, des in help_commands:
        num_commands += 1
        write_effect(f"{maRed('[')}{maBold(num_commands)}{maRed(']')}: {maBold(cmds)}: {maCyan(des)}", 0.005)

    cmd = int(input(f"\n×××{maRed('[')}{maBold('SPY-DORKING')}{maRed(']')}---> "))

    if cmd == 1:
       user, res, dly = three_pr("DORK-USER")
       file = f"data/dorks/user_dorks/results_{user}_file.txt"

       ls_search_user = [
           (f'a_descr="{user}"', res, dly),
           (f'a_descr="{user}"&docs', res, dly),
           (f'a_descr="{user}"&email', res, dly),
           (f'a_descr="{user}"&phone', res, dly),
           (f'a_descr="{user}"&adr', res, dly),
           (f'a_descr="{user}"&dbase', res, dly)
       ]

       multi_search(1, ls_search_user, file, tor)

    elif cmd == 2:
        usr = input(f"\n×××{maRed('[')}{maBold('DORK-PROFILE')}{maRed(']')}---> ").strip()
        if len(usr) <= 0: raise Exception(f"{display_error} Error, you can't leave the profile empty!")
        site, res, dly = three_pr("WEBSITE")

        file = f"data/dorks/profile_dorks/results_{usr}_file.txt"

        ls_search_profile = [
            (f'site="{site}"&descr="{usr}"', res, dly),
            (f'site="{site}"&descr="{usr}"&email', res, dly),
            (f'site="{site}"&descr="{usr}"&phone', res, dly),
            (f'site="{site}"&descr="{usr}"&pass', res, dly),
            (f'site="{site}"&descr="{usr}"&adr', res, dly)
        ]

        multi_search(1, ls_search_profile, file, tor)

    elif cmd == 3:
       site, res, dly = three_pr("DORK-WEBSITE")
       file = f"data/dorks/site_dorks/results_{site}_file.txt"

       ls_search_site = [
           (f'site="{site}"', res, dly),
           (f'rel="{site}"', res, dly),
           (f'site="{site}"&docs', res, dly),
           (f'site="{site}"&email', res, dly),
           (f'site="{site}"&docs&email', res, dly),
           (f'site="{site}"&phone', res, dly),
           (f'site="{site}"&docs&phone', res, dly),
           (f'site="{site}"&pass', res, dly),
           (f'site="{site}"&breach', res, dly),
           (f'site="{site}"&keys', res, dly),
           (f'site="{site}"&docs&leak', res, dly),
           (f'site="{site}"&dbase', res, dly)
       ]

       multi_search(1, ls_search_site, file, tor)

    elif cmd == 4:
        email, res, dly = three_pr("DORK-EMAIL")
        file = f"data/dorks/email_dorks/results_{email}_file.txt"

        ls_search_email = [
            (f'descr="{email}"', res, dly),
            (f'descr="{email}"&docs', res, dly),
            (f'descr="{email}"&pass', res, dly),
            (f'descr="{email}"&docs&pass', res, dly),
            (f'descr="{email}"&dbase', res, dly)
        ]

        multi_search(1, ls_search_email, file, tor)

    elif cmd == 5:
        phone, res, dly = three_pr("DORK-PHONE")
        file = f"data/dorks/phone_dorks/results_{phone}_file.txt"

        ls_search_phone = [
            (f'a_descr="{phone}"', res, dly),
            (f'a_descr="{phone}"&docs', res, dly),
            (f'a_descr="{phone}"&dbase', res, dly)
        ]

        multi_search(1, ls_search_phone, file, tor)

    elif cmd == 6:
        write_effect(f"\n{display_info} 1: {maGreen('Simple Search')}\n{display_info} 2: {maGreen('Multiple Searches')}", 0.02)

        option = int(input(f"\n×××{maRed('[')}{maBold('SELECT-OPTION')}{maRed(']')}---> "))
        if option == 1:
            print()
            for comm, des in all_operators:
                print(f"{display_extra} {comm.ljust(7)} --> {maSkyBlue(des)}")

            srch, res, dly = three_pr("CUSTOM-SEARCH")
            fl_user = str(input(f"×××{maRed('[')}{maBold('FILE')}{maRed(']')}---> ")).strip()
            if len(fl_user) <= 0: raise Exception(f"{display_error} Error, the file name can't be empty!")

            file = f"data/dorks/custom/search_{fl_user}_results.txt"
            wait_out(0.5)
            print()

            search_dork(srch, res, dly, file, tor)

            save_data(file, None, None, "a", True)
        elif option == 2:
            print()
            for comm, des in all_operators:
                print(f"{display_extra} {comm.ljust(7)} --> {maSkyBlue(des)}")

            count = int(input(f"\n×××{maRed('[')}{maBold('NUM-OF-SEARCHES')}{maRed(']')}---> "))
            if count <= 0: raise Exception(f"{display_error} Error, the number of searches can't be below or equals to 0!")

            fl_user = str(input(f"×××{maRed('[')}{maBold('FILE')}{maRed(']')}---> ")).strip()
            if len(fl_user) <= 0: raise Exception(f"{display_error} Error, the file name can't be empty!")
            file = f"data/dorks/custom/search_{fl_user}_results.txt"

            multi_search(count, None, file, tor)

        else: raise Exception(f"{display_error} Error, select a valid option! {maRed(angry)}")

