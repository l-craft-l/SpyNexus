"""
This module analyzes international phone numbers using the `phonenumbers` library and provides
detailed metadata including format validation, location approximation, carrier, and more.

Features:
- Detects phone number validity and type (mobile, landline, etc.)
- Displays multiple standardized formats (E.164, RFC3966, national, international)
- Identifies carrier and country information
- Approximates region and timezone
- Converts output to readable format and stores results in a file
- Offers optional Google Dorking search for the number (via Tor or Requests)

Main Function:
    - execute_ph(): Starts the phone number analysis process with user input.

Helper Functions:
    - conver_num(): Converts enum-like numeric results to human-readable text
    - get_data(): Internal handler to retrieve data using phonenumbers API with error handling

Output:
    - Data is saved in: `data/phones/results_<number>_file.txt`
    - Optionally initiates Google Dorking if user approves

Requirements:
    - `phonenumbers` library (https://pypi.org/project/phonenumbers/)
    - Internet access to resolve some carrier and region info
    - Optional Tor configuration if used with g_dorking

Warnings:
    - Region information can be approximate depending on number format and source
    - Numbers must be in valid international format (e.g., +1 23456789)
"""

import phonenumbers
from phonenumbers import (
    timezone, carrier, geocoder, is_alpha_number,
    format_out_of_country_calling_number,
    format_out_of_country_keeping_alpha_chars
)
from core.save_data import save_data
from tools.coordinates import get_location
from tools.g_dorking import multi_search, gg_connection
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

def conver_num(num, message=None):
    n_a = 'N/A'
    list_num = {
       0: n_a,
       1: n_a,
       2: n_a,
       3: n_a,
       4: n_a,
       5: n_a,
       6: n_a,
       7: n_a,
       8: n_a,
       9: n_a,
       10: n_a,
       99: n_a
    }
    change_list = message if message else list_num
    value = change_list.get(num, "Unknown")

    if num in list_num:
        write_effect(f'{display_extra} {maSkyBlue(value)}\n', 0.005)

def execute_ph():
    print(f"{display_info} Enter a number with his international format... example: +1 23456789")

    phone_number = input(f'\n×××{maRed("[")}{maBold("SPY-PHONE")}{maRed("]")}---> ')

    exist = phonenumbers.parse(phone_number, None)

    possible_numb = phonenumbers.is_possible_number(exist)
    valid_numb = phonenumbers.is_valid_number(exist)

    if not valid_numb or not possible_numb:
        raise Exception(f"{display_error} Error, the number is not valid OR not exists!")

    e_format = phonenumbers.format_number(exist, phonenumbers.PhoneNumberFormat.E164)
    file = f"data/phones/results_{e_format}_file.txt"
    save_data(file, f"\nResults of phone number: {exist}\n", None, "a", False)

    def get_data(cmd, tag, lg):
        try:
            global data
            if not lg or lg == None:
                data = cmd(exist)
                write_effect(f"{display_info} {maBold(tag)}: {maGreen(data)}", 0.005)
            else:
                data = cmd(exist, lg)
                write_effect(f"{display_info} {maBold(tag)}: {maGreen(data)}", 0.005)
            fn_data = f"{tag}: {data}"
            save_data(file, None, fn_data, "a", False)
            return data
        except Exception as err:
            write_effect(f"{display_error} Another error has occured, {maRed(err)}", 0.02)

    wait_out(0.3)
    confirm_num = f'\n{display_validate} {maGreen("Number found...")}\n{maGreen("Getting data...")} {maGreen(happy)}\n'
    write_effect(confirm_num, 0.05)

    between_tag("PHONE NUMBER FORMATS")

    global_numb = phonenumbers.format_number(exist, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    natal_numb = phonenumbers.format_number(exist, phonenumbers.PhoneNumberFormat.NATIONAL)

    write_effect(f"{display_info} {maBold('International Format')}: {maGreen(global_numb)}", 0.005)
    write_effect(f"{display_info} {maBold('National Format')}: {maGreen(natal_numb)}", 0.005)
    write_effect(f"{display_info} {maBold('E.164 Format')}: {maGreen(e_format)}", 0.005)
    write_effect(f"{display_info} {maBold('RFC3966 Format')}: {maGreen(phonenumbers.format_number(exist, phonenumbers.PhoneNumberFormat.RFC3966))}", 0.005)

    space_between()

    between_tag("PHONE NUMBER ANALYSIS")

    types = {
        0: "Fixed Line",
        1: "Mobile",
        2: "Fixed Line or Mobile",
        3: "Toll Free",
        4: "Premium Rate",
        5: "Shared Cost",
        6: "VOIP",
        7: "Personal Number",
        8: "Pager",
        9: "UAN",
        10: "VoiceMail",
    }

    get_data(phonenumbers.truncate_too_long_number, "Truncate", None)
    tp = get_data(phonenumbers.number_type, "Number Type", None)
    conver_num(tp, types)
    get_data(carrier.name_for_number, "Carrier", "en")

    space_between()

    between_tag("MOBILE DIALING")

    get_data(format_out_of_country_calling_number, "In Another Country (US)", "us")
    get_data(format_out_of_country_keeping_alpha_chars, "In Another Country With Letters (US)", "us")

    space_between()

    between_tag("PHONE NUMBER LOCATION")

    get_data(geocoder.country_name_for_number, "Country", "en")
    get_data(phonenumbers.region_code_for_number, "Country Code", None)
    get_data(geocoder.description_for_number, "Region", "en")
    get_data(timezone.time_zones_for_number, "Timezone", None)

    space_between()
    write_effect(f"{display_question} {maYellow('Warning')}: The location of the phone number can be approximate.", 0.05)
    region = geocoder.description_for_number(exist, "en")
    get_location(str(region), None, file)

    space_between()
    ask_ggdork = str(input(f"{display_question} Do you want to search this '{maBold(phone_number)}' phone number in Google? ({maGreen('y')}/{maRed('n')}): "))

    if check_key(ask_ggdork):
        sel = str(input(f"{display_question} Do you want to use a Tor network for this module? ({maGreen('y')}/{maRed('n')}): ")).strip()
        tor = check_key(sel)
        if tor: gg_connection(True)

        wait_out(0.5)
        write_effect(maYellow("\nSearching with the international number..."), 0.05)

        search_phone_int = [
            (f'a_descr="{global_numb}"', 10, 3),
            (f'a_descr="{global_numb}"&docs', 10, 3),
            (f'a_descr="{global_numb}"&dbase', 10, 3)
        ]

        multi_search(1, search_phone_int, file, tor)
        space_between()
        write_effect(maYellow("\nSearching with the national number..."), 0.05)

        search_phone_nt = [
            (f'a_descr="{natal_numb}"', 10, 3),
            (f'a_descr="{natal_numb}"&docs', 10, 3),
            (f'a_descr="{natal_numb}"&dbase', 10, 3)
        ]

        multi_search(1, search_phone_nt, file, tor)
