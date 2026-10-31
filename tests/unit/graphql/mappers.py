from app.graphql.mappers import country_to_type


def test_country_to_type_maps_document(sample_country, country_id):
    result = country_to_type(sample_country)

    assert result.id == country_id
    assert result.code == "IN"
    assert result.name.common == "India"
    assert result.population == 100
    assert result.coordinates.latitude == 20.0
    assert result.currencies[0].code == "INR"
    assert result.languages[0].nativeName == "हिन्दी"


def test_country_to_type_normalizes_single_currency_dict(sample_country):
    document = {
        "_id": sample_country["_id"],
        "code": "IN",
        "name": {"common": "India", "official": "Republic of India"},
        "currencies": {"code": "INR", "name": "Rupee"},
        "languages": [],
        "capital": "Delhi",
        "population": 1,
    }
    result = country_to_type(document)

    assert len(result.currencies) == 1
    assert result.capital == ["Delhi"]
