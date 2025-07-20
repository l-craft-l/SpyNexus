#!/usr/bin/python

"""
SpyNexus – Main Execution Script

This script serves as the primary entry point for the SpyNexus framework, an OSINT (Open-Source Intelligence) tool
designed for ethical information gathering, research, and cybersecurity awareness.

Features:
---------
- Loads all major OSINT modules (Google Dorking, Deep Web, IP Tracking, Metadata, etc.)
- Verifies internet connection and required Python dependencies
- Displays ASCII branding and developer attribution
- Prompts the user to accept legal terms via disclaimer before proceeding
- Handles graceful fallback for missing packages with auto-install
- Offers interactive CLI menu to select tools with themed icons and animations
- Repeats execution loop until user exits
- New feature! now you can see the results of any tools with markdown!
more easier to read and understand!

Tools Available:
----------------
1. Track your current IP
2. Search information of any IP
3. Whois and metadata about a domain/website
4. Trace phone numbers with location and format data
5. Lookup coordinates or places via geocoding
6. Find user profiles across social media and platforms
7. Extract and analyze image metadata (Exif)
8. Use Google Dorking with smart OSINT dorks
9. Perform Tor-based Deep Web or Onion search
10. Exit program

Safety & Ethics:
----------------
- Includes conditions/disclaimer file (`READ_CONDITIONS.txt`) to ensure responsible use
- Logs and displays clear usage messages for transparency
- Optional Tor support available in tools that require anonymity

Requirements:
-------------
- Internet access (tested on Unix-like systems with Python 3.8+)
- Required packages: requests, whois, phonenumbers, googlesearch, exif, bs4, geopy
- All dependencies are auto-installed if missing (via `requirements.txt`)

Author:
-------
Developed by: l-craft-l
GitHub: https://github.com/l-craft-l
Repository: https://github.com/l-craft-l/SpyNexus

Usage:
------
Run this file directly via terminal or Python interpreter:
    python SpyNexus.py

Note:
-----
Do not use SpyNexus against systems without explicit permission.
The creator is not responsible for any misuse or illegal activity.
"""

import os

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
from core.ma_command import launch
from core.ma_command import check_internet

try:
    import requests
    import whois
    import phonenumbers
    from googlesearch import search
    from exif import Image
    from bs4 import BeautifulSoup
    from geopy.geocoders import Nominatim

except ModuleNotFoundError as pkg:
    write_effect(f"{display_question} Missing packages {maBold(pkg)}...\n{display_info} Trying to install the missing packages automatically...", 0.05)
    space_between()
    print()

    try:
        launch("pip install -r requirements.txt")
    except Exception as err:
        write_effect(err, 0.03)
        exit()

    space_between()
    write_effect(f"\n{display_validate} {maGreen('Successfully downloaded the missing packages!')} {maGreen(pointing)}\n{display_info} Run the script again!", 0.05)
    exit()


from tools.g_dorking import make_search, available_commands
from tools.deep_search import ex_deep
from tools.ip_search import search_ip
from tools.data_web import execute_webtool
from tools.user_search import execute_user
from tools.coordinates import get_location
from tools.metadata_img import execute_img
from tools.track_phone import execute_ph
from core.save_data import save_data
from core.agents import agents
from core.icons import show_icon

conditions = "READ_CONDITIONS.txt"

conditions_content = """
**Disclaimer Notice**

This software has been developed **for educational purposes only** and to promote awareness about cybersecurity.

Its intended use is **exclusively for learning, research, and testing** on systems where the user has **explicit authorization** to perform security analysis.

**The creator of this program assumes no responsibility for any misuse.**

Using this software on systems **without proper authorization is illegal** and may lead to **civil or criminal penalties**, depending on the laws of your jurisdiction.

By using this program, you agree that **you are solely responsible** for your actions, and the creator shall **not be held liable for any damage, loss, or consequences** arising from the use of this software.

⚠️ Please use it **ethically**, always respecting applicable laws and the privacy of others.
"""

print('Authentic MAM')

SpyNexus = """
             _____             _   __
            / ___/____  __  __/ | / /__  _  ____  _______
            \\__ \\/ __ \\/ / / /  |/ / _ \\| |/_/ / / / ___/
           ___/ / /_/ / /_/ / /|  /  __/>  </ /_/ (__  )
          /____/ .___/\\__, /_/ |_/\\___/_/|_|\\__,_/____/
              /_/    /____/
"""

