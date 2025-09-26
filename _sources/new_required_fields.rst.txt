New Required Fields
==================

This document describes the new required fields added to the vCon library to support the latest IETF vCon specification requirements.

Overview
--------

The vCon library has been updated to include new fields that enhance functionality and interoperability:

- **vCon Object Level**: Extensions and must-support requirements
- **Party Object**: SIP URI, Decentralized Identifier (DID), vCard format, and timezone
- **Dialog Object**: Session identifier and content hash for integrity verification

vCon Object Level Extensions
---------------------------

Extensions allow vCon implementations to declare additional capabilities and requirements.

Adding Extensions
~~~~~~~~~~~~~~~~

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

Managing Extensions
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Get current extensions
    extensions = vcon.get_extensions()  # ["video", "encryption", "analytics"]
    must_support = vcon.get_must_support()  # ["encryption", "video"]
    
    # Remove extensions if needed
    vcon.remove_extension("analytics")
    vcon.remove_must_support("video")
    
    # Check extension compatibility
    required = vcon.get_must_support()
    available = vcon.get_extensions()
    
    for ext in required:
        if ext not in available:
            print(f"Warning: Required extension '{ext}' not available")

Enhanced Party Information
-------------------------

Parties now support additional contact and identification methods for better interoperability.

SIP URI Support
~~~~~~~~~~~~~~

SIP (Session Initiation Protocol) URIs allow parties to be contacted via VoIP:

.. code-block:: python

    from vcon.party import Party
    
    party = Party(
        name="John Doe",
        tel="+1234567890",
        sip="sip:john@example.com"
    )
```

Decentralized Identifier (DID) Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DIDs provide blockchain-based identity management:

.. code-block:: python

    party = Party(
        name="Alice Smith",
        did="did:example:123456789abcdef"
    )
```

vCard Format Support
~~~~~~~~~~~~~~~~~~~

vCard format provides standardized contact information:

.. code-block:: python

    party = Party(
        name="Bob Johnson",
        jCard={
            "fn": "Bob Johnson",
            "tel": "+1234567890",
            "email": "bob@example.com",
            "org": "Example Corp",
            "title": "Software Engineer"
        }
    )
```

Timezone Support
~~~~~~~~~~~~~~~

Timezone information helps with proper time handling:

.. code-block:: python

    party = Party(
        name="Carol Wilson",
        timezone="America/New_York"
    )
```

Complete Party Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    party = Party(
        name="John Doe",
        tel="+1234567890",
        sip="sip:john@example.com",
        did="did:example:123456789abcdef",
        jCard={
            "fn": "John Doe",
            "tel": "+1234567890",
            "email": "john@example.com",
            "org": "Example Corp"
        },
        timezone="America/New_York"
    )
```

Dialog Session Management and Content Integrity
----------------------------------------------

Dialogs now support session tracking and content integrity verification.

Session Identifier
~~~~~~~~~~~~~~~~~

Session IDs help track conversation sessions across multiple dialogs:

.. code-block:: python

    from vcon.dialog import Dialog
    from datetime import datetime, timezone
    
    dialog = Dialog(
        type="text",
        start=datetime.now(timezone.utc),
        parties=[0, 1],
        body="Hello, this is a test message!",
        session_id="session-12345"
    )
    
    # Get session ID
    session_id = dialog.get_session_id()
    
    # Set session ID
    dialog.set_session_id("session-67890")
```

Content Hash for Integrity Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Content hashes ensure data integrity and can replace the older alg/signature fields:

.. code-block:: python

    # Calculate content hash
    content_hash = dialog.calculate_content_hash()
    dialog.set_content_hash(content_hash)
    
    # Verify content integrity
    is_valid = dialog.verify_content_hash(content_hash)
    print(f"Content integrity: {is_valid}")
    
    # Get current hash
    current_hash = dialog.get_content_hash()
    
    # Set hash manually
    dialog.set_content_hash("abc123def456")
```

Complete Dialog Example
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    dialog = Dialog(
        type="text",
        start=datetime.now(timezone.utc),
        parties=[0, 1],
        body="Hello, this is a test message!",
        session_id="session-12345"
    )
    
    # Calculate and set content hash for integrity verification
    content_hash = dialog.calculate_content_hash()
    dialog.set_content_hash(content_hash)
    
    # Verify content integrity
    is_valid = dialog.verify_content_hash(content_hash)
    print(f"Content integrity: {is_valid}")
```

JSON Serialization
-----------------

The new fields are properly serialized to JSON:

.. code-block:: python

    # Create a vCon with new fields
    vcon = Vcon.build_new()
    vcon.add_extension("video")
    vcon.add_must_support("encryption")
    
    party = Party(
        name="John Doe",
        sip="sip:john@example.com",
        did="did:example:123456789abcdef",
        jCard={"fn": "John Doe"},
        timezone="America/New_York"
    )
    vcon.add_party(party)
    
    dialog = Dialog(
        type="text",
        start=datetime.now(timezone.utc),
        parties=[0],
        body="Hello!",
        session_id="session-12345"
    )
    dialog.set_content_hash(dialog.calculate_content_hash())
    vcon.add_dialog(dialog)
    
    # Serialize to JSON
    json_data = vcon.to_json()
    print(json_data)
```

The resulting JSON will include:

.. code-block:: json

    {
        "uuid": "...",
        "extensions": ["video"],
        "must_support": ["encryption"],
        "parties": [{
            "name": "John Doe",
            "sip": "sip:john@example.com",
            "did": "did:example:123456789abcdef",
            "jCard": {"fn": "John Doe"},
            "timezone": "America/New_York"
        }],
        "dialog": [{
            "type": "text",
            "start": "...",
            "parties": [0],
            "body": "Hello!",
            "session_id": "session-12345",
            "content_hash": "..."
        }]
    }
```

Backward Compatibility
---------------------

All new fields are optional and backward compatible:

- Existing vCon objects without the new fields will continue to work
- New fields only appear in JSON output when they have values
- The library maintains compatibility with older vCon versions

Migration Guide
--------------

To migrate existing code to use the new fields:

1. **Add Extensions**: Use `add_extension()` and `add_must_support()` to declare capabilities
2. **Enhance Parties**: Add SIP, DID, jCard, and timezone information to Party objects
3. **Track Sessions**: Add session_id to Dialog objects for better session management
4. **Verify Integrity**: Use content_hash for data integrity verification instead of alg/signature

Example migration:

.. code-block:: python

    # Old code
    party = Party(name="John", tel="+1234567890")
    dialog = Dialog(type="text", start=datetime.now(), parties=[0], body="Hello")
    
    # New code
    party = Party(
        name="John", 
        tel="+1234567890",
        sip="sip:john@example.com",
        timezone="America/New_York"
    )
    
    dialog = Dialog(
        type="text", 
        start=datetime.now(), 
        parties=[0], 
        body="Hello",
        session_id="session-12345"
    )
    dialog.set_content_hash(dialog.calculate_content_hash())
``` 