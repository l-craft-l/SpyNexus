"""
This module performs an IP address lookup using the ipapi.co API. It retrieves
details such as geolocation, timezone, organization, language, and more.
It also integrates with Google Dorking to perform OSINT searches based on the IP.

Features:
- Retrieves location and ISP data from an IP address
- Saves information into a file
- Optionally maps coordinates and performs Google Dork searches
- Supports Tor-based connections for anonymity
"""

from core.save_data import save_data
from requests import get
import requests
from tools.g_dorking import multi_search, gg_connection
from tools.coordinates import get_location
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

def search_ip(address):
    """
    Searches public information about a given IP address using ipapi.co.

    Retrieves:
    - Geolocation: Country, Region, City, Latitude, Longitude
    - Metadata: Timezone, Organization, Hostname, Postal Code
    - Optional Google Dorking and coordinate mapping

    Parameters:
        address (str): The IP address to investigate.
    """

    select_agent = agents()

    try:
        ip_info = get(f'https://ipapi.co/{address}/json/', headers=select_agent, timeout=10)
    except requests.exceptions.ConnectionError:
        raise Exception(f"{display_error} Error, can't connect to the page, try again later...")
    except requests.exceptions.RequestException as err:
        raise Exception(f"{display_error} Another error has ocurred, {maRed(err)}")
    location = f'data/ip_address/info_{address}_ip.txt'

    if ip_info.status_code == 200:
        data = ip_info.json()
        save_data(location, f'\nIP Address Searched: {address}\n', None, 'a', False)

        location_info = {
            'IP': address,
            'Country': data.get('country'),
            'Region': data.get('region'),
            'City': data.get('city'),
            'Latitude': data.get('latitude'),
            'Longitude': data.get('longitude'),
            'Timezone': data.get('timezone'),
            'Country Calling Code': data.get('country_calling_code'),
            'Currency': data.get('currency'),
            'Language/s': data.get('languages'),
            'Postal': data.get('postal'),
            'Org': data.get('org'),
            'Hostname': data.get('hostname')
        }
        for info, data in location_info.items():
            write_effect(f'{display_info} {maBold(info)}: {maGreen(data)}', 0.005)
            save_ip = f'{info}: {data}'
            save_data(location, None, save_ip, 'a', False)

        lat = location_info.get("Latitude")
        lng = location_info.get("Longitude")

        between_tag("INFO COORDINATES")
        get_location(lat, lng, location)

        conf = input(f"\n{display_question} You want to search this {maBold(address)} IP address in google? ({maGreen('y')}/{maRed('n')}): ")
        if check_key(conf):
            sel = str(input(f"{display_question} Do you want to use a Tor network for this module? ({maGreen('y')}/{maRed('n')}): ")).strip()
            tor = check_key(sel)
            if tor: gg_connection(True)

            save_data(location, f"\nResults of {address} IP Address:\n", None, 'a', False)

            ls_ip_addr = [
                (f'descr="{address}"', 10, 3),
                (f'descr="{address}"&breach', 10, 3),
                (f'descr="{address}"&dbase', 10, 3),
                (f'rel="{address}"', 10, 3)
            ]

            multi_search(1, ls_ip_addr, location, tor)
    else: raise Exception(f"{display_error} Error, can't search the ip address... status code: {maRed(ip_info.status_code)}")