icon = """                               +@+ @@@@@@@@@@@- +@<
                                -  {@@@@@@@@<  ]@@{ @
                              {     @@@@@@]   {@@@@ ]
                             {      @@@@@    @@@@@@ <
                            ]   -+<<+-<<   -@@@@@@@ +
                           {<<       {     @@@@@@@@ <
                        +                @@@@@@@@@] @]-
                      @               < <@@@@@@@@@-{@@@ @
                    ]                  -+{@@@@@@]<@@@@{-{
                   <                      +]@@@@@@@@@@@+<
                  @                        ]]<{@@@@@@@@] @
                 -    --+ -+<]]]]]+ -  ]<]@@{@@@@@@@@@@ @
                 {  +]@@@@@@@@@@@@@@@@-]@@{- ]@@@@@@@@@@ @
                  {@@@@@@@{@{{@@@@@@@+]-  + @@@@@@@@@@@ @
                  ]@@@{{{{]]]]{@@@@@@     -+@@@@@@@@@@{ @
                 ]+]{@@@@@@@@@@@@@@@@      @@@@@@@@@@@<+
                 <]{{{@@@{{{{{{{{{@@+-    <@@@@@@@@@@{-]
                 +@]]<<]{{@@@@@@@@<-     <@@@@@@@@@@@]-
               {- +<]@@@@@@@@@]<-      -]@@@@@@@@@@@{ {
              @       -+-{@< +-        <@@@@@@@@@@@<-{
            <        -               -<@@@@@@@@{]+{@]{
          ]- -<                       {@@@@@@@{{@@@@@< +-+
         ]{@@<                      +@@@@@@@@@@@@< <@@@<]
          {@<                      +{@@@@@@@@{+ <@@@@@@+<
           {            +]+    ]{@@@@@@@@@- <@@@@@@@@@{-
             {       ++    <@@@@@@@@@@@<  {@@@@@@@@@@{<+
               {-       ]@@@@@@@@@@@{  +@@@@<]]@@@@@{@@{-{
                 {   ]@@@@@<@@@@@@+   <@@{    @@@]@@@@@@@]-
               ]]@@@@@{-    +]{    <@]]] -+{@@@@@@{<{@@@@@@
            +{@@@@@@       -     @<]@{-     -  ]@@@{-{@@@@@
             <-@@@@@@{-@+-        +<]@@@@@<     +   <{@@]+@@
            <-- +-]@@{+@@@@<     <<@@{  - -{+    <]]]{@@@@<<@
             ] <@@{+@@@@@@] < @@@-    -   ]<@] -]{@@@@@@@<@@@
             <{@@-@@@@@@@@{@@]         --        ]@@@@@@{@@@@
            +<@@+@@@@@@@@@@+         +        -]@@@@@@@<{@@@@
         {- <@@@<{@@@@@{  -        --       ]@@@@@{@@@@@@-]@@@
        <@@@@{]{@{+@+        +  --     -{@@@<   {@@@@@@@-{@
        ]@@@+-{+ ]         ]   <     {@{      ]@@@@@@@@<<@@@@
        ]@@] -  -         <   -  ]+ -      +{@@@@@@@@@@{-@@@@@
       {              <{  -  @{      <{@<   +@@@@@@@@+@@@@@@@

"""

def show_main():
    launch("clear")
    prRed(SpyNexus)
    prRed(icon)
    print(f"{backRed('THE NETWORK OF ESPIONAGE AND INFORMATION ANALYSIS')}: {maGreen('SpyNexus')}")
    print(f'\nCreated and Developed by: {maGreen("l-craft-l")}\n{maBold("GitHub")}: {maUnderline("https://github.com/l-craft-l")}\n{maBold("Repository")}: {maUnderline("https://github.com/l-craft-l/SpyNexus")}')

def make_conditions():
    if not os.path.exists(conditions):
        write_effect(maYellow(conditions_content), 0.005)

        accept_cond = str(input(f"\n{display_extra} With this said you accept the terms? ({maGreen('y')}/{maRed('n')}): "))
        if check_key(accept_cond):
            with open(conditions, 'w') as archive:
                archive.write(conditions_content)
            show_main()
        else: exit()

launch("clear")
write_effect(maRed(SpyNexus), 0.005)
write_effect(maRed(icon), 0.0005)
write_effect(f'{backRed("THE NETWORK OF ESPIONAGE AND INFORMATION ANALYSIS")}: {maGreen("SpyNexus")}', 0.05)

print(f'\nCreated and Developed by: {maGreen("l-craft-l")}\n{maBold("GitHub")}: {maUnderline("https://github.com/l-craft-l")}\n{maBold("Repository")}: {maUnderline("https://github.com/l-craft-l/SpyNexus")}')

def cont_spy():
    option = str(input(f"\n{display_question} Do you want to continue? ({maGreen('y')}/{maRed('n')}): "))
    if check_key(option): show_main()
    else:
        write_effect(f"\nThanks for using SpyNexus, be a good puppy {maGreen(pointing)}\n", 0.03)
        exit()

