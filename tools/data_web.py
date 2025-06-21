"""
This module is responsible for gathering and displaying public domain information
from a given website using the `whois` protocol. It also allows additional intelligence
collection through Google Dorking queries related to the same website.

Features:
- Domain WHOIS lookup (registrar, expiration, nameservers, etc.)
- Date formatting and multi-line text parsing
- Optional geolocation based on WHOIS address field
- Integration with Google Dorking for advanced website intel gathering
- Optional Tor network usage for anonymous queries
"""

import whois
import datetime
from whois import parser
from core.save_data import save_data
from tools.g_dorking import multi_search, gg_connection
from tools.coordinates import get_location
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

def get_site(site):
    """
    Retrieves WHOIS information about a given domain and displays it to the user.

    The function also saves the output to a local file and attempts to perform
    geolocation if the domain's address is provided.

    Parameters:
        site (str): The target domain name (e.g. "example.com")
    """

    global file
    file = f"data/websites/results_{site}_file.txt"
    try:
        get_data = whois.whois(site)
    except whois.parser.PywhoisError:
        raise Exception(f"{display_error} Error, the domain {maBold(site)} don't found.")
    except Exception as err:
        raise Exception(f"{display_error} Another error has occurred, {maRed(err)}")

    write_effect(f"\n{display_validate} {maGreen('Data of the website found!')} {maGreen(surprised)}\n", 0.05)
    save_data(file, f'\nResults of the website "{site}":\n', None, "a", False)

    for tag, data in get_data.items():
        tag = tag.replace("_", " ").capitalize()

        if not data or data == "null":
            write_effect(f"{display_question} {maBold(tag)}: {maYellow('Unknown')}", 0.005)
            continue

        if isinstance(data, list):
            write_effect(f"{display_info} {maBold(tag)}:", 0.005)
            save_data(file, None, f"{tag}:", "a", False)

            if len(data) == 1 and isinstance(data[0], str) and '\n' in data[0]:
                for line in data[0].splitlines():
                    write_effect(f"  {display_extra} {maGreen(line)}", 0.005)
                    save_data(file, None, f"  -> {line}", "a", False)
            else:
                for item in data:
                    if isinstance(item, datetime.datetime):
                        item = item.strftime("%Y-%m-%d %H:%M:%S")
                    write_effect(f"  {display_extra} {maGreen(item)}", 0.005)
                    save_data(file, None, f"  -> {item}", "a", False)

        elif isinstance(data, datetime.datetime):
            formatted = data.strftime("%Y-%m-%d %H:%M:%S")
            write_effect(f"{display_info} {maBold(tag)}: {maGreen(formatted)}", 0.005)
            save_data(file, None, f"{tag}: {formatted}", "a", False)

        elif isinstance(data, str) and '\n' in data:
            write_effect(f"{display_info} {maBold(tag)}:", 0.005)
            save_data(file, None, f"{tag}:", "a", False)
            for line in data.splitlines():
                write_effect(f"  {display_extra} {maGreen(line)}", 0.005)
                save_data(file, None, f"  -> {line}", "a", False)

        else:
            write_effect(f"{display_info} {maBold(tag)}: {maGreen(data)}", 0.005)
            save_data(file, None, f"{tag}: {data}", "a", False)

    try:
        get_adr = get_data.get("address")

        if get_adr != "null":
            between_tag("INFO LOCATION")
            get_location(get_adr, None, file)
        else:
            save_data(file, None, None, "a", True)

    except Exception:
        write_effect(f"{display_question} Location from {maBold(site)} not found...", 0.05)


def execute_webtool():
    """
    Main interactive CLI interface for the Website Tool.

    Prompts the user for a website domain name, performs a WHOIS lookup,
    displays the formatted results, and optionally asks the user if they want
    to perform Google Dorking analysis on the same domain with or without Tor.
    """

    print(f"{display_info} Enter a website like: example.com\n{display_info} Always put the website with his domain at the end like: .gov, .us, .com\n{display_extra} It's not necessary to put http, https at the beginning of the website")

    site = input(f"\n×××{maRed('[')}{maBold('SPY-WEBSITE')}{maRed(']')}---> ").strip()
    if not site: raise Exception(f"{display_error} Error, the website can't be empty!")

    wait_out(2)
    get_site(site)

    ask_web = str(input(f'\n{display_question} Do you want to search "{maBold(site)}" using Google Dorks? ({maGreen("y")}/{maRed("n")}): '))
    if check_key(ask_web):
        sel = str(input(f"{display_question} Do you want to use a Tor network for this module? ({maGreen('y')}/{maRed('n')}): ")).strip()
        tor = check_key(sel)
        if tor: gg_connection(True)

        wait_out(0.5)

        ls_search_site = [
           (f'site="{site}"', 10, 3),
           (f'rel="{site}"', 10, 3),
           (f'site="{site}"&docs', 10, 3),
           (f'site="{site}"&email', 10, 3),
           (f'site="{site}"&docs&email', 10, 3),
           (f'site="{site}"&phone', 10, 3),
           (f'site="{site}"&docs&phone', 10, 3),
           (f'site="{site}"&pass', 10, 3),
           (f'site="{site}"&breach', 10, 3),
           (f'site="{site}"&keys', 10, 3),
           (f'site="{site}"&docs&leak', 10, 3),
           (f'site="{site}"&dbase', 10, 3)
        ]

        multi_search(1, ls_search_site, file, tor)
