"""
This module extracts and analyzes metadata (EXIF) from image files, including camera details,
GPS coordinates, capture time, and other embedded attributes.

Features:
- Extracts device, lens, location, and camera information
- Converts GPS coordinates into decimal format and maps them
- Detects orientation, lighting, classification, and technical data
- Saves formatted metadata into a structured Markdown file
- Displays metadata interactively in the terminal

Main Function:
    - execute_img(): Interactively analyzes metadata from a specified image file

Helper Functions:
    - directions_degrees(): Converts image direction (degrees) into cardinal direction (e.g., NW)
    - conver_num(): Converts numeric EXIF codes to human-readable form
    - dcm_coordinates(): Converts GPS DMS format into decimal degrees
    - direction_ref(): Decodes magnetic/true north direction reference
    - sea_level(): Describes altitude reference above or below sea level
    - velocity_photo(): Converts velocity reference to readable unit (KM/H, MPH)

Requirements:
    - `exif` module (https://pypi.org/project/exif/)
    - Images must contain EXIF metadata (usually JPEG/JPG, TIFF)
    - Works best when GPS tags are embedded

Saved Output:
    - File path: data/image_metadata/results_<filename>_file.md
    - Includes raw tags, device info, coordinates, and environmental conditions
"""

import os
from exif import Image
from tools.coordinates import get_location
from tools.g_dorking import multi_search, gg_connection
from core.save_data import save_data
from core.ma_command import check_internet
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

no_info = "Unknown"
users = []
global amount
amount = 0

def directions_degrees(deg):
    if deg == no_info:
        return 'No exists'

    compass = [
        'N',
        'NNE',
        'NE',
        'ENE',
        'E',
        'ESE',
        'SE',
        'SSE',
        'S',
        'SSW',
        'SW',
        'WSW',
        'W',
        'WNW',
        'NW',
        'NNW'
    ]

    compass_count = len(compass)
    compass_dir = 360 / compass_count
    return compass[int(deg / compass_dir) % compass_count]

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

    value = change_list.get(num, no_info)

    if num in list_num:
        write_effect(f'{display_extra} {maYellow(value)}\n', 0.005)

def dcm_coordinates(coor, coor_ref):
    if not coor or not isinstance(coor, (list, tuple)) or len(coor) != 3:
        return no_info

    try:
        dcmcoo = coor[0] + coor[1] / 60 + coor[2] / 3600

        if coor_ref in ('S', 'W'):
            dcmcoo = -dcmcoo

        return dcmcoo
    except Exception:
        return no_info


def direction_ref(ref):
    dir_text = '(value not specified)'
    if ref == 'T':
        dir_text = 'Dir North'
    elif ref == 'M':
        dir_text = 'Mag North'
    return dir_text

def sea_level(lat, lat_ref):
    text_sea = '(Sea level unknown)'
    if lat == no_info:
        return text_sea

    if lat_ref == 0:
        text_sea = 'Above the sea level'
    elif lat_ref == 1:
        text_sea = 'Under the sea level'
    return f'{lat} meters {text_sea}'

def velocity_photo(vel_ref):
    vel_text = '(Value not specified)'
    if vel_ref == 'M':
        vel_text = 'MPH'
    elif vel_ref == 'K':
        vel_text = 'KM/H'
    return vel_text