def main():
    try:
        make_conditions()

        while True:
            all_commands = [
                'Track my IP',
                'Search IP',
                'Get info from a Website',
                'Track phone number',
                'Search coordinates/place',
                'Search user',
                'Extract metadata from image',
                'Google Dorking',
                'Deep Search (deep/dark web)',
                'Exit'
            ]

            print()
            for i, txt in enumerate(all_commands, start=1):
                write_effect(f"{maRed('[')}{maBold(i)}{maRed(']')}: {maRed(txt)}", 0.005)

            try:
                elec = int(input(f'\n×××{maRed("[")}{maBold("NEXUS")}{maRed("]")}---> '))

                if elec == 1:
                    wait_out(2)
                    from core.socks_connect import get_tor_connection
                    select_agent = agents()
                    try:
                        ses = get_tor_connection()
                        response = ses.get('https://api.ipify.org?format=json', headers=select_agent)
                    except Exception:
                        response = requests.get('https://api.ipify.org?format=json', headers=select_agent)

                    if response.status_code == 200:
                        final_ip = response.json().get("ip")
                        write_effect(f'\n{display_info} Your actual IP Address is: {maGreen(final_ip)}', 0.02)
                        print()
                        search_ip(final_ip)
                    cont_spy()


                elif elec == 2:
                    show_icon("icons/tl_ip", maBlue, maTeal)

                    print(f"{display_info} Enter a IP Address like: 127.0.0.1")

                    ip_address = input(f'\n×××{maRed("[")}{maBold("SPY-IP")}{maRed("]")}---> ').strip()
                    if not ip_address: raise Exception(f"{display_error} You can't leave the IP Address empty!")

                    wait_out(0.5)
                    print()
                    search_ip(ip_address)
                    cont_spy()

                elif elec == 3:
                    if not check_internet(): raise Exception(f"{display_error} Error, connection neeeded for this module...")
                    show_icon("icons/tl_wb", maBlue, maTeal)

                    execute_webtool()
                    cont_spy()

                elif elec == 4:
                    show_icon("icons/tl_ph", maBlue, maTeal)

                    execute_ph()
                    cont_spy()

                elif elec == 5:
                    if not check_internet(): continue
                    show_icon("icons/tl_loc", maSkyBlue, maBlue)

                    ls_loc = [
                        "Search coordinates (latitude, longitude)",
                        "Search place (example: Washington)"
                    ]
                    print()
                    for i, item in enumerate(ls_loc, start=1):
                        write_effect(f"{maRed('[')}{maBold(i)}{maRed(']')}: {maRed(item)}", 0.003)

                    ch_loc = int(input(f"\n×××{maRed('[')}{maBold('SELECT-OPTION')}{maRed(']')}---> "))

                    if ch_loc == 1:
                        lat_inp = float(input(f'\n×××{maRed("[")}{maBold("SPY-LATITUDE")}{maRed("]")}---> '))
                        lng_inp = float(input(f'×××{maRed("[")}{maBold("SPY-LONGITUDE")}{maRed("]")}---> '))
                        wait_out(0.5)
                        get_location(lat_inp, lng_inp, None)

                    elif ch_loc == 2:
                        place = input(f"\n×××{maRed('[')}{maBold('PLACE')}{maRed(']')}---> ").strip()
                        if not place: raise Exception(f"{display_error} Error, the place can't be empty!")

                        wait_out(0.5)
                        get_location(place, None, None)

                    else: raise Exception(f"{display_error} Error, select a valid option!")
                    cont_spy()

                elif elec == 6:
                    if not check_internet(): continue
                    show_icon("icons/tl_us", maRed, maRed)

                    execute_user()
                    cont_spy()

                elif elec == 7:
                    show_icon("icons/tl_img", maSkyBlue, maLightBlue)

                    execute_img()
                    cont_spy()

                elif elec == 8:
                    if not check_internet(): continue
                    show_icon("icons/tl_gk", maOrange, maLightYellow)

                    available_commands()
                    cont_spy()

                elif elec == 9:
                    if not check_internet(): continue
                    show_icon("icons/tl_ds", maMagenta, maPink)

                    ex_deep()
                    cont_spy()

                elif elec == 10:
                    write_effect(f'\nSee you later, be a good puppy {maGreen(pointing)}\n', 0.05)
                    break

                else:
                    write_effect(f'\n{display_error} {maRed("Please enter a valid option")} {maRed(angry)}', 0.02)
                    cont_spy()

            except ValueError:
                write_effect(f'\n{display_error} {maRed("Invalid operation, try again...")}', 0.03)
                cont_spy()

            except Exception as err:
                write_effect(err, 0.02)
                cont_spy()

    except Exception as err:
        write_effect(f'\n{display_error} {maRed(str(err))}', 0.02)
        exit()


if __name__ == "__main__":
    main()
