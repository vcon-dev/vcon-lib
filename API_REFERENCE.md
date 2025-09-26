# vCon Library API Reference

Complete API documentation for the vCon library - a Python implementation of the latest vCon specification for Virtual Conversation objects.

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
- [Extensions](#extensions)
  - [Extension Framework](#extension-framework)
  - [Lawful Basis Extension](#lawful-basis-extension)
  - [WTF Extension](#wtf-extension)
- [Constants](#constants)
- [Examples](#examples)

## Overview

The vCon library provides a complete Python implementation of the latest vCon specification for representing virtual conversations. It supports all features including parties, dialogs, attachments, analysis, digital signatures, extensibility, and advanced extensions for lawful basis management and standardized transcription formats.

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
Vcon(vcon_dict: Dict[str, Any] = None, property_handling: str = "default")
```

**Parameters:**
- `vcon_dict` (Dict[str, Any], optional): Dictionary representing a vCon. Defaults to empty dict.
- `property_handling` (str): How to handle non-standard properties:
  - `"default"`: Keep non-standard properties (default)
  - `"strict"`: Remove non-standard properties
  - `"meta"`: Move non-standard properties to meta object

#### Class Methods

##### `build_new() -> Vcon`
Create a new vCon object with default values.

```python
vcon = Vcon.build_new()
```

##### `build_from_json(json_str: str, property_handling: str = "default") -> Vcon`
Create a vCon object from JSON string.

```python
vcon = Vcon.build_from_json('{"uuid": "123", "created_at": "2024-01-01T00:00:00Z"}')
```

##### `load(file_path_or_url: str, property_handling: str = "default") -> Vcon`

Load a vCon from file or URL.

```python
# From file
vcon = Vcon.load("conversation.vcon.json")

# From URL
vcon = Vcon.load("https://example.com/conversation.vcon.json")
```

##### `load_from_file(file_path: str, property_handling: str = "default") -> Vcon`
Load a vCon from a local file.

##### `load_from_url(url: str, property_handling: str = "default") -> Vcon`

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

##### Extension-Specific Methods

###### `add_lawful_basis_attachment(lawful_basis: str, expiration: str, purpose_grants: list, party_index: Optional[int] = None, dialog_index: Optional[int] = None, **kwargs) -> None`
Add a lawful basis attachment to the vCon.

```python
vcon.add_lawful_basis_attachment(
    lawful_basis="consent",
    expiration="2026-01-01T00:00:00Z",
    purpose_grants=[
        {"purpose": "recording", "granted": True, "granted_at": "2025-01-01T00:00:00Z"}
    ],
    party_index=0
)
```

###### `add_wtf_transcription_attachment(transcript: Dict[str, Any], segments: List[Dict[str, Any]], metadata: Dict[str, Any], party_index: Optional[int] = None, dialog_index: Optional[int] = None, **kwargs) -> None`
Add a WTF transcription attachment to the vCon.

```python
vcon.add_wtf_transcription_attachment(
    transcript={"text": "Hello world", "language": "en", "duration": 2.0, "confidence": 0.95},
    segments=[{"id": 0, "start": 0.0, "end": 2.0, "text": "Hello world", "confidence": 0.95}],
    metadata={"created_at": "2025-01-01T00:00:00Z", "provider": "whisper", "model": "whisper-1"}
)
```

###### `find_lawful_basis_attachments(party_index: Optional[int] = None) -> List[Dict[str, Any]]`
Find lawful basis attachments in the vCon.

```python
attachments = vcon.find_lawful_basis_attachments(party_index=0)
```

###### `find_wtf_attachments(party_index: Optional[int] = None) -> List[Dict[str, Any]]`
Find WTF transcription attachments in the vCon.

```python
attachments = vcon.find_wtf_attachments(party_index=0)
```

###### `check_lawful_basis_permission(purpose: str, party_index: Optional[int] = None) -> bool`
Check if permission is granted for a specific purpose.

```python
has_permission = vcon.check_lawful_basis_permission("recording", party_index=0)
```

###### `validate_extensions() -> Dict[str, Any]`
Validate all extensions in the vCon.

```python
results = vcon.validate_extensions()
```

###### `process_extensions() -> Dict[str, Any]`
Process all extensions in the vCon.

```python
results = vcon.process_extensions()
```

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

##### `vcon -> Optional[str]`
Get the vCon version (optional field).

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

## Extensions

The vCon library includes a comprehensive extension framework that allows for standardized implementation of additional functionality. Two major extensions are currently implemented: the Lawful Basis extension for privacy compliance and the WTF (World Transcription Format) extension for standardized transcription data.

### Extension Framework

The extension framework provides a standardized way to add new functionality to vCon objects while maintaining compatibility and validation.

#### Core Extension Classes

##### `ExtensionType`
Enumeration of extension types:
- `COMPATIBLE`: Safe to ignore, no breaking changes
- `INCOMPATIBLE`: Must be supported, breaking changes  
- `EXPERIMENTAL`: Development/testing only

##### `ExtensionValidator`
Abstract base class for extension validation logic.

##### `ExtensionProcessor`
Abstract base class for extension processing logic.

##### `ExtensionRegistry`
Central registry for managing extensions.

```python
from vcon.extensions import get_extension_registry

# Get the global registry
registry = get_extension_registry()

# List all registered extensions
extensions = registry.list_extensions()
```

### Lawful Basis Extension

The Lawful Basis extension provides comprehensive support for privacy compliance and consent management according to GDPR and other privacy regulations.

#### Key Features

- **Multiple Lawful Basis Types**: consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests
- **Purpose-Specific Permissions**: Granular permission grants with conditions
- **Cryptographic Proof Mechanisms**: Verbal confirmation, signed documents, cryptographic signatures, external systems
- **Temporal Validity**: Expiration dates and status intervals
- **Content Integrity**: Hash validation and canonicalization
- **External Registry Integration**: SCITT (Supply Chain Integrity, Transparency, and Trust) support

#### Core Classes

##### `LawfulBasisAttachment`
Main class representing a lawful basis attachment.

```python
from vcon.extensions.lawful_basis import LawfulBasisAttachment, LawfulBasisType, PurposeGrant
from datetime import datetime, timezone, timedelta

# Create purpose grants
purpose_grants = [
    PurposeGrant(
        purpose="recording",
        granted=True,
        granted_at=datetime.now(timezone.utc).isoformat()
    ),
    PurposeGrant(
        purpose="analysis",
        granted=True,
        granted_at=datetime.now(timezone.utc).isoformat(),
        conditions=["anonymized_data_only"]
    )
]

# Create lawful basis attachment
attachment = LawfulBasisAttachment(
    lawful_basis=LawfulBasisType.CONSENT,
    expiration=(datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
    purpose_grants=purpose_grants
)
```

##### `PurposeGrant`
Represents a purpose-specific permission grant.

```python
grant = PurposeGrant(
    purpose="recording",
    granted=True,
    granted_at=datetime.now(timezone.utc).isoformat(),
    conditions=["anonymized_data_only"]
)
```

##### `ContentHash`
Represents content integrity information.

```python
from vcon.extensions.lawful_basis import ContentHash, HashAlgorithm, CanonicalizationMethod

content_hash = ContentHash(
    algorithm=HashAlgorithm.SHA_256,
    canonicalization=CanonicalizationMethod.JCS,
    value="computed_hash_value"
)
```

##### `ProofMechanism`
Represents a proof mechanism for lawful basis.

```python
from vcon.extensions.lawful_basis import ProofMechanism, ProofType

proof = ProofMechanism(
    proof_type=ProofType.VERBAL_CONFIRMATION,
    timestamp=datetime.now(timezone.utc).isoformat(),
    proof_data={
        "dialog_reference": 0,
        "confirmation_text": "I consent to recording"
    }
)
```

#### Validation and Processing

##### `LawfulBasisValidator`
Validates lawful basis attachments and extension usage.

```python
from vcon.extensions.lawful_basis import LawfulBasisValidator

validator = LawfulBasisValidator()
result = validator.validate_attachment(attachment_dict)
```

##### `LawfulBasisProcessor`
Processes lawful basis attachments and evaluates permissions.

```python
from vcon.extensions.lawful_basis import LawfulBasisProcessor

processor = LawfulBasisProcessor()
result = processor.check_permission(vcon_dict, "recording", party_index=0)
```

#### Registry Integration

##### `SCITTRegistryClient`
Client for SCITT (Supply Chain Integrity, Transparency, and Trust) registries.

```python
from vcon.extensions.lawful_basis import SCITTRegistryClient

client = SCITTRegistryClient("https://registry.example.com", auth_token="token")
receipt_id = client.submit_attestation(lawful_basis_attachment)
```

### WTF Extension

The WTF (World Transcription Format) extension provides standardized representation of speech-to-text transcription data from multiple providers.

#### Key Features

- **Multi-Provider Support**: Whisper, Deepgram, AssemblyAI, Google, Amazon, Azure, and more
- **Standardized Format**: Hierarchical structure with transcripts, segments, words, and speakers
- **Quality Metrics**: Audio quality assessment and confidence scoring
- **Export Capabilities**: SRT and WebVTT subtitle formats
- **Provider Adapters**: Automatic conversion from provider-specific formats
- **Analysis Tools**: Keyword extraction, confidence analysis, and transcription comparison

#### Core Classes

##### `WTFAttachment`
Main class representing a WTF transcription attachment.

```python
from vcon.extensions.wtf import WTFAttachment, Transcript, Segment, Metadata
from datetime import datetime, timezone

# Create transcript
transcript = Transcript(
    text="Hello world",
    language="en",
    duration=2.0,
    confidence=0.95
)

# Create segments
segments = [
    Segment(
        id=0,
        start=0.0,
        end=2.0,
        text="Hello world",
        confidence=0.95
    )
]

# Create metadata
metadata = Metadata(
    created_at=datetime.now(timezone.utc).isoformat(),
    processed_at=datetime.now(timezone.utc).isoformat(),
    provider="whisper",
    model="whisper-1"
)

# Create WTF attachment
attachment = WTFAttachment(
    transcript=transcript,
    segments=segments,
    metadata=metadata
)
```

##### `Transcript`
Represents high-level transcript information.

```python
transcript = Transcript(
    text="Hello world",
    language="en",
    duration=2.0,
    confidence=0.95
)
```

##### `Segment`
Represents a logical chunk of transcribed content.

```python
segment = Segment(
    id=0,
    start=0.0,
    end=2.0,
    text="Hello world",
    confidence=0.95,
    speaker=0
)
```

##### `Word`
Represents a single word in the transcription.

```python
word = Word(
    id=0,
    start=0.0,
    end=1.0,
    text="Hello",
    confidence=0.95,
    speaker=0
)
```

##### `Speaker`
Represents speaker information for diarization.

```python
speaker = Speaker(
    id=0,
    label="Speaker 1",
    segments=[0, 1, 2],
    total_time=10.5,
    confidence=0.9
)
```

##### `Quality`
Represents quality metrics for the transcription.

```python
quality = Quality(
    audio_quality="high",
    background_noise=0.1,
    multiple_speakers=True,
    overlapping_speech=False,
    silence_ratio=0.2,
    average_confidence=0.95,
    low_confidence_words=5,
    processing_warnings=[]
)
```

#### Provider Adapters

##### `WhisperAdapter`
Converts Whisper transcription data to WTF format.

```python
from vcon.extensions.wtf import WhisperAdapter

adapter = WhisperAdapter()
wtf_attachment = adapter.convert(whisper_data)
```

##### `DeepgramAdapter`
Converts Deepgram transcription data to WTF format.

```python
from vcon.extensions.wtf import DeepgramAdapter

adapter = DeepgramAdapter()
wtf_attachment = adapter.convert(deepgram_data)
```

##### `AssemblyAIAdapter`
Converts AssemblyAI transcription data to WTF format.

```python
from vcon.extensions.wtf import AssemblyAIAdapter

adapter = AssemblyAIAdapter()
wtf_attachment = adapter.convert(assemblyai_data)
```

#### Export Capabilities

##### SRT Export
Export transcription to SRT subtitle format.

```python
srt_content = attachment.export_to_srt()
```

##### WebVTT Export
Export transcription to WebVTT format.

```python
vtt_content = attachment.export_to_vtt()
```

#### Analysis Tools

##### Keyword Extraction
Extract keywords from high-confidence words.

```python
keywords = attachment.extract_keywords(min_confidence=0.8)
```

##### Low Confidence Detection
Find segments with confidence below threshold.

```python
low_confidence_segments = attachment.find_low_confidence_segments(threshold=0.5)
```

##### Speaking Time Calculation
Calculate speaking time for each speaker.

```python
speaking_times = attachment.get_speaking_time()
```

#### Validation and Processing

##### `WTFValidator`
Validates WTF transcription attachments.

```python
from vcon.extensions.wtf import WTFValidator

validator = WTFValidator()
result = validator.validate_attachment(attachment_dict)
```

##### `WTFProcessor`
Processes WTF transcription attachments and provides analysis.

```python
from vcon.extensions.wtf import WTFProcessor

processor = WTFProcessor()
analysis = processor.analyze_transcription(attachment)
```

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

### Extension Types

```python
from vcon.extensions.base import ExtensionType

ExtensionType.COMPATIBLE     # Safe to ignore, no breaking changes
ExtensionType.INCOMPATIBLE   # Must be supported, breaking changes
ExtensionType.EXPERIMENTAL   # Development/testing only
```

### Lawful Basis Types

```python
from vcon.extensions.lawful_basis import LawfulBasisType

LawfulBasisType.CONSENT              # Explicit consent
LawfulBasisType.CONTRACT             # Contractual necessity
LawfulBasisType.LEGAL_OBLIGATION     # Legal obligation
LawfulBasisType.VITAL_INTERESTS      # Vital interests
LawfulBasisType.PUBLIC_TASK          # Public task
LawfulBasisType.LEGITIMATE_INTERESTS # Legitimate interests
```

### Proof Types

```python
from vcon.extensions.lawful_basis import ProofType

ProofType.VERBAL_CONFIRMATION        # Verbal confirmation
ProofType.SIGNED_DOCUMENT           # Signed document
ProofType.CRYPTOGRAPHIC_SIGNATURE   # Cryptographic signature
ProofType.EXTERNAL_SYSTEM           # External system attestation
```

### Hash Algorithms

```python
from vcon.extensions.lawful_basis import HashAlgorithm

HashAlgorithm.SHA_256    # SHA-256
HashAlgorithm.SHA_384    # SHA-384
HashAlgorithm.SHA_512    # SHA-512
```

### Canonicalization Methods

```python
from vcon.extensions.lawful_basis import CanonicalizationMethod

CanonicalizationMethod.JCS    # JSON Canonicalization Scheme
```

### WTF Provider Adapters

```python
from vcon.extensions.wtf import (
    WhisperAdapter,      # OpenAI Whisper
    DeepgramAdapter,     # Deepgram
    AssemblyAIAdapter,   # AssemblyAI
    ProviderAdapter      # Base adapter class
)
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

### Lawful Basis Extension

```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime, timezone, timedelta

# Create vCon with parties and dialog
vcon = Vcon.build_new()
caller = Party(tel="+1234567890", name="Alice", role="caller")
agent = Party(tel="+1987654321", name="Bob", role="agent")
vcon.add_party(caller)
vcon.add_party(agent)

# Add dialog
dialog = Dialog(
    type="recording",
    start=datetime.now(timezone.utc),
    parties=[0, 1],
    mimetype="audio/mp3"
)
vcon.add_dialog(dialog)

# Add lawful basis attachment
vcon.add_lawful_basis_attachment(
    lawful_basis="consent",
    expiration=(datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
    purpose_grants=[
        {
            "purpose": "recording",
            "granted": True,
            "granted_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "purpose": "analysis",
            "granted": True,
            "granted_at": datetime.now(timezone.utc).isoformat(),
            "conditions": ["anonymized_data_only"]
        }
    ],
    party_index=0,
    dialog_index=0
)

# Check permissions
recording_permission = vcon.check_lawful_basis_permission("recording", party_index=0)
marketing_permission = vcon.check_lawful_basis_permission("marketing", party_index=0)

print(f"Recording permission: {recording_permission}")
print(f"Marketing permission: {marketing_permission}")

# Find lawful basis attachments
attachments = vcon.find_lawful_basis_attachments(party_index=0)
print(f"Found {len(attachments)} lawful basis attachments")
```

### WTF Extension

```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime, timezone

# Create vCon with parties and dialog
vcon = Vcon.build_new()
caller = Party(tel="+1234567890", name="Alice", role="caller")
agent = Party(tel="+1987654321", name="Bob", role="agent")
vcon.add_party(caller)
vcon.add_party(agent)

# Add dialog
dialog = Dialog(
    type="recording",
    start=datetime.now(timezone.utc),
    parties=[0, 1],
    mimetype="audio/mp3"
)
vcon.add_dialog(dialog)

# Add WTF transcription attachment
vcon.add_wtf_transcription_attachment(
    transcript={
        "text": "Hello, this is a test transcription.",
        "language": "en",
        "duration": 3.5,
        "confidence": 0.95
    },
    segments=[
        {
            "id": 0,
            "start": 0.0,
            "end": 1.5,
            "text": "Hello, this is",
            "confidence": 0.95,
            "speaker": 0
        },
        {
            "id": 1,
            "start": 1.5,
            "end": 3.5,
            "text": "a test transcription.",
            "confidence": 0.94,
            "speaker": 0
        }
    ],
    metadata={
        "created_at": datetime.now(timezone.utc).isoformat(),
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "provider": "whisper",
        "model": "whisper-1",
        "audio_quality": "high",
        "background_noise": 0.1
    },
    party_index=0,
    dialog_index=0
)

# Find WTF attachments
attachments = vcon.find_wtf_attachments(party_index=0)
print(f"Found {len(attachments)} WTF attachments")

# Export to SRT format
if attachments:
    from vcon.extensions.wtf import WTFAttachment
    wtf_attachment = WTFAttachment.from_dict(attachments[0]["body"])
    srt_content = wtf_attachment.export_to_srt()
    print("SRT Export:")
    print(srt_content)
```

### Extension Validation and Processing

```python
# Validate all extensions
validation_results = vcon.validate_extensions()
print("Extension validation results:")
for extension, result in validation_results.items():
    if extension != "attachments":
        status = "✓ Valid" if result["is_valid"] else "✗ Invalid"
        print(f"  {extension}: {status}")
        if result["errors"]:
            for error in result["errors"]:
                print(f"    Error: {error}")
        if result["warnings"]:
            for warning in result["warnings"]:
                print(f"    Warning: {warning}")

# Process all extensions
processing_results = vcon.process_extensions()
print("Extension processing completed")
```

### Provider Data Conversion

```python
from vcon.extensions.wtf import WhisperAdapter, DeepgramAdapter

# Convert Whisper data to WTF format
whisper_data = {
    "text": "Hello world from Whisper",
    "segments": [
        {
            "start": 0.0,
            "end": 2.0,
            "text": "Hello world from Whisper"
        }
    ]
}

whisper_adapter = WhisperAdapter()
wtf_attachment = whisper_adapter.convert(whisper_data)

# Add to vCon
vcon.add_wtf_transcription_attachment(
    transcript=wtf_attachment.transcript.to_dict(),
    segments=[segment.to_dict() for segment in wtf_attachment.segments],
    metadata=wtf_attachment.metadata.to_dict()
)
```

### Complete Extension Workflow

```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime, timezone, timedelta

# Create comprehensive vCon with extensions
vcon = Vcon.build_new()

# Add parties
caller = Party(tel="+1234567890", name="Alice", role="caller")
agent = Party(tel="+1987654321", name="Bob", role="agent")
vcon.add_party(caller)
vcon.add_party(agent)

# Add dialog
dialog = Dialog(
    type="recording",
    start=datetime.now(timezone.utc),
    parties=[0, 1],
    mimetype="audio/mp3"
)
vcon.add_dialog(dialog)

# Add lawful basis for consent
vcon.add_lawful_basis_attachment(
    lawful_basis="consent",
    expiration=(datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
    purpose_grants=[
        {
            "purpose": "recording",
            "granted": True,
            "granted_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "purpose": "transcription",
            "granted": True,
            "granted_at": datetime.now(timezone.utc).isoformat()
        }
    ],
    party_index=0
)

# Add transcription
vcon.add_wtf_transcription_attachment(
    transcript={
        "text": "Hello, I need help with my account.",
        "language": "en",
        "duration": 4.2,
        "confidence": 0.92
    },
    segments=[
        {
            "id": 0,
            "start": 0.0,
            "end": 4.2,
            "text": "Hello, I need help with my account.",
            "confidence": 0.92,
            "speaker": 0
        }
    ],
    metadata={
        "created_at": datetime.now(timezone.utc).isoformat(),
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "provider": "whisper",
        "model": "whisper-1"
    },
    party_index=0,
    dialog_index=0
)

# Validate and process
validation_results = vcon.validate_extensions()
processing_results = vcon.process_extensions()

# Check permissions
can_record = vcon.check_lawful_basis_permission("recording", party_index=0)
can_transcribe = vcon.check_lawful_basis_permission("transcription", party_index=0)

print(f"Can record: {can_record}")
print(f"Can transcribe: {can_transcribe}")

# Save vCon
vcon.save_to_file("conversation_with_extensions.vcon.json")
print("Saved vCon with extensions")
```

This API reference covers all the main functionality of the vCon library, including the new extension framework. For more detailed examples and use cases, see the [Quickstart Guide](QUICKSTART.md) and the [samples directory](samples/).
