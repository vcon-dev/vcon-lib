from vcon import Vcon
from vcon.civic_address import CivicAddress
import pytest

# Initialize CivicAddress with all parameters set to valid strings
def test_initialize_with_valid_strings() -> None:
    # Given
    valid_data = {
        "country": "US",
        "a1": "California",
        "a2": "Los Angeles County",
        "a3": "Los Angeles",
        "a4": "Downtown",
        "a5": "90001",
        "a6": "Building A",
        "prd": "Suite 100",
        "pod": "PO Box 123",
        "sts": "Main St",
        "hno": "1234",
        "hns": "House Name",
        "lmk": "Near Central Park",
        "loc": "Location Name",
        "flr": "5th Floor",
        "nam": "Office Name",
        "pc": "90001"
    }

    # When
    address = CivicAddress(**valid_data)
    
    # Then
    assert address.to_dict() == valid_data
    
# Initialize CivicAddress with all parameters set to None
def test_initialize_with_none():
    # Given
    none_data = {
        "country": None,
        "a1": None,
        "a2": None,
        "a3": None,
        "a4": None,
        "a5": None,
        "a6": None,
        "prd": None,
        "pod": None,
        "sts": None,
        "hno": None,
        "hns": None,
        "lmk": None,
        "loc": None,
        "flr": None,
        "nam": None,
        "pc": None
    }

    # When
    address = CivicAddress(**none_data)

    # Then
    assert address.to_dict() == {}

# Initialize CivicAddress with some parameters set to None
def test_initialize_with_some_parameters_set_to_none():
    # Given
    none_data = {
        "country": None,
        "a1": None,
        "a2": None,
        "a3": None,
        "a4": None,
        "a5": None,
        "a6": None,
        "prd": None,
        "pod": None,
        "sts": None,
        "hno": None,
        "hns": None,
        "lmk": None,
        "loc": None,
        "flr": None,
        "nam": None,
        "pc": None
    }

    # When
    address = CivicAddress(**none_data)

    # Then
    assert address.to_dict() == {}

# Convert a fully populated CivicAddress object to a dictionary
def test_convert_to_dict_with_valid_data():
    # Given
    valid_data = {
        "country": "US",
        "a1": "California",
        "a2": "Los Angeles County",
        "a3": "Los Angeles",
        "a4": "Downtown",
        "a5": "90001",
        "a6": "Building A",
        "prd": "Suite 100",
        "pod": "PO Box 123",
        "sts": "Main St",
        "hno": "1234",
        "hns": "House Name",
        "lmk": "Near Central Park",
        "loc": "Location Name",
        "flr": "5th Floor",
        "nam": "Office Name",
        "pc": "90001"
    }

    # When
    address = CivicAddress(**valid_data)

    # Then
    assert address.to_dict() == valid_data

# Convert a partially populated CivicAddress object to a dictionary
def test_convert_partially_populated_to_dict():
    # Given
    partial_data = {
        "country": "US",
        "a1": "California",
        "a2": "Los Angeles County",
        "a3": "Los Angeles",
        "a4": None,
        "a5": None,
        "a6": None,
        "prd": None,
        "pod": None,
        "sts": "Main St",
        "hno": "1234",
        "hns": None,
        "lmk": None,
        "loc": None,
        "flr": None,
        "nam": None,
        "pc": "90001"
    }

    # When
    address = CivicAddress(**partial_data)

    # Then
    assert address.to_dict() == {
        "country": "US",
        "a1": "California",
        "a2": "Los Angeles County",
        "a3": "Los Angeles",
        "sts": "Main St",
        "hno": "1234",
        "pc": "90001"
    }

# Ensure all attributes are correctly assigned during initialization
def test_initialize_with_valid_attributes():
    # Given
    valid_data = {
        "country": "US",
        "a1": "California",
        "a2": "Los Angeles County",
        "a3": "Los Angeles",
        "a4": "Downtown",
        "a5": "90001",
        "a6": "Building A",
        "prd": "Suite 100",
        "pod": "PO Box 123",
        "sts": "Main St",
        "hno": "1234",
        "hns": "House Name",
        "lmk": "Near Central Park",
        "loc": "Location Name",
        "flr": "5th Floor",
        "nam": "Office Name",
        "pc": "90001"
    }

    # When
    address = CivicAddress(**valid_data)

    # Then
    assert address.country == valid_data["country"]
    assert address.a1 == valid_data["a1"]
    assert address.a2 == valid_data["a2"]
    assert address.a3 == valid_data["a3"]
    assert address.a4 == valid_data["a4"]
    assert address.a5 == valid_data["a5"]
    assert address.a6 == valid_data["a6"]
    assert address.prd == valid_data["prd"]
    assert address.pod == valid_data["pod"]
    assert address.sts == valid_data["sts"]
    assert address.hno == valid_data["hno"]
    assert address.hns == valid_data["hns"]
    assert address.lmk == valid_data["lmk"]
    assert address.loc == valid_data["loc"]
    assert address.flr == valid_data["flr"]
    assert address.nam == valid_data["nam"]
    assert address.pc == valid_data["pc"]

# Convert a CivicAddress object with all attributes set to None to a dictionary
def test_convert_all_attributes_none_to_dict():
    # Given
    empty_data = {
        "country": None,
        "a1": None,
        "a2": None,
        "a3": None,
        "a4": None,
        "a5": None,
        "a6": None,
        "prd": None,
        "pod": None,
        "sts": None,
        "hno": None,
        "hns": None,
        "lmk": None,
        "loc": None,
        "flr": None,
        "nam": None,
        "pc": None
    }

    # When
    address = CivicAddress(**empty_data)

    # Then
    assert address.to_dict() == {}

# Initialize CivicAddress with empty strings for all parameters
def test_initialize_with_empty_strings():
    # Given
    empty_data = {
        "country": "",
        "a1": "",
        "a2": "",
        "a3": "",
        "a4": "",
        "a5": "",
        "a6": "",
        "prd": "",
        "pod": "",
        "sts": "",
        "hno": "",
        "hns": "",
        "lmk": "",
        "loc": "",
        "flr": "",
        "nam": "",
        "pc": ""
    }

    # When
    address = CivicAddress(**empty_data)

    # Then
    assert address.to_dict() == empty_data

# Convert a CivicAddress object with empty strings for all attributes to a dictionary
def test_convert_empty_strings_to_dict():
    # Given
    empty_data = {
        "country": "",
        "a1": "",
        "a2": "",
        "a3": "",
        "a4": "",
        "a5": "",
        "a6": "",
        "prd": "",
        "pod": "",
        "sts": "",
        "hno": "",
        "hns": "",
        "lmk": "",
        "loc": "",
        "flr": "",
        "nam": "",
        "pc": ""
    }

    # When
    address = CivicAddress(**empty_data)

    # Then
    assert address.to_dict() == empty_data

# Initialize CivicAddress with a mix of valid strings, None, and empty strings
def test_initialize_with_mixed_data():
    # Given
    mixed_data = {
        "country": "US",
        "a2": "",
        "a3": "Los Angeles",
        "a4": "Downtown",
        "a5": "90001",
        "prd": "",
        "pod": "PO Box 123",
        "sts": "Main St",
        "hno": "",
        "hns": "House Name",
        "loc": "Location Name",
        "flr": "5th Floor",
        "nam": "",
        "pc": "90001"
    }

    # When
    address = CivicAddress(**mixed_data)

    # Then
    assert address.to_dict() == mixed_data