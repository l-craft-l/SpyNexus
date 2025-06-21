"""
This module extracts and analyzes metadata (EXIF) from image files, including camera details,
GPS coordinates, capture time, and other embedded attributes.

Features:
- Extracts device, lens, location, and camera information
- Converts GPS coordinates into decimal format and maps them
- Detects orientation, lighting, classification, and technical data
- Saves formatted metadata into a structured TXT file
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
    - File path: data/image_metadata/results_<filename>_file.txt
    - Includes raw tags, device info, coordinates, and environmental conditions
"""

import os
from exif import Image
from tools.coordinates import get_location
from core.save_data import save_data
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

def directions_degrees(deg):
    if deg == 'Unknown':
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

    value = change_list.get(num, "Unknown")

    if num in list_num:
        write_effect(f'{display_extra} {maYellow(value)}\n', 0.005)

def dcm_coordinates(coor, coor_ref):
    if not coor or not isinstance(coor, (list, tuple)) or len(coor) != 3:
        return "Unknown"

    try:
        dcmcoo = coor[0] + coor[1] / 60 + coor[2] / 3600

        if coor_ref in ('S', 'W'):
            dcmcoo = -dcmcoo

        return dcmcoo
    except Exception:
        return "Unknown"


def direction_ref(ref):
    dir_text = '(value not specified)'
    if ref == 'T':
        dir_text = 'Dir North'
    elif ref == 'M':
        dir_text = 'Mag North'
    return dir_text

def sea_level(lat, lat_ref):
    text_sea = '(Sea level unknown)'
    if lat == 'Unknown':
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

    file = f"data/image_metadata/results_{fl}_file.txt"

    wait_out(0.5)
    write_effect(maYellow("Extracting metadata..."), 0.05)

    image = Image(media_photo)
    got_location = True
    save_data(file, f"\nResults of image: {media_photo}\n", None, "a", False)

    def print_tags(tag, info):
        data = image.get(info, "Unknown")

        if data != "Unknown":
            write_effect(f'{display_info} {maGreen(tag)}: {maUnderline(data)}', 0.005)
            meta_save = f'{tag}: {data}'
            save_data(file, None, meta_save, 'a', False)
            return data

    enabled_gps = image.get('gps_latitude', 'Unknown')
    if enabled_gps == 'Unknown':
        got_location = False

    lat_dcm = dcm_coordinates(image.get("gps_latitude", "Unknown"), image.get("gps_latitude_ref", "Unknown"))
    lng_dcm = dcm_coordinates(image.get("gps_longitude", "Unknown"), image.get("gps_longitude_ref", "Unknown"))


    between_tag("INFO DEVICE")
    print_tags("Make", "make")
    print_tags("Model", "model")
    print_tags("Software", "software")

    space_between()

    between_tag("INFO IMAGE")
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
    print_tags("Make", "lens_make")
    print_tags("Lens Model", "lens_model")
    print_tags("Specifications", "lens_specification")
    print_tags("Lens Info", "Lens_Info")

    space_between()

    between_tag("INFO TIME")
    print_tags("Date & Time", "datetime_original")
    print_tags("UTC", "offset_time")

    between_tag("INFO PLACE")
    print_tags("Latitude", "gps_latitude")
    print_tags("Longitude", "gps_longitude")
    print(f'{display_info} {maGreen("Latitude Decimal")}: {maYellow(lat_dcm)}')
    print(f'{display_info} {maGreen("Longitude Decimal")}: {maYellow(lng_dcm)}\n')

    space_between()

    if got_location:
        get_location(lat_dcm, lng_dcm, file)
        space_between()

    between_tag("EXTRA INFO")
    dir_image = directions_degrees(image.get("gps_img_direction", "Unknown"))
    write_effect(f'{display_info} {maGreen("Dir Image")}: {maUnderline(dir_image)}', 0.005)
    print_tags("Image Direction", "gps_img_direction")
    write_effect(f'{display_info} {maGreen("Sea Level")}: {maUnderline(sea_level(image.get("gps_altitude", "Unknown"), image.get("gps_altitude_ref", "Unknown")))}', 0.005)
    write_effect(f'{display_info} {maGreen("Speed")}: {maUnderline(image.get("gps_speed", "Unknown"))} {maUnderline(velocity_photo(image.get("gps_speed_ref", "Unknown")))}', 0.005)
    print_tags("Flash", "Flash")
    print_tags("Humidity", "Humidity")
    print_tags("Pressure", "Pressure")
    print_tags("Temperature Ambient", "temperature_ambient")
    print_tags("Battery Level", "Battery_Level")

    save_data(file, None, None, "a", True)
