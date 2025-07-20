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
import urllib.parse
import warnings
from googlesearch import search as dorking_google
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
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
from http import HTTPStatus

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
no_info = 'Unknown'
errs = []
conf = []

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
    ("conf", 'Search for exposed configuration files. Usage: config'),

    ("pass", 'Search for exposed passwords. Use: pass'),
    ("email", 'Search for email leaks. Use: email'),
    ("phone", 'Search for leaked phone numbers. Use: phone'),
    ("adr", 'Search for exposed addresses. Use: adr'),
    ("keys", 'Search for leaked API keys. Use: keys'),
    ("leak", 'Search for leaks (data/files). Use: leak'),
    ("cv", 'Search for public CVs, resumes, or curriculum vitae. Use: cv'),
    ("contr", 'Search for confidential or legal contracts online. Use: contract'),
    ("invoice", 'Search for exposed invoices or billing documents. Use: invoice'),
    ("index", 'Search for publicly exposed web directories (index of). Use: index'),
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

def make_search(query, num_of_results, file, tor=False):
    """
    Executes a Google Dork search based on the final parsed query.
    Handles request retries, result formatting, and optional Tor usage.

    Parameters:
        query (str): A final Google Dork query string.
        num_of_results (int): How many search results to retrieve.
        file (str): Destination filepath to save formatted results.
        tor (bool): Whether to route requests through the Tor network.

    Side Effects:
        - Results are printed to the terminal.
        - Results are saved to a markdown file.
        - Prints errors or warnings for invalid links or failed requests.
    """
    MAX_RETRIES = 4
    retry_count = 0

    total_search_results = 0
    connection = gg_connection(tor)

    while retry_count < MAX_RETRIES:
        get_list = []
        try:
            for url in dorking_google(query, num_results=num_of_results):
                if not url or not url.startswith(('http://', 'https://')): continue
                if url: get_list.append(url)

            if get_list: break
            else:
                retry_count = MAX_RETRIES
                break

        except Exception as err:
            if "429" in str(err):
                retry_count += 1
                write_effect(f"{display_error} Oops!, it seems Google detect an {maRed('suspicious activity')}...\n{display_info} Trying to make the search again in 30 seconds...\n{display_info} Try change your IP Address with a {maBold('VPN')}, to evade the block from Google...", 0.02)
                space_between()
                time.sleep(30)

    if not get_list:
        save_data(file, "- No **results found** on this search ❌", None, "a", False)
        write_effect(f"{display_error} There are not enough results for this search {maBlue(sad)}", 0.03)
        return

    for link in get_list:
        select_agent = agents()
        time.sleep(random.uniform(0.5, 2))
        try:
            result_dork = connection.get(link, headers=select_agent, timeout=30)

            if result_dork.status_code != 200:
                write_effect(f"{display_error} Error, can't check the url, status code: {maRed(result_dork.status_code)}, {maRed(link)}", 0.02)
                errs.append((link, result_dork.status_code))
                space_between()
                continue

            try:
                soup = BeautifulSoup(result_dork.text, 'html.parser')
                title_url = soup.title.text if soup.title else no_info
                description_tag = soup.find('meta', attrs={'name': 'description'})
                description_url = description_tag["content"] if description_tag else no_info
            except AssertionError:
                write_effect(f'{display_error} Assertion Error in the site. {maRed(link)}', 0.05)
                space_between()
                continue
            except Exception as err:
                write_effect(f"{display_error} Another error has ocurred, {maRed(err)}\n{display_info} {maBold('URL:')} {maUnderline(link)}", 0.02)
                space_between()
                continue

            total_search_results += 1
            conf.append(link)

            if file:
                if title_url != no_info:
                    write_effect(f'{display_info} {maBold("Site")}: {maSkyBlue(title_url)}', 0.005)
                    save_data(file, f"\n{total_search_results}. [{title_url}]({link})", None, 'a', False)
                else:
                    write_effect(f"{display_question} {maBold('Site')}: {maYellow(no_info)}", 0.005)

                if description_url != no_info:
                    write_effect(f"{display_extra} {maBold('Description')}: {maGreen(description_url)}", 0.005)
                    save_data(file, f"> {description_url}", None, 'a', False)
                else:
                    write_effect(f"{display_question} {maBold('Description')}: {maYellow(no_info)}", 0.005)

                write_effect(f"{display_info} {maCyan('URL')}: {maUnderline(link)}", 0.005)
                space_between()
                if title_url == no_info:
                    save_data(file, f'{total_search_results}. **Website unknown:** ({link})', None, 'a', False)

        except requests.exceptions.RequestException as url_err:
            write_effect(f'{display_error} Another error has ocurred, {maRed(url_err)}', 0.02)
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

    save_data(file, "\n---\n", None, "a", False)
    if total_search_results <= 0:
        write_effect(f'\n{display_extra} There were a total of "{total_search_results}" confirmed searches {maBlue(sad)}', 0.05)
    else:
        write_effect(f'\n{display_info} There were a total of "{total_search_results}" confirmed searches {maGreen(happy)}', 0.02)


