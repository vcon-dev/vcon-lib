# Migration Guide: New Required Fields

This guide helps you migrate your existing vCon code to use the new required fields introduced in the latest version.

## Overview

The vCon library now supports additional fields as specified in the IETF vCon specification. All new fields are **optional** and **backward compatible**, so existing code will continue to work without changes.

## What's New

### vCon Object Level
- `extensions`: List of extension names used
- `must_support`: List of extensions that must be supported

### Party Object
- `sip`: SIP URI for VoIP communication
- `did`: Decentralized Identifier for blockchain-based identity
- `jCard`: vCard format contact information
- `timezone`: Party's timezone

### Dialog Object
- `session_id`: Session identifier for tracking conversations
- `content_hash`: Hash for content integrity verification (replaces alg/signature)

## Migration Steps

### Step 1: Add Extensions (Optional)

If you want to declare extension capabilities:

```python
# Old code
vcon = Vcon.build_new()

# New code
vcon = Vcon.build_new()
vcon.add_extension("video")
vcon.add_extension("encryption")
vcon.add_must_support("encryption")
```

### Step 2: Enhance Party Information (Optional)

Add additional contact and identification methods:

```python
# Old code
party = Party(
    name="John Doe",
    tel="+1234567890"
)

# New code
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
```

### Step 3: Add Session Tracking (Optional)

Track conversation sessions:

```python
# Old code
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    body="Hello!"
)

# New code
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    body="Hello!",
    session_id="session-12345"
)
```

### Step 4: Add Content Integrity (Optional)

Replace alg/signature with content_hash:

```python
# Old code
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    body="Hello!",
    alg="sha256",
    signature="abc123"
)

# New code
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    body="Hello!",
    session_id="session-12345"
)

# Calculate and set content hash
content_hash = dialog.calculate_content_hash()
dialog.set_content_hash(content_hash)
```

## Complete Migration Example

### Before Migration

```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime

# Create vCon
vcon = Vcon.build_new()

# Add party
party = Party(name="Alice", tel="+1234567890")
vcon.add_party(party)

# Add dialog
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0],
    body="Hello!"
)
vcon.add_dialog(dialog)

# Save
vcon.save_to_file("conversation.json")
```

### After Migration

```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime

# Create vCon with extensions
vcon = Vcon.build_new()
vcon.add_extension("video")
vcon.add_must_support("encryption")

# Add party with enhanced information
party = Party(
    name="Alice",
    tel="+1234567890",
    sip="sip:alice@example.com",
    did="did:example:123456789abcdef",
    jCard={
        "fn": "Alice Johnson",
        "tel": "+1234567890",
        "email": "alice@example.com"
    },
    timezone="America/New_York"
)
vcon.add_party(party)

# Add dialog with session tracking and integrity
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0],
    body="Hello!",
    session_id="session-12345"
)

# Calculate and set content hash
content_hash = dialog.calculate_content_hash()
dialog.set_content_hash(content_hash)

vcon.add_dialog(dialog)

# Save
vcon.save_to_file("conversation.json")
```

## JSON Output Comparison

### Before Migration
```json
{
    "uuid": "...",
    "vcon": "0.3.0",
    "parties": [{
        "name": "Alice",
        "tel": "+1234567890"
    }],
    "dialog": [{
        "type": "text",
        "start": "...",
        "parties": [0],
        "body": "Hello!"
    }]
}
```

### After Migration
```json
{
    "uuid": "...",
    "vcon": "0.3.0",
    "extensions": ["video"],
    "must_support": ["encryption"],
    "parties": [{
        "name": "Alice",
        "tel": "+1234567890",
        "sip": "sip:alice@example.com",
        "did": "did:example:123456789abcdef",
        "jCard": {
            "fn": "Alice Johnson",
            "tel": "+1234567890",
            "email": "alice@example.com"
        },
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

## Backward Compatibility

- **Existing code continues to work**: All new fields are optional
- **No breaking changes**: Existing vCon files will load correctly
- **Gradual adoption**: You can add new fields incrementally
- **Property handling**: New fields work with all property handling modes (default, strict, meta)

## Testing Your Migration

1. **Run existing tests**: Ensure they still pass
2. **Test new functionality**: Use the example in `samples/example_new_fields.py`
3. **Validate JSON output**: Check that new fields appear correctly
4. **Verify backward compatibility**: Load old vCon files to ensure they work

## Need Help?

- Check the full documentation in `docs/source/new_required_fields.rst`
- Run the example: `python samples/example_new_fields.py`
- Review the test files for usage examples
- Open an issue if you encounter problems 