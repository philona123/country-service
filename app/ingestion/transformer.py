from datetime import datetime, timezone

from app.models.country import normalize_capital_list


def transform_country(data: dict) -> dict:

    latlng = data.get("latlng") or []

    latitude = None
    longitude = None

    if len(latlng) >= 2:
        latitude = float(latlng[0])
        longitude = float(latlng[1])

    location = None

    if latitude is not None and longitude is not None:
        location = {
            "type": "Point",
            "coordinates": [
                longitude,
                latitude
            ]
        }

    return {
        "code": data["alpha2Code"].upper(),

        "name": {
            "common": data["name"],
            "official": data.get("officialName", data["name"]),
            "native": data.get("nativeName")
        },

        "alpha3Code": data.get("alpha3Code"),

        "numericCode": data.get("numericCode"),

        "capital": normalize_capital_list(data.get("capital")),

        "region": data.get("region"),
        "subregion": data.get("subregion"),

        "population": data.get("population", 0),
        "area": data.get("area"),

        "coordinates": (
            {
                "latitude": latitude,
                "longitude": longitude
            }
            if location else None
        ),

        "location": location,

        "currencies": data.get("currencies") or [],
        "languages": data.get("languages") or [],

        "timezones": data.get("timezones") or [],
        "borders": data.get("borders") or [],
        "callingCodes": data.get("callingCodes") or [],

        "topLevelDomains": data.get("topLevelDomain") or [],

        "flag": {
            "emoji": data.get("flag"),
            "svg": (data.get("flags") or {}).get("svg"),
            "png": (data.get("flags") or {}).get("png")
        },

        "source": {
            "provider": "apicountries",
            "lastSyncedAt": datetime.now(timezone.utc)
        },

        "updatedAt": datetime.now(timezone.utc)
    }