#########################
# special search of google/dorking
#########################

def search_dork(dork_query, results, file, tor=False):
    """
    Converts a user-friendly query containing smart keywords into a valid
    Google Dork query, then triggers a search.

    Parameters:
        dork_query (str): Raw search string using simplified custom syntax.
        results (int): Number of search results desired.
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

    all_cf = ['ini', 'json', 'conf', 'csv', 'xml', 'sql', 'env', 'db', 'bak']

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

    all_idx = ['index of /admin', 'index of /backup', 'index of /private', 'index of /db',
    'index of /ftp', 'index of /documents']

    all_ivc = ['invoice', 'invoice number', 'total amount', 'quote', 'quotation',
    'factura']

    all_ctr = ['confidential contract', 'service level agreement', 'contract between',
    'license agreement', 'memorandum of understanding', 'contrato confidencial',
    'contrato']

    all_cv = ['curriculum', 'curriculum vitae', 'resume', 'CV', 'CV of', 'contact',
    'hoja de vida']

    dork_query.lower()
    parts = dork_query.split('&')

    def command_search(cmd, dork, part, final_search):
        if part.startswith(f'{cmd}='):
            ext = part.split('=')[1].strip('" ')
            if ext:
                cont = [dt.strip() for dt in ext.split(",")]
                if cont and dork: final_search += "OR".join(f' {dork}"{dt}" ' for dt in cont)
                elif cont and not dork: final_search += "OR".join(f' "{dt}" ' for dt in cont)
                else:
                    if dork: final_search += f' {dork}"{ext}" '
                    else: final_search += f' "{ext}" '
            else: write_effect(f"{display_error} You can't leave the command '{cmd}' empty!", 0.03)

        elif part == cmd: write_effect(f"{display_error} Error, the command '{cmd}' can't be empty!", 0.02)
        return final_search

    def special_command(cmd, dork, part, list, final_search):
        if part == cmd:
            if dork: final_search += "OR".join([f' {dork}"{ext}" ' for ext in list])
            else: final_search += "OR".join([f' "{ext}" ' for ext in list])
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
        final_search = command_search('kword', None, part, final_search)


        final_search = special_command('dbase', url_search, part, all_db, final_search)
        final_search = special_command('breach', url_search, part, possible_breaches, final_search)
        final_search = special_command('index', title_search, part, all_idx, final_search)
        final_search = special_command('pass', None, part, all_pass, final_search)
        final_search = special_command('email', None, part, all_email, final_search)
        final_search = special_command('phone', None, part, all_ph, final_search)
        final_search = special_command('adr', None, part, all_adr, final_search)
        final_search = special_command('keys', None, part, all_ky, final_search)
        final_search = special_command('leak', None, part, all_sn, final_search)
        final_search = special_command('invoice', None, part, all_ivc, final_search)
        final_search = special_command('contr', None, part, all_ctr, final_search)
        final_search = special_command('cv', None, part, all_cv, final_search)

        if part.startswith("doc="):
            ext = part.split("=")[1].strip('" ')
            if ext:
                cont = [dt.strip() for dt in ext.split(",")]
                if cont: final_search += "OR".join(f' {file_tp}{dt} ' for dt in cont)
                else: final_search += f' {file_tp}{ext} '
            else: write_effect(f"{display_error} You can't leave the command '{cmd}' empty!", 0.03)

        if part == "docs": final_search += "OR".join(f' {file_tp}{fl} ' for fl in all_doc)
        if part == "conf": final_search += "OR".join(f' {file_tp}{fl} ' for fl in all_cf)

    if final_search == '':
        write_effect(f"{display_error} Error, the query is empty! {maRed(angry)}", 0.03)
    else:
        space_between()
        print(f"{display_extra} Command converted: {maBold(final_search)}")
        save_data(file, f"## 🔍 Search: `{dork_query}` [Check](https://www.google.com/search?q={urllib.parse.quote_plus(final_search.strip())}) \n**Searched results:** {results}\n", "### ✅ Results", "a", False)
        space_between()
        make_search(final_search, results, file, tor)



def multi_search(num, main_ls, file, tor=False):
    """
    Executes a batch of multiple search queries sequentially.
    Used for automating user-profile searches, leak detection, etc.

    Parameters:
        num (int): Number of separate search commands to execute.
        main_ls (list or None): Optional list of prebuilt search tuples.
                                Each tuple contains (query, result count).
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

            list_src.append((srch, rets))
        main_ls = list_src

    num_cmds = 0
    for srch, rets in main_ls:
        num_cmds += 1
        messg = f'\nMaking search number "{num_cmds}"...\nThe command is: {srch}\n'
        write_effect(maYellow(messg), 0.05)
        search_dork(srch, rets, file, tor)

    if not errs: save_data(file, "\n- No errors detected ✅", None, "a", False)
    else:
        save_data(file, "\n---\n### ❌ Errors", None, "a", False)
        for lk, err in errs:
            try:
                status = HTTPStatus(err).phrase
            except Exception:
                status = "Unknown Status"
            save_data(file, f'- [Link]({lk}) -> **{err} {status}**', None, "a", False)

    mess = f"""
\n---\n## 📊 Final Summary\n\n
- 🔍 Total searches: {num_cmds}
- 📑 Total Valid Results: {len(conf)} links
- ⚠️ Total Errors: {len(errs)}
    """

    if not tor:
        mess += '\n- 🧅  Tor used: ❌'
    else: mess += '\n- 🧅  Tor ued: ✅'
    tip = f'---\n> Remember this searches are **NOT** 100% acurate, check the links given one by one.'
    save_data(file, mess, tip, "a", True)


