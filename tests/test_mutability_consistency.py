"""
Test to demonstrate and verify the mutability consistency between vcon.dialog and vcon.parties properties.
"""
import pytest
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime, timezone


def test_mutability_consistency_demonstration():
    """
    Demonstrate that both vcon.dialog and vcon.parties now work consistently.
    
    This test shows that:
    - vcon.dialog returns mutable references (in-place modifications work)
    - vcon.parties now also returns mutable references (in-place modifications work)
    """
    # Create a vCon with parties and dialogs
    vcon = Vcon.build_new()
    
    # Add parties
    party1 = Party(name="Alice", tel="+1234567890")
    party2 = Party(name="Bob", tel="+1987654321")
    vcon.add_party(party1)
    vcon.add_party(party2)
    
    # Add dialogs
    dialog1 = Dialog(
        type="text",
        start=datetime.now(timezone.utc).isoformat(),
        parties=[0, 1],
        body="Hello, this is a test message"
    )
    dialog2 = Dialog(
        type="text", 
        start=datetime.now(timezone.utc).isoformat(),
        parties=[0],
        body="This is another message"
    )
    vcon.add_dialog(dialog1)
    vcon.add_dialog(dialog2)
    
    # Test dialog mutability (should work - returns direct references)
    dialog_list = vcon.dialog
    original_body = dialog_list[0]["body"]
    dialog_list[0]["body"] = "Modified dialog body"
    
    # Verify the change is reflected in the internal data
    assert vcon.dialog[0]["body"] == "Modified dialog body"
    assert vcon.vcon_dict["dialog"][0]["body"] == "Modified dialog body"
    
    # Test parties mutability (now works - returns mutable references)
    parties_list = vcon.parties
    original_name = parties_list[0]["name"]
    
    # This modification now affects the internal data
    parties_list[0]["name"] = "Modified Alice"
    
    # Verify the change IS reflected in the internal data (new consistent behavior)
    assert vcon.parties[0]["name"] == "Modified Alice"  # Modified name
    assert vcon.vcon_dict["parties"][0]["name"] == "Modified Alice"  # Internal data changed


def test_mutability_consistency_after_fix():
    """
    Test that after the fix, both vcon.dialog and vcon.parties behave consistently.
    
    This test verifies that both properties return mutable references.
    """
    # Create a vCon with parties and dialogs
    vcon = Vcon.build_new()
    
    # Add parties
    party1 = Party(name="Alice", tel="+1234567890")
    party2 = Party(name="Bob", tel="+1987654321")
    vcon.add_party(party1)
    vcon.add_party(party2)
    
    # Add dialogs
    dialog1 = Dialog(
        type="text",
        start=datetime.now(timezone.utc).isoformat(),
        parties=[0, 1],
        body="Hello, this is a test message"
    )
    vcon.add_dialog(dialog1)
    
    # Test dialog mutability (should work)
    dialog_list = vcon.dialog
    dialog_list[0]["body"] = "Modified dialog body"
    assert vcon.dialog[0]["body"] == "Modified dialog body"
    assert vcon.vcon_dict["dialog"][0]["body"] == "Modified dialog body"
    
    # Test parties mutability (should work after fix)
    parties_list = vcon.parties
    parties_list[0]["name"] = "Modified Alice"
    
    # Verify the change IS reflected in the internal data (after fix)
    assert vcon.parties[0]["name"] == "Modified Alice"
    assert vcon.vcon_dict["parties"][0]["name"] == "Modified Alice"
    
    # Test that we can still access party data as dictionaries
    assert isinstance(vcon.parties[0], dict)
    assert "name" in vcon.parties[0]
    assert "tel" in vcon.parties[0]


def test_party_object_creation_still_works():
    """
    Test that we can still create Party objects from the dictionary data when needed.
    """
    vcon = Vcon.build_new()
    
    # Add a party
    party = Party(name="Alice", tel="+1234567890")
    vcon.add_party(party)
    
    # Get the party data as dictionary
    party_dict = vcon.parties[0]
    
    # Create a Party object from the dictionary data
    party_obj = Party(**party_dict)
    
    # Verify the Party object works correctly
    assert party_obj.name == "Alice"
    assert party_obj.tel == "+1234567890"
    assert isinstance(party_obj, Party)


def test_backward_compatibility():
    """
    Test that existing code that expects Party objects still works.
    """
    vcon = Vcon.build_new()
    
    # Add a party
    party = Party(name="Alice", tel="+1234567890")
    vcon.add_party(party)
    
    # Get parties and create Party objects (common pattern)
    parties = [Party(**party_dict) for party_dict in vcon.parties]
    
    # Verify the Party objects work correctly
    assert len(parties) == 1
    assert parties[0].name == "Alice"
    assert parties[0].tel == "+1234567890"
    assert isinstance(parties[0], Party)
