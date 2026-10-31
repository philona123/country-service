from app.ingestion.transformer import transform_country


def test_transform_country_maps_core_fields():
    raw = {
        "alpha2Code": "in",
        "name": "India",
        "officialName": "Republic of India",
        "nativeName": "भारत",
        "alpha3Code": "IND",
        "capital": "New Delhi",
        "region": "Asia",
        "population": 100,
    }

    document = transform_country(raw)

    assert document["code"] == "IN"
    assert document["name"]["common"] == "India"
    assert document["name"]["official"] == "Republic of India"
    assert document["name"]["native"] == "भारत"
    assert document["capital"] == ["New Delhi"]
    assert document["population"] == 100
    assert document["coordinates"] is None
    assert document["location"] is None
    assert document["source"]["provider"] == "apicountries"


def test_transform_country_builds_geo_from_latlng():
    raw = {
        "alpha2Code": "IN",
        "name": "India",
        "latlng": [20.0, 77.0],
    }

    document = transform_country(raw)

    assert document["coordinates"] == {"latitude": 20.0, "longitude": 77.0}
    assert document["location"] == {
        "type": "Point",
        "coordinates": [77.0, 20.0],
    }
