# Migration Guide: Version Management Changes

This guide helps you migrate your existing vCon code to work with the updated version management system.

## Overview

The vCon library has been updated to align with the latest vCon specification changes. The most significant change is that the **version field is now optional** and version management has been simplified. All changes are **backward compatible**, so existing code will continue to work without changes.

## Key Changes

### Version Field is Now Optional
- The `vcon` field is no longer required in vCon objects
- No automatic version assignment or migration
- Existing vCons with version fields continue to work unchanged
- New vCons can be created without version fields

### Removed Version Management
- Removed `strict_version` parameter from all methods
- No more automatic version migration
- No more version enforcement or validation

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

### Step 1: Update Method Calls (Required if using strict_version)

If you were using the `strict_version` parameter, you need to remove it:

```python
# Old code (will cause errors)
vcon = Vcon.load("file.json", strict_version=True)
vcon = Vcon.build_from_json(json_str, strict_version=True)
vcon = Vcon(data, strict_version=True)

# New code (remove strict_version parameter)
vcon = Vcon.load("file.json")
vcon = Vcon.build_from_json(json_str)
vcon = Vcon(data)
```

### Step 2: Version Field Handling (Optional)

The version field is now optional. You can choose to:

**Option A: Remove version fields from new vCons**
```python
# Old code
vcon = Vcon({"uuid": "123", "vcon": "0.3.0", "created_at": "2024-01-01T00:00:00Z"})

# New code (version field optional)
vcon = Vcon({"uuid": "123", "created_at": "2024-01-01T00:00:00Z"})
```

**Option B: Keep existing version fields**
```python
# This still works - no changes needed
vcon = Vcon({"uuid": "123", "vcon": "0.3.0", "created_at": "2024-01-01T00:00:00Z"})
```

### Step 3: Add Extensions (Optional)

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