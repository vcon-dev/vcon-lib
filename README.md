# vCon Library

A Python library for working with vCon (Virtual Conversation) objects according to the vCon specification.

## Overview

The vCon library provides a complete implementation of the vCon format for representing conversations and related metadata. It supports all features defined in the latest vCon specification including:

- **Conversation Management**: Parties, dialogs, attachments, and analysis
- **Contact Information**: Multiple contact methods (tel, email, SIP, DID)
- **Media Support**: Audio, video, text, and image formats
- **Security**: Digital signatures and content hashing
- **Extensibility**: Extensions and must_support fields
- **Location Data**: Civic address information (GEOPRIV)
- **Event Tracking**: Party history with join/drop/hold/mute events

## Key Features

This library implements the latest vCon specification with the following features:

### Enhanced Party Information
```python
from vcon import Vcon, Party

# Create a party with enhanced contact information
party = Party(
    tel="+1234567890",
    name="John Doe",
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

### Extensions and Must-Support
```python
vcon = Vcon.build_new()

# Add extensions used in this vCon
vcon.add_extension("video")
vcon.add_extension("encryption")

# Add extensions that must be supported
vcon.add_must_support("encryption")

print(vcon.get_extensions())  # ['video', 'encryption']
print(vcon.get_must_support())  # ['encryption']
```

### Enhanced Dialog Support
```python
from vcon import Dialog
from datetime import datetime

# Create dialog with new fields
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    session_id="session-12345",
    content_hash="c8d3d67f662a787e96e74ccb0a77803138c0f13495a186ccbde495c57c385608",
    application="chat-app",
    message_id="<message-id@example.com>"
)
```

### Party History Events
```python
from vcon import PartyHistory
from datetime import datetime

# Track party events
history = [
    PartyHistory(0, "join", datetime.now()),
    PartyHistory(1, "join", datetime.now()),
    PartyHistory(0, "hold", datetime.now()),
    PartyHistory(0, "unhold", datetime.now()),
    PartyHistory(1, "drop", datetime.now())
]
```

### Disposition Values for Incomplete Dialogs
```python
# Create incomplete dialog with proper disposition
incomplete_dialog = Dialog(
    type="incomplete",
    start=datetime.now(),
    parties=[0],
    disposition="no-answer"  # Valid: no-answer, congestion, failed, busy, hung-up, voicemail-no-message
)
```

### Civic Address Support
```python
from vcon import CivicAddress

# Create civic address with GEOPRIV fields
address = CivicAddress(
    country="US",
    a1="CA",
    a3="San Francisco",
    sts="Market Street",
    hno="123",
    pc="94102"
)

party = Party(name="Jane", civicaddress=address)
```

## Installation

```bash
pip install vcon
```

## Basic Usage

### Creating a vCon

```python
from vcon import Vcon, Party, Dialog
from datetime import datetime

# Create a new vCon
vcon = Vcon.build_new()

# Add parties
alice = Party(tel="+1234567890", name="Alice", role="caller")
bob = Party(tel="+1987654321", name="Bob", role="agent")

vcon.add_party(alice)
vcon.add_party(bob)

# Add dialog
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    body="Hello, this is a test message!"
)

vcon.add_dialog(dialog)

# Save to file
vcon.save_to_file("conversation.vcon.json")
```

### Loading a vCon

```python
# Load from file
vcon = Vcon.load("conversation.vcon.json")

# Load from URL
vcon = Vcon.load("https://example.com/conversation.vcon.json")
```

### Validation

```python
# Validate a vCon
is_valid, errors = vcon.is_valid()

if is_valid:
    print("vCon is valid")
else:
    print("Validation errors:", errors)

# Validate from file
is_valid, errors = Vcon.validate_file("conversation.vcon.json")
```

## Media Support

### Audio and Video

```python
# Add audio recording
audio_dialog = Dialog(
    type="recording",
    start=datetime.now(),
    parties=[0, 1],
    url="https://example.com/recording.wav",
    mimetype="audio/x-wav"
)

# Add video with metadata
video_dialog = Dialog(
    type="video",
    start=datetime.now(),
    parties=[0, 1],
    url="https://example.com/video.mp4",
    mimetype="video/mp4",
    resolution="1920x1080",
    frame_rate=30.0,
    codec="H.264"
)
```

### Supported Media Types

**Audio**: `audio/x-wav`, `audio/x-mp3`, `audio/x-mp4`, `audio/ogg`
**Video**: `video/x-mp4`, `video/ogg`
**Text**: `text/plain`
**Multipart**: `multipart/mixed`

## Security Features

### Digital Signatures

```python
from cryptography.hazmat.primitives import serialization

# Generate key pair
private_key, public_key = Vcon.generate_key_pair()

# Sign the vCon
vcon.sign(private_key)

# Verify signature
is_valid = vcon.verify(public_key)
```

### Content Hashing

```python
# Calculate content hash for external files
content_hash = dialog.calculate_content_hash("sha256")

# Verify content integrity
is_valid = dialog.verify_content_hash(expected_hash, "sha256")
```

## Advanced Features

### Property Handling

```python
# Strict mode - only allow standard properties
vcon = Vcon.load("file.json", property_handling="strict")

# Meta mode - move non-standard properties to meta object
vcon = Vcon.load("file.json", property_handling="meta")

# Default mode - keep all properties
vcon = Vcon.load("file.json", property_handling="default")
```

### Transfer Dialogs

```python
# Create transfer dialog
transfer_data = {
    "transferee": 0,
    "transferor": 1,
    "transfer_target": 2,
    "original": 0,
    "target_dialog": 1
}

vcon.add_transfer_dialog(
    start=datetime.now(),
    transfer_data=transfer_data,
    parties=[0, 1, 2]
)
```

### Analysis Data

```python
# Add analysis
vcon.add_analysis(
    type="sentiment",
    dialog=0,
    vendor="example-vendor",
    body={"sentiment": "positive", "confidence": 0.95},
    encoding="json"
)
```

## Specification Compliance

This library implements the latest vCon specification with:

- ✅ All required fields and validation
- ✅ Proper media type support
- ✅ Civic address (GEOPRIV) compliance
- ✅ Party history event tracking
- ✅ Transfer dialog support
- ✅ Content hashing and security
- ✅ Extensions and must_support
- ✅ Flexible versioning (version field is optional)
- ✅ Backward compatibility

## Testing

Run the test suite:

```bash
pytest tests/
```

All tests pass, covering:
- Basic functionality
- Enhanced vCon features
- Validation and error handling
- Media type support
- Security features
- Flexible versioning
- Backward compatibility

## License

This project is licensed under the MIT License - see the LICENSE file for details.
