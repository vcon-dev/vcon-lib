# vCon Library API Reference

Complete API documentation for the vCon library - a Python implementation of the vCon 0.3.0 specification for Virtual Conversation objects.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Core Classes](#core-classes)
  - [Vcon](#vcon-class)
  - [Party](#party-class)
  - [Dialog](#dialog-class)
  - [CivicAddress](#civicaddress-class)
  - [PartyHistory](#partyhistory-class)
  - [Attachment](#attachment-class)
- [Constants](#constants)
- [Examples](#examples)

## Overview

The vCon library provides a complete Python implementation of the vCon 0.3.0 specification for representing virtual conversations. It supports all features including parties, dialogs, attachments, analysis, digital signatures, and extensibility.

## Installation

```bash
pip install vcon
```

For image processing support:
```bash
pip install vcon[image]
```

## Core Classes

### Vcon Class

The main class for working with vCon objects.

#### Constructor

```python
Vcon(vcon_dict: Dict[str, Any] = None, property_handling: str = "default", strict_version: bool = False)
```

**Parameters:**
- `vcon_dict` (Dict[str, Any], optional): Dictionary representing a vCon. Defaults to empty dict.
- `property_handling` (str): How to handle non-standard properties:
  - `"default"`: Keep non-standard properties (default)
  - `"strict"`: Remove non-standard properties
  - `"meta"`: Move non-standard properties to meta object
- `strict_version` (bool): If True, reject vCons not at version "0.3.0". Defaults to False.

#### Class Methods

##### `build_new() -> Vcon`
Create a new vCon object with default values.

```python
vcon = Vcon.build_new()
```

##### `build_from_json(json_str: str, property_handling: str = "default", strict_version: bool = False) -> Vcon`
Create a vCon object from JSON string.

```python
vcon = Vcon.build_from_json('{"uuid": "123", "vcon": "0.3.0"}')
```

##### `load(file_path_or_url: str, property_handling: str = "default", strict_version: bool = False) -> Vcon`
Load a vCon from file or URL.

```python
# From file
vcon = Vcon.load("conversation.vcon.json")

# From URL
vcon = Vcon.load("https://example.com/conversation.vcon.json")
```

##### `load_from_file(file_path: str, property_handling: str = "default", strict_version: bool = False) -> Vcon`
Load a vCon from a local file.

##### `load_from_url(url: str, property_handling: str = "default", strict_version: bool = False) -> Vcon`
Load a vCon from a URL.

##### `validate_file(file_path: str) -> Tuple[bool, List[str]]`
Validate a vCon file.

```python
is_valid, errors = Vcon.validate_file("conversation.vcon.json")
```

##### `validate_json(json_str: str) -> Tuple[bool, List[str]]`
Validate a vCon JSON string.

##### `generate_key_pair() -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]`
Generate RSA key pair for digital signatures.

```python
private_key, public_key = Vcon.generate_key_pair()
```

##### `uuid8_domain_name(domain_name: str) -> str`
Generate UUID8 with domain name.

##### `uuid8_time(custom_c_62_bits: int) -> str`
Generate UUID8 with custom time bits.

#### Instance Methods

##### Party Management

###### `add_party(party: Party) -> None`
Add a party to the vCon.

```python
party = Party(tel="+1234567890", name="Alice", role="caller")
vcon.add_party(party)
```

###### `find_party_index(by: str, val: str) -> Optional[int]`
Find party index by field value.

```python
index = vcon.find_party_index("tel", "+1234567890")
```

##### Dialog Management

###### `add_dialog(dialog: Dialog) -> None`
Add a dialog to the vCon.

```python
dialog = Dialog(type="text", start=datetime.now(), parties=[0, 1], body="Hello")
vcon.add_dialog(dialog)
```

###### `find_dialog(by: str, val: str) -> Optional[Dialog]`
Find dialog by field value.

```python
dialog = vcon.find_dialog("type", "text")
```

###### `find_dialogs_by_type(type: str) -> List[Dict[str, Any]]`
Find all dialogs of a specific type.

```python
text_dialogs = vcon.find_dialogs_by_type("text")
```

###### `add_transfer_dialog(start: Union[datetime, str], transfer_data: Dict[str, Any], parties: List[int]) -> None`
Add a transfer dialog.

```python
transfer_data = {
    "transferee": 0,
    "transferor": 1,
    "transfer_target": 2
}
vcon.add_transfer_dialog(datetime.now(), transfer_data, [0, 1, 2])
```

###### `add_incomplete_dialog(start: Union[datetime, str], disposition: str, parties: List[int]) -> None`
Add an incomplete dialog.

```python
vcon.add_incomplete_dialog(datetime.now(), "no-answer", [0])
```

##### Attachment Management

###### `add_attachment(type: str, body: Any, encoding: str = "none") -> Attachment`
Add an attachment to the vCon.

```python
attachment = vcon.add_attachment("transcript", "Full conversation...", "none")
```

###### `add_image(image_path: str, type: str = "image") -> Attachment`
Add an image attachment from file.

```python
attachment = vcon.add_image("screenshot.png", "screenshot")
```

###### `find_attachment_by_type(type: str) -> Optional[Dict[str, Any]]`
Find attachment by type.

```python
transcript = vcon.find_attachment_by_type("transcript")
```

##### Analysis Management

###### `add_analysis(type: str, dialog: Union[int, List[int]], vendor: str, body: Any, encoding: str = "none") -> None`
Add analysis data to the vCon.

```python
vcon.add_analysis(
    type="sentiment",
    dialog=[0, 1],
    vendor="SentimentAnalyzer",
    body={"sentiment": "positive", "confidence": 0.85},
    encoding="json"
)
```

###### `find_analysis_by_type(type: str) -> Optional[Dict[str, Any]]`
Find analysis by type.

```python
sentiment = vcon.find_analysis_by_type("sentiment")
```

##### Tag Management

###### `add_tag(tag_name: str, tag_value: str) -> None`
Add a tag to the vCon.

```python
vcon.add_tag("customer_id", "12345")
```

###### `get_tag(tag_name: str) -> Optional[str]`
Get a tag value.

```python
customer_id = vcon.get_tag("customer_id")
```

##### Extension Management

###### `add_extension(extension: str) -> None`
Add an extension to the vCon.

```python
vcon.add_extension("video")
```

###### `get_extensions() -> List[str]`
Get list of extensions.

```python
extensions = vcon.get_extensions()
```

###### `remove_extension(extension: str) -> None`
Remove an extension.

```python
vcon.remove_extension("video")
```

###### `add_must_support(extension: str) -> None`
Add a must-support extension.

```python
vcon.add_must_support("encryption")
```

###### `get_must_support() -> List[str]`
Get list of must-support extensions.

```python
must_support = vcon.get_must_support()
```

###### `remove_must_support(extension: str) -> None`
Remove a must-support extension.

##### Security

###### `sign(private_key: Union[rsa.RSAPrivateKey, bytes]) -> None`
Sign the vCon with a private key.

```python
vcon.sign(private_key)
```

###### `verify(public_key: Union[rsa.RSAPublicKey, bytes]) -> bool`
Verify the vCon signature.

```python
is_valid = vcon.verify(public_key)
```

##### Validation

###### `is_valid() -> Tuple[bool, List[str]]`
Validate the vCon object.

```python
is_valid, errors = vcon.is_valid()
```

##### Serialization

###### `to_json() -> str`
Convert vCon to JSON string.

```python
json_str = vcon.to_json()
```

###### `to_dict() -> Dict[str, Any]`
Convert vCon to dictionary.

```python
vcon_dict = vcon.to_dict()
```

###### `dumps() -> str`
Alias for `to_json()`.

###### `save_to_file(file_path: str) -> None`
Save vCon to file.

```python
vcon.save_to_file("conversation.vcon.json")
```

##### HTTP Operations

###### `post_to_url(url: str, headers: Optional[Dict[str, str]] = None) -> requests.Response`
Post vCon to URL.

```python
response = vcon.post_to_url("https://api.example.com/vcon", headers={"Authorization": "Bearer token"})
```

##### Timestamp Management

###### `set_created_at(created_at: Union[str, datetime]) -> None`
Set the creation timestamp.

###### `set_updated_at(timestamp: Union[str, datetime]) -> None`
Set the update timestamp.

#### Properties

##### `uuid -> str`
Get the vCon UUID.

##### `vcon -> str`
Get the vCon version.

##### `subject -> Optional[str]`
Get the vCon subject.

##### `created_at`
Get the creation timestamp.

##### `updated_at`
Get the update timestamp.

##### `redacted`
Get the redacted flag.

##### `appended`
Get the appended flag.

##### `group`
Get the group information.

##### `meta`
Get the metadata.

##### `parties -> List[Party]`
Get list of parties.

##### `dialog -> List[Dict[str, Any]]`
Get list of dialogs.

##### `attachments -> List[Dict[str, Any]]`
Get list of attachments.

##### `analysis -> List[Dict[str, Any]]`
Get list of analysis data.

##### `tags -> Optional[Dict[str, Any]]`
Get all tags.

### Party Class

Represents a participant in a vCon conversation.

#### Constructor

```python
Party(
    tel: Optional[str] = None,
    stir: Optional[str] = None,
    mailto: Optional[str] = None,
    name: Optional[str] = None,
    validation: Optional[str] = None,
    gmlpos: Optional[str] = None,
    civicaddress: Optional[CivicAddress] = None,
    uuid: Optional[str] = None,
    role: Optional[str] = None,
    contact_list: Optional[str] = None,
    meta: Optional[dict] = None,
    sip: Optional[str] = None,
    did: Optional[str] = None,
    jCard: Optional[dict] = None,
    timezone: Optional[str] = None,
    **kwargs
)
```

**Parameters:**
- `tel` (str, optional): Telephone number
- `stir` (str, optional): STIR identifier
- `mailto` (str, optional): Email address
- `name` (str, optional): Display name
- `validation` (str, optional): Validation information
- `gmlpos` (str, optional): GML position coordinates
- `civicaddress` (CivicAddress, optional): Civic address information
- `uuid` (str, optional): Unique identifier
- `role` (str, optional): Role in conversation (e.g., "caller", "agent")
- `contact_list` (str, optional): Contact list reference
- `meta` (dict, optional): Additional metadata
- `sip` (str, optional): SIP URI for VoIP communication
- `did` (str, optional): Decentralized Identifier
- `jCard` (dict, optional): vCard format contact information
- `timezone` (str, optional): Party's timezone

#### Methods

##### `to_dict() -> Dict[str, Any]`
Convert Party to dictionary.

```python
party_dict = party.to_dict()
```

### Dialog Class

Represents a dialog segment in a vCon conversation.

#### Constructor

```python
Dialog(
    type: str,
    start: Union[datetime, str],
    parties: List[int],
    originator: Optional[int] = None,
    mimetype: Optional[str] = None,
    filename: Optional[str] = None,
    body: Optional[str] = None,
    encoding: Optional[str] = None,
    url: Optional[str] = None,
    alg: Optional[str] = None,
    signature: Optional[str] = None,
    disposition: Optional[str] = None,
    party_history: Optional[List[PartyHistory]] = None,
    transferee: Optional[int] = None,
    transferor: Optional[int] = None,
    transfer_target: Optional[int] = None,
    original: Optional[int] = None,
    consultation: Optional[int] = None,
    target_dialog: Optional[int] = None,
    campaign: Optional[str] = None,
    interaction: Optional[str] = None,
    skill: Optional[str] = None,
    duration: Optional[float] = None,
    meta: Optional[dict] = None,
    metadata: Optional[Dict[str, Any]] = None,
    transfer: Optional[Dict[str, Any]] = None,
    signaling: Optional[Dict[str, Any]] = None,
    resolution: Optional[str] = None,
    frame_rate: Optional[float] = None,
    codec: Optional[str] = None,
    bitrate: Optional[int] = None,
    thumbnail: Optional[str] = None,
    session_id: Optional[str] = None,
    content_hash: Optional[str] = None,
    application: Optional[str] = None,
    message_id: Optional[str] = None,
    **kwargs
)
```

**Parameters:**
- `type` (str): Dialog type ("text", "recording", "transfer", "incomplete", "audio", "video")
- `start` (Union[datetime, str]): Start time
- `parties` (List[int]): List of party indices
- `originator` (int, optional): Originator party index
- `mimetype` (str, optional): MIME type of content
- `filename` (str, optional): Filename
- `body` (str, optional): Content body
- `encoding` (str, optional): Content encoding
- `url` (str, optional): External URL
- `alg` (str, optional): Signature algorithm
- `signature` (str, optional): Content signature
- `disposition` (str, optional): Disposition for incomplete dialogs
- `party_history` (List[PartyHistory], optional): Party event history
- `transferee` (int, optional): Transferee party index
- `transferor` (int, optional): Transferor party index
- `transfer_target` (int, optional): Transfer target party index
- `original` (int, optional): Original dialog index
- `consultation` (int, optional): Consultation dialog index
- `target_dialog` (int, optional): Target dialog index
- `campaign` (str, optional): Campaign identifier
- `interaction` (str, optional): Interaction identifier
- `skill` (str, optional): Skill identifier
- `duration` (float, optional): Dialog duration
- `meta` (dict, optional): Additional metadata
- `metadata` (Dict[str, Any], optional): Structured metadata
- `transfer` (Dict[str, Any], optional): Transfer-specific information
- `signaling` (Dict[str, Any], optional): Signaling information
- `resolution` (str, optional): Video resolution (e.g., "1920x1080")
- `frame_rate` (float, optional): Video frame rate
- `codec` (str, optional): Video codec
- `bitrate` (int, optional): Video bitrate
- `thumbnail` (str, optional): Base64-encoded thumbnail
- `session_id` (str, optional): Session identifier
- `content_hash` (str, optional): Content hash for external files
- `application` (str, optional): Application identifier
- `message_id` (str, optional): Message identifier

#### Methods

##### `to_dict() -> Dict[str, Any]`
Convert Dialog to dictionary.

##### `add_external_data(url: str, filename: str, mimetype: str) -> None`
Add external data to dialog.

##### `add_inline_data(body: str, filename: str, mimetype: str) -> None`
Add inline data to dialog.

##### `is_external_data() -> bool`
Check if dialog has external data.

##### `is_inline_data() -> bool`
Check if dialog has inline data.

##### `is_text() -> bool`
Check if dialog is text type.

##### `is_recording() -> bool`
Check if dialog is recording type.

##### `is_transfer() -> bool`
Check if dialog is transfer type.

##### `is_incomplete() -> bool`
Check if dialog is incomplete type.

##### `is_audio() -> bool`
Check if dialog has audio content.

##### `is_video(content_type: Optional[str] = None) -> bool`
Check if dialog has video content.

##### `is_email() -> bool`
Check if dialog is email type.

##### `is_image() -> bool`
Check if dialog has image content.

##### `is_pdf() -> bool`
Check if dialog has PDF content.

##### `add_video_data(video_data, filename: Optional[str] = None, mimetype: Optional[str] = None, inline: bool = True, metadata: Optional[dict] = None) -> None`
Add video data to dialog.

##### `extract_video_metadata(video_path: Optional[str] = None) -> dict`
Extract video metadata using FFmpeg.

##### `generate_thumbnail(timestamp: float = 0.0, width: int = 320, height: int = 240, quality: int = 90) -> bytes`
Generate video thumbnail.

##### `add_streaming_video_reference(reference_id: str, mimetype: str, metadata: Optional[dict] = None) -> None`
Add streaming video reference.

##### `add_video_with_optimal_storage(video_data, filename: str, mimetype: Optional[str] = None, size_threshold_mb: int = 10) -> None`
Add video with optimal storage method.

##### `transcode_video(target_format: str, codec: Optional[str] = None, bit_rate: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None) -> None`
Transcode video to different format.

##### `add_image_data(image_path: str, mimetype: Optional[str] = None) -> None`
Add image data from file.

##### `extract_image_metadata(image_data: bytes, mimetype: str) -> None`
Extract image metadata.

##### `generate_thumbnail(max_size: Tuple[int, int] = (200, 200)) -> Optional[str]`
Generate image thumbnail.

##### `is_external_data_changed() -> bool`
Check if external data has changed.

##### `to_inline_data() -> None`
Convert external data to inline data.

##### `set_session_id(session_id: str) -> None`
Set session identifier.

##### `get_session_id() -> Optional[str]`
Get session identifier.

##### `set_content_hash(content_hash: str) -> None`
Set content hash.

##### `get_content_hash() -> Optional[str]`
Get content hash.

##### `calculate_content_hash(algorithm: str = "sha256") -> str`
Calculate content hash.

##### `verify_content_hash(expected_hash: str, algorithm: str = "sha256") -> bool`
Verify content hash.

### CivicAddress Class

Represents civic address information according to GEOPRIV specification.

#### Constructor

```python
CivicAddress(
    country: Optional[str] = None,
    a1: Optional[str] = None,
    a2: Optional[str] = None,
    a3: Optional[str] = None,
    a4: Optional[str] = None,
    a5: Optional[str] = None,
    a6: Optional[str] = None,
    prd: Optional[str] = None,
    pod: Optional[str] = None,
    sts: Optional[str] = None,
    hno: Optional[str] = None,
    hns: Optional[str] = None,
    lmk: Optional[str] = None,
    loc: Optional[str] = None,
    flr: Optional[str] = None,
    nam: Optional[str] = None,
    pc: Optional[str] = None
)
```

**Parameters:**
- `country` (str, optional): Country code (ISO 3166-1 alpha-2)
- `a1` (str, optional): Administrative area 1 (state/province)
- `a2` (str, optional): Administrative area 2 (county/municipality)
- `a3` (str, optional): Administrative area 3 (city/town)
- `a4` (str, optional): Administrative area 4 (neighborhood/district)
- `a5` (str, optional): Administrative area 5 (postal code)
- `a6` (str, optional): Administrative area 6 (building/floor)
- `prd` (str, optional): Premier (department/suite number)
- `pod` (str, optional): Post office box identifier
- `sts` (str, optional): Street name
- `hno` (str, optional): House number
- `hns` (str, optional): House name
- `lmk` (str, optional): Landmark name
- `loc` (str, optional): Location name
- `flr` (str, optional): Floor
- `nam` (str, optional): Name of location
- `pc` (str, optional): Postal code

#### Methods

##### `to_dict() -> Dict[str, Optional[str]]`
Convert CivicAddress to dictionary.

### PartyHistory Class

Represents party history events in a vCon dialog.

#### Constructor

```python
PartyHistory(party: int, event: str, time: datetime)
```

**Parameters:**
- `party` (int): Index of the party
- `event` (str): Event type ("join", "drop", "hold", "unhold", "mute", "unmute")
- `time` (datetime): Time of the event

#### Methods

##### `to_dict() -> Dict[str, Any]`
Convert PartyHistory to dictionary.

### Attachment Class

Represents an attachment in a vCon.

#### Constructor

```python
Attachment(type: str, body: Any, encoding: str = "none")
```

**Parameters:**
- `type` (str): Type of attachment
- `body` (Any): Content of attachment
- `encoding` (str): Encoding format ("base64", "base64url", "none")

#### Methods

##### `to_dict() -> Dict[str, Any]`
Convert Attachment to dictionary.

##### `from_image(image_path: str, type: str = "image") -> 'Attachment'`
Create attachment from image file.

## Constants

### Property Handling Modes

```python
PROPERTY_HANDLING_DEFAULT = "default"  # Keep non-standard properties
PROPERTY_HANDLING_STRICT = "strict"    # Remove non-standard properties
PROPERTY_HANDLING_META = "meta"        # Move non-standard properties to meta
```

### Dialog Types

```python
VALID_TYPES = ["recording", "text", "transfer", "incomplete", "audio", "video"]
```

### Disposition Values

```python
VALID_DISPOSITIONS = [
    "no-answer", "congestion", "failed", "busy", 
    "hung-up", "voicemail-no-message"
]
```

### Party History Events

```python
VALID_EVENTS = ["join", "drop", "hold", "unhold", "mute", "unmute"]
```

### Attachment Encodings

```python
VALID_ENCODINGS = ["base64", "base64url", "none"]
```

### Supported MIME Types

```python
MIME_TYPES = [
    "text/plain",
    "audio/x-wav", "audio/wav", "audio/wave", "audio/mpeg", "audio/mp3",
    "audio/x-mp3", "audio/x-mp4", "audio/ogg", "audio/webm", "audio/x-m4a", "audio/aac",
    "video/x-mp4", "video/ogg", "video/mp4", "video/quicktime", "video/webm",
    "video/x-msvideo", "video/x-matroska", "video/mpeg", "video/x-flv", "video/3gpp", "video/x-m4v",
    "multipart/mixed", "message/rfc822",
    "image/jpeg", "image/tiff", "application/pdf", "application/json"
]
```

## Examples

### Basic vCon Creation

```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime

# Create new vCon
vcon = Vcon.build_new()

# Add parties
caller = Party(tel="+1234567890", name="Alice", role="caller")
agent = Party(tel="+1987654321", name="Bob", role="agent")
vcon.add_party(caller)
vcon.add_party(agent)

# Add dialog
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    originator=0,
    body="Hello, I need help with my account."
)
vcon.add_dialog(dialog)

# Save to file
vcon.save_to_file("conversation.vcon.json")
```

### Loading and Validation

```python
# Load vCon
vcon = Vcon.load("conversation.vcon.json")

# Validate
is_valid, errors = vcon.is_valid()
if not is_valid:
    print("Validation errors:", errors)

# Access data
print(f"UUID: {vcon.uuid}")
print(f"Parties: {len(vcon.parties)}")
print(f"Dialogs: {len(vcon.dialog)}")
```

### Digital Signatures

```python
# Generate key pair
private_key, public_key = Vcon.generate_key_pair()

# Sign vCon
vcon.sign(private_key)

# Verify signature
is_valid = vcon.verify(public_key)
print(f"Signature valid: {is_valid}")
```

### Extensions and Must-Support

```python
# Add extensions
vcon.add_extension("video")
vcon.add_extension("encryption")

# Add must-support
vcon.add_must_support("encryption")

print(f"Extensions: {vcon.get_extensions()}")
print(f"Must support: {vcon.get_must_support()}")
```

### Analysis and Attachments

```python
# Add analysis
vcon.add_analysis(
    type="sentiment",
    dialog=[0, 1],
    vendor="SentimentAnalyzer",
    body={"sentiment": "positive", "confidence": 0.85},
    encoding="json"
)

# Add attachment
vcon.add_attachment(
    type="transcript",
    body="Full conversation transcript...",
    encoding="none"
)

# Add tags
vcon.add_tag("customer_id", "12345")
vcon.add_tag("priority", "high")
```

### Video Content

```python
# Add video dialog
video_dialog = Dialog(
    type="video",
    start=datetime.now(),
    parties=[0, 1],
    mimetype="video/mp4",
    resolution="1920x1080",
    frame_rate=30.0,
    codec="H.264"
)

# Add video data
video_dialog.add_video_data(
    video_data=binary_video_data,
    filename="recording.mp4",
    mimetype="video/mp4",
    inline=True
)

# Extract metadata
metadata = video_dialog.extract_video_metadata()

# Generate thumbnail
thumbnail = video_dialog.generate_thumbnail(timestamp=10.0)

vcon.add_dialog(video_dialog)
```

### Civic Address

```python
from vcon.civic_address import CivicAddress

# Create civic address
address = CivicAddress(
    country="US",
    a1="CA",
    a3="San Francisco",
    sts="Market Street",
    hno="123",
    pc="94102"
)

# Add to party
party = Party(
    name="Jane",
    tel="+1555123456",
    civicaddress=address
)
```

### Party History

```python
from vcon.party import PartyHistory

# Create party history
history = [
    PartyHistory(0, "join", datetime.now()),
    PartyHistory(1, "join", datetime.now()),
    PartyHistory(0, "hold", datetime.now()),
    PartyHistory(0, "unhold", datetime.now()),
    PartyHistory(1, "drop", datetime.now())
]

# Add to dialog
dialog = Dialog(
    type="recording",
    start=datetime.now(),
    parties=[0, 1],
    party_history=history
)
```

### HTTP Operations

```python
# Post vCon to server
response = vcon.post_to_url(
    "https://api.example.com/vcon",
    headers={
        "Authorization": "Bearer your-token",
        "Content-Type": "application/json"
    }
)

if response.status_code == 200:
    print("Successfully posted vCon")
else:
    print(f"Error: {response.status_code}")
```

### Property Handling

```python
# Strict mode - remove non-standard properties
vcon = Vcon.load("file.json", property_handling="strict")

# Meta mode - move non-standard properties to meta
vcon = Vcon.load("file.json", property_handling="meta")

# Default mode - keep all properties
vcon = Vcon.load("file.json", property_handling="default")
```

This API reference covers all the main functionality of the vCon library. For more detailed examples and use cases, see the [Quickstart Guide](QUICKSTART.md) and the [samples directory](samples/).
