Usage Guide
===========

This guide will help you get started with using the vcon library.

Basic Usage
----------

Creating a vCon Container
~~~~~~~~~~~~~~~~~~~~~~~

Here's a simple example of creating a vCon container:

.. code-block:: python

    from vcon import Vcon
    from vcon.party import Party
    from vcon.dialog import Dialog
    from datetime import datetime, timezone
    
    # Create a new vCon container
    vcon = Vcon.build_new()
    
    # Add extensions and must-support requirements
    vcon.add_extension("video")
    vcon.add_extension("encryption")
    vcon.add_must_support("encryption")
    
    # Add participants with enhanced contact information
    party = Party(
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
    vcon.add_party(party)
    
    # Create a dialog with session tracking and content integrity
    dialog = Dialog(
        type="text",
        start=datetime.now(timezone.utc),
        parties=[0],
        body="Hello, this is a test message!",
        session_id="session-12345"
    )
    
    # Calculate and set content hash for integrity verification
    content_hash = dialog.calculate_content_hash()
    dialog.set_content_hash(content_hash)
    
    vcon.add_dialog(dialog)
    
    # Save the container
    vcon.save_to_file("my_conference.vcon")

Reading a vCon Container
~~~~~~~~~~~~~~~~~~~~~~~

To read an existing vCon container:

.. code-block:: python

    from vcon import Vcon
    
    # Load a vCon container
    vcon = Vcon.load_from_file("my_conference.vcon")
    
    # Access extensions
    extensions = vcon.get_extensions()
    must_support = vcon.get_must_support()
    
    # Get participants with enhanced information
    parties = vcon.parties
    for party in parties:
        print(f"Name: {party.name}")
        print(f"SIP: {getattr(party, 'sip', 'Not set')}")
        print(f"DID: {getattr(party, 'did', 'Not set')}")
        print(f"Timezone: {getattr(party, 'timezone', 'Not set')}")
    
    # Get dialogs with session information
    dialogs = vcon.dialog
    for dialog in dialogs:
        print(f"Session ID: {getattr(dialog, 'session_id', 'Not set')}")
        print(f"Content Hash: {getattr(dialog, 'content_hash', 'Not set')}")

Advanced Usage
-------------

Working with Extensions
~~~~~~~~~~~~~~~~~~~~~~

Extensions allow vCon implementations to declare additional capabilities:

.. code-block:: python

    from vcon import Vcon
    
    vcon = Vcon.build_new()
    
    # Add extensions used in this vCon
    vcon.add_extension("video")
    vcon.add_extension("encryption")
    vcon.add_extension("analytics")
    
    # Specify extensions that must be supported
    vcon.add_must_support("encryption")
    vcon.add_must_support("video")
    
    # Check extension compatibility
    required = vcon.get_must_support()
    available = vcon.get_extensions()
    
    for ext in required:
        if ext not in available:
            print(f"Warning: Required extension '{ext}' not available")

Working with Enhanced Party Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parties now support additional contact and identification methods:

.. code-block:: python

    from vcon.party import Party
    
    # Create a party with SIP URI for VoIP communication
    party = Party(
        name="Alice Johnson",
        tel="+1234567890",
        sip="sip:alice@example.com",
        did="did:example:123456789abcdef",
        jCard={
            "fn": "Alice Johnson",
            "tel": "+1234567890",
            "email": "alice@example.com",
            "org": "Example Corp"
        },
        timezone="America/New_York"
    )

Working with Dialog Session Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dialogs now support session tracking and content integrity verification:

.. code-block:: python

    from vcon.dialog import Dialog
    from datetime import datetime, timezone
    
    # Create a dialog with session tracking
    dialog = Dialog(
        type="text",
        start=datetime.now(timezone.utc),
        parties=[0, 1],
        body="Hello, this is a test message!",
        session_id="session-12345"
    )
    
    # Calculate content hash for integrity verification
    content_hash = dialog.calculate_content_hash()
    dialog.set_content_hash(content_hash)
    
    # Verify content integrity
    is_valid = dialog.verify_content_hash(content_hash)
    print(f"Content integrity: {is_valid}")

Working with Media Files
~~~~~~~~~~~~~~~~~~~~~~~

You can attach and manage media files in a vCon container:

.. code-block:: python

    from vcon import Vcon
    
    vcon = Vcon()
    
    # Add a video recording
    vcon.add_media("recording.mp4", media_type="video/mp4")
    
    # Add a transcript
    vcon.add_media("transcript.txt", media_type="text/plain")

.. _api-reference:

API Reference
------------

For more detailed information about the API, please refer to the sections below. 