def three_pr(sh):
    """
    Utility function to prompt user for three core search parameters:

    Parameters:
        sh (str): Short label shown in the prompt UI.

    Returns:
        tuple: (search_term: str, number_of_results: int)

    Raises:
        Exception: If the input is empty or invalid (e.g. results = 0).
    """

    main1 = input(f'\n×××{maRed("[")}{maBold(sh)}{maRed("]")}---> ').strip().lower()
    if len(main1) <= 0:
        raise Exception(f"{display_error} Error, you can't leave the {maBold(sh)} empty! {maRed(angry)}")

    results = int(input(f'×××{maRed("[")}{maBold("RESULTS")}{maRed("]")}---> '))
    if results <= 0:
        raise Exception(f"{display_error} You can't leave the number of results below or equals to 0! {maRed(angry)}")

    return main1, results



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
        - Inputs for filename and result limits
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
       user, res = three_pr("DORK-USER")
       file = f"data/dorks/user_dorks/results_{user}_file.md"
       mess = f"\n## <center>👤 Search of the user {user} using Google Dorks</center>"
       save_data(file, mess, None, "a", False)

       ls_search_user = [
           (f'a_descr="{user}"', res),
           (f'a_descr="{user}"&docs', res),
           (f'a_descr="{user}"&email', res),
           (f'a_descr="{user}"&phone', res),
           (f'a_descr="{user}"&adr', res),
           (f'a_descr="{user}"&dbase', res),
           (f'a_descr="{user}"&cv', res),
           (f'a_descr="{user}"&cv&docs', res)
       ]

       multi_search(1, ls_search_user, file, tor)

    elif cmd == 2:
        usr = input(f"\n×××{maRed('[')}{maBold('DORK-PROFILE')}{maRed(']')}---> ").strip()
        if len(usr) <= 0: raise Exception(f"{display_error} Error, you can't leave the profile empty!")
        site, res = three_pr("WEBSITE")

        file = f"data/dorks/profile_dorks/results_{usr}_file.md"
        mess = f'\n## <center>🖥️ Search of the user {usr} on the website {site} using Google Dorks</center>'

        save_data(file, mess, None, "a", False)
        ls_search_profile = [
            (f'site="{site}"&descr="{usr}"', res),
            (f'site="{site}"&descr="{usr}"&email', res),
            (f'site="{site}"&descr="{usr}"&phone', res),
            (f'site="{site}"&descr="{usr}"&pass', res),
            (f'site="{site}"&descr="{usr}"&adr', res)
        ]

        multi_search(1, ls_search_profile, file, tor)

    elif cmd == 3:
       site, res = three_pr("DORK-WEBSITE")
       file = f"data/dorks/site_dorks/results_{site}_file.md"
       mess = f'\n## <center>📜 Search of the website {site} using Google Dorks'

       save_data(file, mess, None, "a", False)
       ls_search_site = [
           (f'site="{site}"', res),
           (f'rel="{site}"', res),
           (f'site="{site}"&docs', res),
           (f'site="{site}"&email', res),
           (f'site="{site}"&docs&email', res),
           (f'site="{site}"&phone', res),
           (f'site="{site}"&docs&phone', res),
           (f'site="{site}"&pass', res),
           (f'site="{site}"&breach', res),
           (f'site="{site}"&keys', res),
           (f'site="{site}"&docs&leak', res),
           (f'site="{site}"&dbase', res),
           (f'site="{site}"&index', res),
           (f'site="{site}"&conf', res),
       ]

       multi_search(1, ls_search_site, file, tor)

    elif cmd == 4:
        email, res = three_pr("DORK-EMAIL")
        file = f"data/dorks/email_dorks/results_{email}_file.md"
        mess = f'## <center>✉️ Search of the email {email} using Google Dorks</center>'

        save_data(file, mess, None, "a", False)
        ls_search_email = [
            (f'descr="{email}"', res),
            (f'descr="{email}"&docs', res),
            (f'descr="{email}"&pass', res),
            (f'descr="{email}"&docs&pass', res),
            (f'descr="{email}"&dbase', res)
        ]

        multi_search(1, ls_search_email, file, tor)

    elif cmd == 5:
        phone, res = three_pr("DORK-PHONE")
        file = f"data/dorks/phone_dorks/results_{phone}_file.md"
        mess = f'## <center>📱 Search of the phone number {phone} using Google Dorks</center>'

        save_data(file, mess, None, "a", False)
        ls_search_phone = [
            (f'a_descr="{phone}"', res),
            (f'a_descr="{phone}"&docs', res),
            (f'a_descr="{phone}"&dbase', res)
        ]

        multi_search(1, ls_search_phone, file, tor)

    elif cmd == 6:
        write_effect(f"\n{display_info} 1: {maGreen('Simple Search')}\n{display_info} 2: {maGreen('Multiple Searches')}", 0.02)

        option = int(input(f"\n×××{maRed('[')}{maBold('SELECT-OPTION')}{maRed(']')}---> "))
        if option == 1:
            print()
            for comm, des in all_operators:
                print(f"{display_extra} {comm.ljust(7)} --> {maSkyBlue(des)}")

            srch, res = three_pr("CUSTOM-SEARCH")
            fl_user = str(input(f"×××{maRed('[')}{maBold('FILE')}{maRed(']')}---> ")).strip()
            if len(fl_user) <= 0: raise Exception(f"{display_error} Error, the file name can't be empty!")

            file = f"data/dorks/custom/search_{fl_user}_results.md"
            mess = f'## <center>📝 The user selected the custom option using Google Dorks</center>'
            save_data(file, mess, None, "a", False)
            wait_out(0.5)
            print()

            search_dork(srch, res, file, tor)

            save_data(file, None, None, "a", True)
        elif option == 2:
            print()
            for comm, des in all_operators:
                print(f"{display_extra} {comm.ljust(7)} --> {maSkyBlue(des)}")

            count = int(input(f"\n×××{maRed('[')}{maBold('NUM-OF-SEARCHES')}{maRed(']')}---> "))
            if count <= 0: raise Exception(f"{display_error} Error, the number of searches can't be below or equals to 0!")

            fl_user = str(input(f"×××{maRed('[')}{maBold('FILE')}{maRed(']')}---> ")).strip()
            if len(fl_user) <= 0: raise Exception(f"{display_error} Error, the file name can't be empty!")
            file = f"data/dorks/custom/search_{fl_user}_results.md"
            mess = f'## <center>📝 The user selected the custom option using Google Dorks</center>'

            save_data(file, mess, None, "a", False)
            multi_search(count, None, file, tor)

        else: raise Exception(f"{display_error} Error, select a valid option! {maRed(angry)}")

