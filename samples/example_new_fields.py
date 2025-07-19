#!/usr/bin/env python3
"""
Example demonstrating the new required fields in vCon library.

This example shows how to use the new fields:
- vCon level: extensions, must_support
- Party level: sip, did, jCard, timezone
- Dialog level: session_id, content_hash
"""

from datetime import datetime
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog


def main():
    """Demonstrate the new required fields functionality."""
    
    # Create a new vCon
    vcon = Vcon.build_new()
    
    # Add extensions to the vCon
    vcon.add_extension("video")
    vcon.add_extension("encryption")
    vcon.add_must_support("encryption")
    
    print(f"vCon extensions: {vcon.get_extensions()}")
    print(f"vCon must_support: {vcon.get_must_support()}")
    
    # Create parties with new fields
    party1 = Party(
        name="John Doe",
        tel="+1234567890",
        sip="sip:john@example.com",
        did="did:example:123456789abcdef",
        jCard={
            "fn": "John Doe",
            "tel": "+1234567890",
            "email": "john@example.com"
        },
        timezone="America/New_York"
    )
    
    party2 = Party(
        name="Jane Smith",
        tel="+0987654321",
        sip="sip:jane@example.com",
        did="did:example:abcdef123456789",
        jCard={
            "fn": "Jane Smith",
            "tel": "+0987654321",
            "email": "jane@example.com"
        },
        timezone="Europe/London"
    )
    
    # Add parties to vCon
    vcon.add_party(party1)
    vcon.add_party(party2)
    
    print(f"Added {len(vcon.parties)} parties")
    
    # Create a dialog with new fields
    dialog = Dialog(
        type="text",
        start=datetime.now(),
        parties=[0, 1],
        session_id="session-12345",
        body="Hello, this is a test message!",
        content_hash="abc123def456"
    )
    
    # Calculate and set content hash
    calculated_hash = dialog.calculate_content_hash()
    dialog.set_content_hash(calculated_hash)
    
    print(f"Dialog session_id: {dialog.get_session_id()}")
    print(f"Dialog content_hash: {dialog.get_content_hash()}")
    print(f"Content hash verification: {dialog.verify_content_hash(calculated_hash)}")
    
    # Add dialog to vCon
    vcon.add_dialog(dialog)
    
    print(f"Added {len(vcon.dialog)} dialogs")
    
    # Convert to JSON and print
    json_output = vcon.to_json()
    print("\nGenerated vCon JSON:")
    print(json_output)
    
    # Save to file
    vcon.save_to_file("samples/example_new_fields.vcon.json")
    print("\nSaved to samples/example_new_fields.vcon.json")


if __name__ == "__main__":
    main() 