def execute_img():
    print(f"{display_info} Enter the directory of the image like: images/example_image.png")

    media_photo = input(f'\n×××{maRed("[")}{maBold("SPY-PHOTO")}{maRed("]")}---> ').strip()
    if not os.path.exists(media_photo): raise Exception(f"{display_error} The rute is not valid OR does not exists.")
    fl = input(f"×××{maRed('[')}{maBold('FILE')}{maRed(']')}---> ").strip()
    if not fl: raise Exception(f"{display_error} Error, you can't leave the name file empty!")

    file = f"data/image_metadata/results_{fl}_file.md"

    wait_out(0.5)
    write_effect(maYellow("Extracting metadata..."), 0.05)

    image = Image(media_photo)
    got_location = True
    save_data(file, f"## <center> Results of image: {media_photo}</center>", None, "a", False)

    def print_tags(tag, info):
        data = image.get(info, no_info)

        if data != no_info:
            #amount += 1
            write_effect(f'{display_info} {maGreen(tag)}: {maUnderline(data)}', 0.005)
            meta_save = f'- {tag}: **{data}**'
            save_data(file, None, meta_save, 'a', False)
            return data

    def extract_us(data):
        var = image.get(data, no_info)
        if var != no_info: users.append(var)

    enabled_gps = image.get('gps_latitude', no_info)
    if enabled_gps == no_info:
        got_location = False

    lat_dcm = dcm_coordinates(image.get("gps_latitude", no_info), image.get("gps_latitude_ref", no_info))
    lng_dcm = dcm_coordinates(image.get("gps_longitude", no_info), image.get("gps_longitude_ref", no_info))


    between_tag("INFO DEVICE")
    save_data(file, "---\n### 🎥 Info Device", None, "a", False)
    print_tags("Make", "make")
    print_tags("Model", "model")
    print_tags("Software", "software")

    space_between()

    between_tag("INFO IMAGE")
    save_data(file, "---\n### 🖼️ Info Image", None, "a", False)
    print_tags("Image Width", "Image_Width")
    print_tags("Image Height", "Image_Height")
    print_tags("Width Resolution", "X_Resolution")
    print_tags("Vertical Resolution", "Y_Resolution")
    print_tags("Image Size", "Sony_Raw_Image_Size")

    change_value = {
        2: "Inches",
        3: "Centimeters"
    }

    units_re = print_tags("Unit of Distance", "Resolution_Unit")

    conver_num(units_re, change_value)


    print_tags("Profile", "Profile_Name")
    print_tags("Owner", "Owner_Name")
    print_tags("Copyright", "Copyright")
    print_tags("Artist", "Artist")
    print_tags("Photographer", "Photographer")

    extract_us("Profile_Name")
    extract_us("Copyright")
    extract_us("Artist")
    extract_us("Photographer")

    print_tags("Shared Data", "Shared_Data")
    print_tags("Description", "Image_Description")
    print_tags("Comment", "User_Comment")
    print_tags("Document", "document_name")

    change_value = {
        1: 'Horizontal',
        2: 'Mirror Horizontal',
        3: 'Rotated 180°',
        4: 'Mirror Vertical',
        5: 'Mirror Horizontal & Rotated 270° CW',
        6: 'Rotated 90° CW',
        7: 'Mirror Horizontal & Rotated 90° CW',
        8: 'Rotated 270° CW'
    }
    orientation = print_tags("Orientacion", "Orientation")
    conver_num(orientation, change_value)


    print_tags("Exposure", "Exposure")
    print_tags("Exposure Mode", "Exposure_Mode")
    print_tags("Exposure Time", "exposure_time")
    print_tags("Iso", "ISO")
    print_tags("Aperture", "aperture_value")
    print_tags("Focal Lenght", "focal_lenght")
    print_tags("Pixel Scale", "pixel_scale")
    print_tags("Shadows", "Shadows")
    print_tags("Brightness", "brightness_value")

    change_value = {
        0: 'Normal',
        1: 'Low',
        2: 'High'
    }
    contrast = print_tags("Contrast", "Contrast")
    conver_num(contrast, change_value)
    saturation = print_tags("Saturation", "Saturation")
    conver_num(saturation, change_value)


    print_tags("Smoothness", "Smoothness")
    print_tags("Clasification", "Security_Classification")
    print_tags("History", "Image_History")
    print_tags("Field of View", "fov_cot")

    space_between()

    between_tag("INFO CAMERA")
    save_data(file, "---\n### 📷 Info Camera", None, "a", False)
    print_tags("Make", "lens_make")
    print_tags("Lens Model", "lens_model")
    print_tags("Specifications", "lens_specification")
    print_tags("Lens Info", "Lens_Info")

    space_between()

    between_tag("INFO TIME")
    save_data(file, "---\n### 🗓️ Info Date & Time", None, "a", False)
    print_tags("Date & Time", "datetime_original")
    print_tags("UTC", "offset_time")

    between_tag("INFO PLACE")
    save_data(file, "---\n### 📍 Info Place", None, "a", False)
    print_tags("Latitude", "gps_latitude")
    print_tags("Longitude", "gps_longitude")
    print(f'{display_info} {maGreen("Latitude Decimal")}: {maYellow(lat_dcm)}')
    print(f'{display_info} {maGreen("Longitude Decimal")}: {maYellow(lng_dcm)}\n')

    space_between()

    if got_location:
        if check_internet():
            get_location(lat_dcm, lng_dcm, file)
            space_between()
        else: save_data(file, "- ❌ Location not found", None, "a", False)
    else: save_data(file, "- ❌ Location not found", None, "a", False)

    between_tag("EXTRA INFO")
    save_data(file, "---\n### 📌 Extra Info", None, "a", False)
    dir_image = directions_degrees(image.get("gps_img_direction", no_info))
    write_effect(f'{display_info} {maGreen("Dir Image")}: {maUnderline(dir_image)}', 0.005)
    print_tags("Image Direction", "gps_img_direction")
    write_effect(f'{display_info} {maGreen("Sea Level")}: {maUnderline(sea_level(image.get("gps_altitude", no_info), image.get("gps_altitude_ref", no_info)))}', 0.005)
    write_effect(f'{display_info} {maGreen("Speed")}: {maUnderline(image.get("gps_speed", no_info))} {maUnderline(velocity_photo(image.get("gps_speed_ref", no_info)))}', 0.005)
    print_tags("Flash", "Flash")
    print_tags("Humidity", "Humidity")
    print_tags("Pressure", "Pressure")
    print_tags("Temperature Ambient", "temperature_ambient")
    print_tags("Battery Level", "Battery_Level")

    mess = f"""
\n---\n## 📊 Final Summary\n
- 📋 Total amount of data: **{amount}**
- 👤 Possible users found on the image: **{len(users)}**
    """
    if got_location: mess += "\n- 📍 Location found on the image: ✅"
    else: mess += "\n- 📍 Location found on the image: ❌"
    save_data(file, mess, None, "a", False)

    if not users: save_data(file, "- ❌ Possible users not found", None, "a", True)
    else:
        if check_internet():
            for user in users:
                write_effect(f"\n{display_info} User '{maBold(user)}' found on the image...", 0.02)
                conf = str(input(f"{display_question} Do you want to search the user '{maBold(user)}' using Google Dorks? ({maGreen('y')}/{maRed('n')}): ")).strip()

                if not check_key(conf): continue

                sel = str(input(f"{display_question} Do you want to use a Tor network for this module? ({maGreen('y')}/{maRed('n')}): ")).strip()
                tor = check_key(sel)
                if tor: gg_connection(True)

                ls_search_user = [
                    (f'a_descr="{user}"', 10),
                    (f'a_descr="{user}"&docs', 10),
                    (f'a_descr="{user}"&email', 10),
                    (f'a_descr="{user}"&phone', 10),
                    (f'a_descr="{user}"&adr', 10),
                    (f'a_descr="{user}"&dbase', 10),
                    (f'a_descr="{user}"&cv', 10),
                    (f'a_descr="{user}"&cv&docs', 10)
                ]

                save_data(file, f"---\n## <center>👤 Searching the user '{user}' using Google Dorks</center>", None, "a", False)
                multi_search(1, ls_search_user, file, tor)
        else: write_effect(f"{display_extra} Connection needed to search the users with Google Dorks...", 0.02)
