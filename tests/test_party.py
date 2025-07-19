from datetime import datetime
from vcon.party import Party, PartyHistory
from vcon.civic_address import CivicAddress


def test_party_named_parameters():
    party = Party(tel="123-456-7890", name="Test User", mailto="test@example.com")

    assert party.tel == "123-456-7890"
    assert party.name == "Test User"
    assert party.mailto == "test@example.com"


def test_party_none_parameters_not_set():
    party = Party(tel="123-456-7890", name=None)

    assert party.tel == "123-456-7890"
    assert not hasattr(party, "name")


def test_party_additional_parameters():
    party = Party(
        tel="123-456-7890",
        custom_field="value",
        another_field=42,
        nested_dict={"key": "value"},
    )

    assert party.tel == "123-456-7890"
    assert party.custom_field == "value"
    assert party.another_field == 42
    assert party.nested_dict == {"key": "value"}


def test_party_to_dict():
    party = Party(tel="123-456-7890", name="Test User", custom_field="value")

    expected_dict = {
        "tel": "123-456-7890",
        "name": "Test User",
        "custom_field": "value",
    }

    assert party.to_dict() == expected_dict


def test_party_with_civic_address():
    address = CivicAddress(a1="US", a2="RI", a3="Newport")

    party = Party(tel="401-456-7890", civicaddress=address)

    assert party.tel == "401-456-7890"
    assert party.civicaddress == address


def test_party_history():
    """Test PartyHistory class."""
    party_history = PartyHistory(0, "join", datetime.now())
    assert party_history.party == 0
    assert party_history.event == "join"
    assert isinstance(party_history.time, datetime)


def test_party_history_to_dict():
    """Test PartyHistory to_dict method with ISO 8601 time serialization."""
    test_time = datetime(2023, 1, 15, 14, 30, 45, 123456)
    party_history = PartyHistory(1, "leave", test_time)
    
    result = party_history.to_dict()
    expected = {
        "party": 1,
        "event": "leave", 
        "time": "2023-01-15T14:30:45.123456"
    }
    
    assert result == expected
    assert isinstance(result["time"], str)


def test_party_new_fields():
    """Test the new required fields for Party."""
    party = Party(
        name="John Doe",
        tel="+1234567890",
        sip="sip:john@example.com",
        did="did:example:123456789abcdef",
        jCard={"fn": "John Doe", "tel": "+1234567890"},
        timezone="America/New_York"
    )
    
    assert party.name == "John Doe"
    assert party.tel == "+1234567890"
    assert party.sip == "sip:john@example.com"
    assert party.did == "did:example:123456789abcdef"
    assert party.jCard == {"fn": "John Doe", "tel": "+1234567890"}
    assert party.timezone == "America/New_York"


def test_party_new_fields_to_dict():
    """Test that new Party fields are included in to_dict()."""
    party = Party(
        name="Jane Smith",
        sip="sip:jane@example.com",
        did="did:example:abcdef123456789",
        jCard={"fn": "Jane Smith", "email": "jane@example.com"},
        timezone="Europe/London"
    )
    
    party_dict = party.to_dict()
    assert party_dict["name"] == "Jane Smith"
    assert party_dict["sip"] == "sip:jane@example.com"
    assert party_dict["did"] == "did:example:abcdef123456789"
    assert party_dict["jCard"] == {"fn": "Jane Smith", "email": "jane@example.com"}
    assert party_dict["timezone"] == "Europe/London"


def test_party_new_fields_optional():
    """Test that new Party fields are optional."""
    party = Party(name="Test User")
    
    party_dict = party.to_dict()
    assert party_dict["name"] == "Test User"
    assert "sip" not in party_dict
    assert "did" not in party_dict
    assert "jCard" not in party_dict
    assert "timezone" not in party_dict


def test_party_new_fields_with_kwargs():
    """Test that new Party fields work with kwargs."""
    party = Party(
        name="Test User",
        sip="sip:test@example.com",
        custom_field="custom_value"
    )
    
    party_dict = party.to_dict()
    assert party_dict["name"] == "Test User"
    assert party_dict["sip"] == "sip:test@example.com"
    assert party_dict["custom_field"] == "custom_value"
