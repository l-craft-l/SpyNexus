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
from geopy.geocoders import Nominatim

def get_location(lat, lng, file):
    if not check_internet(): raise Exception(f"{display_error} Error, connection needed for this module...")
    geocode = Nominatim(user_agent="stfu")

    if isinstance(lat, str):
        lat = lat.strip()
        global place
        place = geocode.geocode(lat)
        lat = place.latitude
        lng = place.longitude
    else: place = False

    final = f"{lat}, {lng}"

    get_data = geocode.reverse(final)

    if not get_data:
        write_effect(f"{display_question} No data found in the coordinates...", 0.03)
    else:
        other_data = get_data.raw
        location = get_data.raw.get("address", {})
        if not file:
            file = f"data/coordinates/results_{lat}-{lng}_file.md"
            if place: save_data(file, f"## <center>🌎 Location from the place {place}</center>", None, "a", False)
            else: save_data(file, f"## <center>📍 Location from the coordinates {final}</center>", None, "a", False)

        def display_data(tag, list, dt):
            data = list.get(dt, "Unknown")

            if data != "Unknown":
                write_effect(f"{display_info} {maBold(tag)}: {maGreen(data)}", 0.005)
                sv_info = f'{tag}: {data}\n'
                save_data(file, None, sv_info, "a", False)
            else:
                write_effect(f"{display_question} {maBold(tag)}: {maYellow(data)}", 0.005)

        if not place: save_data(file, f"## ℹ️ Results coordinates: {final}\n", None, "a", False)

        print()
        display_data("🌐 Latitude", other_data, "lat")
        display_data("🌐 Longitude", other_data, "lon")
        display_data("🆔 Place ID", other_data, "place_id")
        display_data("▶️ Class", other_data, "class")
        display_data("🌎 Type", other_data, "type")
        display_data("❗ Importance", other_data, "importance")
        space_between()
        display_data("🗺️ Country", location, "country")
        display_data("🆔 Country Code", location, "country_code")
        display_data("🗾 State", location, "state")
        display_data("🆔 Post Code", location, "postcode")
        display_data("🏙️ City", location, "city")
        display_data("🌉 Suburb", location, "suburb")
        display_data("🏘️ Neighbourhood", location, "neighbourhood")
        display_data("🛣️ Road", location, "road")
        display_data("🏠 House Number", location, "house_number")

        save_data(file, f"- 📍[Google Maps](https://www.google.com/maps/place/{lat}+{lng})", None, "a", True)
