# vCon Library Guide for LLMs

This guide provides a comprehensive overview of the vCon (Virtual Conversation) Python library, designed specifically for Large Language Models (LLMs) that need to generate or modify code using this library.

## Overview

The vCon library is a Python implementation of the vCon 0.3.0 specification for structuring, managing, and manipulating conversation data in a standardized format. It enables the creation, validation, and manipulation of digital representations of conversations with rich metadata, supporting all modern conversation features including multimedia content, security, and extensibility.

### Key Concepts

- **vCon Container**: The primary object that holds all conversation data
- **Parties**: Participants in a conversation (callers, agents, bots) with contact information
- **Dialogs**: Individual messages or segments of the conversation (text, audio, video, etc.)
- **Attachments**: Additional files or data associated with the conversation
- **Analysis**: Results from processing the conversation (sentiment analysis, transcription, etc.)
- **Extensions**: Optional features that extend the base vCon functionality
  - **Lawful Basis Extension**: GDPR-compliant consent management and privacy compliance
  - **WTF Extension**: World Transcription Format for standardized speech-to-text data
- **Digital Signatures**: Cryptographic verification of vCon integrity
- **Civic Addresses**: Location information for parties using GEOPRIV standard
- **Party History**: Event tracking for multi-party conversations

## Installation

```bash
# Basic installation
pip install vcon

# With image processing support (Pillow, PyPDF)
pip install vcon[image]

# From source
git clone https://github.com/vcon-dev/vcon-lib.git
cd vcon-lib
pip install -e .
```

## Requirements

- Python 3.12+
- Core dependencies: authlib, uuid6, requests, pydash, python-dateutil
- Optional: mutagen (audio metadata), ffmpeg (video processing), Pillow (image processing), PyPDF (PDF processing)

## Core Classes and Usage Patterns

### 1. Vcon Class

The main container for all conversation data.

#### Creating a vCon

```python
from vcon import Vcon

# Create a new empty vCon
vcon = Vcon.build_new()

# Create from existing JSON
vcon = Vcon.build_from_json(json_string)

# Load from file
vcon = Vcon.load_from_file("conversation.json")

# Load from URL
vcon = Vcon.load_from_url("https://example.com/conversation.json")

# Generic load (detects if path or URL)
vcon = Vcon.load("conversation.json")  # or URL
```

#### Saving and Exporting

```python
# Save to file
vcon.save_to_file("conversation.json")

# Convert to JSON string
json_str = vcon.to_json()  # or vcon.dumps()

# Convert to dictionary
vcon_dict = vcon.to_dict()

# Post to URL with optional headers
response = vcon.post_to_url(
    'https://api.example.com/vcons',
    headers={'x-api-token': 'your-token-here'}
)
```

#### Properties

```python
# Access properties
uuid = vcon.uuid
version = vcon.vcon
created_at = vcon.created_at
updated_at = vcon.updated_at
parties_list = vcon.parties
dialog_list = vcon.dialog
attachments_list = vcon.attachments
analysis_list = vcon.analysis
extensions_list = vcon.extensions
must_support_list = vcon.must_support
```

### 2. Party Class

Represents a participant in the conversation.

```python
from vcon.party import Party

# Create a party
caller = Party(
    tel="+1234567890",
    name="Alice Smith",
    role="caller",
    mailto="alice@example.com"
)

# Add to vCon
vcon.add_party(caller)

# Find a party by an attribute
party_index = vcon.find_party_index("name", "Alice Smith")  # Returns index (0-based)
```

#### Party Attributes

**Core Contact Information:**
- `tel`: Telephone number (e.g., "+1234567890")
- `name`: Display name (e.g., "Alice Smith")
- `role`: Role in conversation ("caller", "agent", "bot", etc.)
- `mailto`: Email address (e.g., "alice@example.com")

**Advanced Contact Methods (vCon 0.3.0):**
- `sip`: SIP URI for VoIP communication (e.g., "sip:alice@example.com")
- `did`: Decentralized Identifier for blockchain-based identity
- `jCard`: vCard format contact information (RFC 7095)
- `timezone`: Party's timezone (e.g., "America/New_York")

**Location and Validation:**
- `civicaddress`: Civic address using CivicAddress class (GEOPRIV format)
- `gmlpos`: GML position coordinates
- `validation`: Validation status
- `stir`: STIR verification for secure telephony

**Metadata:**
- `uuid`: Unique identifier for the party
- `contact_list`: Reference to contact list
- `meta`: Additional metadata dictionary
- Custom attributes can be added via kwargs

### 3. Dialog Class

Represents a message or segment in the conversation.

```python
from vcon.dialog import Dialog
from datetime import datetime, timezone

# Create a text dialog
text_dialog = Dialog(
    type="text",
    start=datetime.now(timezone.utc).isoformat(),
    parties=[0, 1],  # Indices of parties involved
    originator=0,    # Index of the party that sent the message
    mimetype="text/plain",
    body="Hello, I need help with my account."
)

# Add to vCon
vcon.add_dialog(text_dialog)

# Create an audio dialog
audio_dialog = Dialog(
    type="audio",
    start=datetime.now(timezone.utc).isoformat(),
    parties=[0, 1],
    originator=0,
    mimetype="audio/mp3",
    body=base64_encoded_audio,
    encoding="base64",
    filename="recording.mp3"
)

vcon.add_dialog(audio_dialog)

# Find a dialog by property
found_dialog = vcon.find_dialog("type", "text")
```

#### Special Dialog Types

```python
# Add a transfer dialog
vcon.add_transfer_dialog(
    start=datetime.now(timezone.utc).isoformat(),
    transfer_data={
        "reason": "Call forwarded",
        "from": "+1234567890",
        "to": "+1987654321"
    },
    parties=[0, 1]
)

# Add an incomplete dialog (for failed conversations)
vcon.add_incomplete_dialog(
    start=datetime.now(timezone.utc).isoformat(),
    disposition="NO_ANSWER",
    details={"ringDuration": 45000},
    parties=[0, 1]
)
```

#### Dialog Type Methods

```python
# Check dialog type
is_text = dialog.is_text()
is_recording = dialog.is_recording()
is_transfer = dialog.is_transfer()
is_incomplete = dialog.is_incomplete()
is_audio = dialog.is_audio()
is_video = dialog.is_video()
is_email = dialog.is_email()
```

#### Dialog Types and MIME Types

**Valid Dialog Types:**
- `"text"`: Text-based communication (chat, SMS, email)
- `"recording"`: Audio/video recording
- `"transfer"`: Call transfer operation
- `"incomplete"`: Failed or incomplete conversation setup
- `"audio"`: Audio content
- `"video"`: Video content

**Supported MIME Types:**

**Text:**
- `text/plain`

**Audio:**
- `audio/x-wav`, `audio/wav`, `audio/wave`
- `audio/mpeg`, `audio/mp3`, `audio/x-mp3`
- `audio/x-mp4`, `audio/ogg`, `audio/webm`
- `audio/x-m4a`, `audio/aac`

**Video:**
- `video/x-mp4`, `video/mp4`, `video/ogg`
- `video/quicktime`, `video/webm`
- `video/x-msvideo`, `video/x-matroska`
- `video/mpeg`, `video/x-flv`, `video/3gpp`, `video/x-m4v`

**Other:**
- `multipart/mixed`
- `message/rfc822` (for email)
- `application/json` (for signaling data)
- `image/jpeg`, `image/tiff`, `application/pdf`

### 4. Working with Tags

Tags are key-value pairs for simple metadata.

```python
# Add tags
vcon.add_tag("customer_id", "12345")
vcon.add_tag("interaction_id", "INT-001")

# Get tag value
value = vcon.get_tag("customer_id")  # Returns "12345"

# Get all tags
all_tags = vcon.tags  # Returns the tags attachment dictionary
```

### 5. Working with Attachments

Attachments are arbitrary data associated with the conversation.

```python
# Add an attachment
vcon.add_attachment(
    type="transcript",
    body="Conversation transcript content...",
    encoding="none"
)

# Add a base64-encoded attachment
vcon.add_attachment(
    type="recording",
    body=base64_encoded_content,
    encoding="base64url"
)

# Find an attachment
attachment = vcon.find_attachment_by_type("transcript")
```

### 6. Working with Analysis

Analysis entries represent insights derived from dialog.

```python
# Add analysis
vcon.add_analysis(
    type="sentiment",
    dialog=[0],  # Index or indices of dialogs analyzed
    vendor="AnalysisCompany",
    body={"sentiment": "positive", "score": 0.8},
    encoding="json"
)

# Find analysis
analysis = vcon.find_analysis_by_type("sentiment")
```

### 7. Extensions and Must-Support (vCon 0.3.0)

Extensions allow vCons to declare optional features they use, while must-support indicates required features.

```python
# Add extensions used in this vCon
vcon.add_extension("video")
vcon.add_extension("encryption")
vcon.add_extension("sentiment_analysis")

# Add extensions that must be supported by consumers
vcon.add_must_support("encryption")
vcon.add_must_support("video")

# Get extensions
extensions = vcon.get_extensions()  # ['video', 'encryption', 'sentiment_analysis']
must_support = vcon.get_must_support()  # ['encryption', 'video']

# Remove extensions
vcon.remove_extension("sentiment_analysis")
vcon.remove_must_support("video")
```

### 7.1. Lawful Basis Extension

The Lawful Basis extension provides comprehensive support for privacy compliance and consent management according to GDPR and other privacy regulations.

#### Key Features
- **Multiple Lawful Basis Types**: consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests
- **Purpose-Specific Permissions**: Granular permission grants with conditions
- **Cryptographic Proof Mechanisms**: Verbal confirmation, signed documents, cryptographic signatures, external systems
- **Temporal Validity**: Expiration dates and status intervals
- **Content Integrity**: Hash validation and canonicalization
- **External Registry Integration**: SCITT (Supply Chain Integrity, Transparency, and Trust) support

#### Adding Lawful Basis Attachments

```python
from datetime import datetime, timezone, timedelta

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

# Add extension to vCon
vcon.add_extension("lawful_basis")
```

#### Checking Permissions

```python
# Check if permission is granted for a specific purpose
recording_permission = vcon.check_lawful_basis_permission("recording", party_index=0)
marketing_permission = vcon.check_lawful_basis_permission("marketing", party_index=0)

print(f"Recording permission: {recording_permission}")
print(f"Marketing permission: {marketing_permission}")
```

#### Finding Lawful Basis Attachments

```python
# Find all lawful basis attachments
attachments = vcon.find_lawful_basis_attachments()

# Find attachments for a specific party
party_attachments = vcon.find_lawful_basis_attachments(party_index=0)
```

#### Advanced Lawful Basis Features

```python
from vcon.extensions.lawful_basis import (
    LawfulBasisAttachment, 
    PurposeGrant, 
    ContentHash,
    ProofMechanism,
    LawfulBasisType,
    ProofType,
    HashAlgorithm
)

# Create purpose grants with conditions
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
        conditions=["anonymized_data_only", "retention_30_days"]
    )
]

# Create content hash for integrity
content_hash = ContentHash(
    algorithm=HashAlgorithm.SHA_256,
    canonicalization="JCS",
    value="computed_hash_value"
)

# Create proof mechanism
proof = ProofMechanism(
    proof_type=ProofType.VERBAL_CONFIRMATION,
    timestamp=datetime.now(timezone.utc).isoformat(),
    proof_data={
        "dialog_reference": 0,
        "confirmation_text": "I consent to recording"
    }
)

# Create comprehensive lawful basis attachment
attachment = LawfulBasisAttachment(
    lawful_basis=LawfulBasisType.CONSENT,
    expiration=(datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
    purpose_grants=purpose_grants,
    content_hash=content_hash,
    proof_mechanisms=[proof]
)
```

### 7.2. WTF (World Transcription Format) Extension

The WTF extension provides standardized representation of speech-to-text transcription data from multiple providers.

#### Key Features
- **Multi-Provider Support**: Whisper, Deepgram, AssemblyAI, Google, Amazon, Azure, and more
- **Standardized Format**: Hierarchical structure with transcripts, segments, words, and speakers
- **Quality Metrics**: Audio quality assessment and confidence scoring
- **Export Capabilities**: SRT and WebVTT subtitle formats
- **Provider Adapters**: Automatic conversion from provider-specific formats
- **Analysis Tools**: Keyword extraction, confidence analysis, and transcription comparison

#### Adding WTF Transcription Attachments

```python
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

# Add extension to vCon
vcon.add_extension("wtf_transcription")
```

#### Finding WTF Attachments

```python
# Find all WTF attachments
attachments = vcon.find_wtf_attachments()

# Find attachments for a specific party
party_attachments = vcon.find_wtf_attachments(party_index=0)
```

#### Exporting Transcriptions

```python
# Find WTF attachments and export to SRT
attachments = vcon.find_wtf_attachments(party_index=0)
if attachments:
    from vcon.extensions.wtf import WTFAttachment
    wtf_attachment = WTFAttachment.from_dict(attachments[0]["body"])
    
    # Export to SRT format
    srt_content = wtf_attachment.export_to_srt()
    print("SRT Export:")
    print(srt_content)
    
    # Export to WebVTT format
    vtt_content = wtf_attachment.export_to_vtt()
    print("WebVTT Export:")
    print(vtt_content)
```

#### Provider Data Conversion

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

#### Advanced WTF Features

```python
from vcon.extensions.wtf import (
    WTFAttachment, 
    Transcript, 
    Segment, 
    Word, 
    Speaker,
    Quality,
    Metadata
)

# Create detailed transcript
transcript = Transcript(
    text="Hello world",
    language="en",
    duration=2.0,
    confidence=0.95
)

# Create segments with words
segments = [
    Segment(
        id=0,
        start=0.0,
        end=2.0,
        text="Hello world",
        confidence=0.95,
        speaker=0,
        words=[
            Word(id=0, start=0.0, end=1.0, text="Hello", confidence=0.95, speaker=0),
            Word(id=1, start=1.0, end=2.0, text="world", confidence=0.95, speaker=0)
        ]
    )
]

# Create speaker information
speakers = [
    Speaker(
        id=0,
        label="Speaker 1",
        segments=[0],
        total_time=2.0,
        confidence=0.9
    )
]

# Create quality metrics
quality = Quality(
    audio_quality="high",
    background_noise=0.1,
    multiple_speakers=False,
    overlapping_speech=False,
    silence_ratio=0.2,
    average_confidence=0.95,
    low_confidence_words=0,
    processing_warnings=[]
)

# Create metadata
metadata = Metadata(
    created_at=datetime.now(timezone.utc).isoformat(),
    processed_at=datetime.now(timezone.utc).isoformat(),
    provider="whisper",
    model="whisper-1",
    audio_quality="high",
    background_noise=0.1
)

# Create comprehensive WTF attachment
attachment = WTFAttachment(
    transcript=transcript,
    segments=segments,
    metadata=metadata,
    words=[word for segment in segments for word in segment.words],
    speakers=speakers,
    quality=quality
)
```

#### Analysis Tools

```python
# Extract keywords from high-confidence words
keywords = attachment.extract_keywords(min_confidence=0.8)

# Find segments with low confidence
low_confidence_segments = attachment.find_low_confidence_segments(threshold=0.5)

# Calculate speaking time for each speaker
speaking_times = attachment.get_speaking_time()
```

### 7.3. Extension Validation and Processing

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

### 8. Civic Address Support (vCon 0.3.0)

Civic addresses provide location information for parties using the GEOPRIV standard.

```python
from vcon.civic_address import CivicAddress

# Create civic address
address = CivicAddress(
    country="US",
    a1="CA",  # State
    a3="San Francisco",  # City
    sts="Market Street",  # Street
    hno="123",  # House number
    pc="94102"  # Postal code
)

# Add to party
party = Party(
    name="Jane Doe",
    tel="+1555123456",
    civicaddress=address
)

# Convert to dictionary
address_dict = address.to_dict()
```

### 9. Party History Events (vCon 0.3.0)

Track when parties join, leave, or change state during conversations.

```python
from vcon.party import PartyHistory
from datetime import datetime

# Create party history events
history = [
    PartyHistory(0, "join", datetime.now()),    # Party 0 joins
    PartyHistory(1, "join", datetime.now()),    # Party 1 joins
    PartyHistory(0, "hold", datetime.now()),    # Party 0 on hold
    PartyHistory(0, "unhold", datetime.now()),  # Party 0 off hold
    PartyHistory(1, "drop", datetime.now())     # Party 1 drops
]

# Add to dialog
dialog = Dialog(
    type="recording",
    start=datetime.now(),
    parties=[0, 1],
    party_history=history
)

# Valid event types: "join", "drop", "hold", "unhold", "mute", "unmute"
```

### 10. Advanced Dialog Features (vCon 0.3.0)

New dialog fields for enhanced functionality.

```python
# Dialog with session tracking and content hashing
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    originator=0,
    body="Hello, this is a test message!",
    session_id="session-12345",
    content_hash="c8d3d67f662a787e96e74ccb0a77803138c0f13495a186ccbde495c57c385608",
    application="chat-app",
    message_id="<message-id@example.com>"
)

# Video dialog with metadata
video_dialog = Dialog(
    type="video",
    start=datetime.now(),
    parties=[0, 1],
    mimetype="video/mp4",
    resolution="1920x1080",
    frame_rate=30.0,
    codec="H.264",
    bitrate=5000000,
    filename="recording.mp4"
)

# Incomplete dialog with disposition
incomplete_dialog = Dialog(
    type="incomplete",
    start=datetime.now(),
    parties=[0],
    disposition="no-answer"  # Valid: no-answer, congestion, failed, busy, hung-up, voicemail-no-message
)
```

## 11. Security and Validation

### Signing and Verification

```python
# Generate a key pair
private_key, public_key = Vcon.generate_key_pair()

# Sign the vCon
vcon.sign(private_key)

# Verify the signature
is_valid = vcon.verify(public_key)
```

### Validation

```python
# Validate a vCon object
is_valid, errors = vcon.is_valid()
if not is_valid:
    print("Validation errors:", errors)

# Validate a file
is_valid, errors = Vcon.validate_file("conversation.json")

# Validate a JSON string
is_valid, errors = Vcon.validate_json(json_string)
```

## Common Patterns and Best Practices

### 1. Creating a Complete Conversation

```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime, timezone

# Create a new vCon
vcon = Vcon.build_new()

# Add participants
caller = Party(tel="+1234567890", name="Alice", role="caller")
agent = Party(tel="+1987654321", name="Bob", role="agent")
vcon.add_party(caller)
vcon.add_party(agent)

# Add conversation dialogs in sequence
vcon.add_dialog(Dialog(
    type="text",
    start=datetime.now(timezone.utc).isoformat(),
    parties=[0, 1],
    originator=0,  # Caller
    mimetype="text/plain",
    body="Hello, I need help with my account."
))

vcon.add_dialog(Dialog(
    type="text",
    start=datetime.now(timezone.utc).isoformat(),
    parties=[0, 1],
    originator=1,  # Agent
    mimetype="text/plain",
    body="I'd be happy to help. Can you provide your account number?"
))

# Add metadata
vcon.add_tag("customer_id", "12345")
vcon.add_tag("interaction_id", "INT-001")

# Validate and save
is_valid, errors = vcon.is_valid()
if is_valid:
    vcon.save_to_file("conversation.json")
else:
    print("Validation errors:", errors)
```

### 2. Working with Audio Content

```python
import base64

# Reading an audio file and adding it to a dialog
with open("recording.mp3", "rb") as f:
    audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")

audio_dialog = Dialog(
    type="audio",
    start=datetime.now(timezone.utc).isoformat(),
    parties=[0, 1],
    originator=0,
    mimetype="audio/mp3",
    body=audio_base64,
    encoding="base64",
    filename="recording.mp3"
)
vcon.add_dialog(audio_dialog)
```

### 3. External vs Inline Content

```python
# External content (referenced by URL)
external_dialog = Dialog(
    type="recording",
    start=datetime.now(timezone.utc).isoformat(),
    parties=[0, 1],
    url="https://example.com/recordings/call123.mp3",
    mimetype="audio/mp3"
)

# Check if dialog refers to external content
if external_dialog.is_external_data():
    # Convert to inline data
    external_dialog.to_inline_data()

# Check if dialog contains inline data
if dialog.is_inline_data():
    print("Dialog contains embedded content")
```

### 4. Video Content Handling

```python
# Add video data with metadata
video_dialog = Dialog(
    type="video",
    start=datetime.now(),
    parties=[0, 1],
    mimetype="video/mp4",
    resolution="1920x1080",
    frame_rate=30.0,
    codec="H.264"
)

# Add video data (inline or external)
video_dialog.add_video_data(
    video_data=binary_video_data,  # or URL string
    filename="recording.mp4",
    mimetype="video/mp4",
    inline=True,  # False for external reference
    metadata={"duration": 120, "quality": "high"}
)

# Extract video metadata using FFmpeg
metadata = video_dialog.extract_video_metadata()

# Generate thumbnail
thumbnail_data = video_dialog.generate_thumbnail(
    timestamp=10.0,  # Time in seconds
    width=320,
    height=240,
    quality=90
)

# Transcode video to different format
video_dialog.transcode_video(
    target_format="webm",
    codec="vp9",
    bit_rate=2000000,
    width=1280,
    height=720
)
```

### 5. Image Content Handling

```python
# Add image data from file
image_dialog = Dialog(
    type="text",  # Can be any type
    start=datetime.now(),
    parties=[0, 1]
)

# Add image from file
image_dialog.add_image_data(
    image_path="screenshot.png",
    mimetype="image/jpeg"  # Optional, auto-detected if not provided
)

# Generate thumbnail
thumbnail_b64 = image_dialog.generate_thumbnail(max_size=(200, 200))

# Check if dialog has image content
if image_dialog.is_image():
    print("Dialog contains image content")

# Check for PDF content
if image_dialog.is_pdf():
    print("Dialog contains PDF content")
```

### 6. Content Hashing and Integrity

```python
# Calculate content hash
content_hash = dialog.calculate_content_hash("sha256")

# Set content hash for external files
dialog.set_content_hash(content_hash)

# Verify content integrity
is_valid = dialog.verify_content_hash(expected_hash, "sha256")

# Check if external data has changed
if dialog.is_external_data_changed():
    print("External content has been modified")
```

## Error Handling

```python
try:
    vcon = Vcon.load_from_file("conversation.json")
    is_valid, errors = vcon.is_valid()
    if not is_valid:
        print("Validation errors:", errors)
except FileNotFoundError:
    print("File not found")
except json.JSONDecodeError:
    print("Invalid JSON format")
except Exception as e:
    print(f"Error: {str(e)}")
```

## Working with Property Handling Modes

The Vcon constructor accepts a `property_handling` parameter to control how non-standard properties are handled:

```python
# Default mode: keep non-standard properties
vcon = Vcon(vcon_dict)  # or Vcon(vcon_dict, property_handling="default")

# Strict mode: remove non-standard properties
vcon = Vcon(vcon_dict, property_handling="strict")

# Meta mode: move non-standard properties to meta object
vcon = Vcon(vcon_dict, property_handling="meta")
```

## LLM-Specific Patterns and Best Practices

### 1. Code Generation Templates

When generating vCon code, use these templates as starting points:

#### Basic Conversation Template
```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime

def create_basic_conversation():
    # Create vCon
    vcon = Vcon.build_new()
    
    # Add parties
    caller = Party(tel="+1234567890", name="Caller", role="caller")
    agent = Party(tel="+1987654321", name="Agent", role="agent")
    vcon.add_party(caller)
    vcon.add_party(agent)
    
    # Add conversation
    vcon.add_dialog(Dialog(
        type="text",
        start=datetime.now().isoformat(),
        parties=[0, 1],
        originator=0,
        body="Hello, I need help."
    ))
    
    return vcon
```

#### Multimedia Conversation Template
```python
def create_multimedia_conversation():
    vcon = Vcon.build_new()
    
    # Add parties with enhanced contact info
    caller = Party(
        tel="+1234567890",
        name="Alice",
        role="caller",
        mailto="alice@example.com",
        timezone="America/New_York"
    )
    agent = Party(
        tel="+1987654321", 
        name="Bob",
        role="agent",
        sip="sip:bob@company.com"
    )
    vcon.add_party(caller)
    vcon.add_party(agent)
    
    # Add text dialog
    vcon.add_dialog(Dialog(
        type="text",
        start=datetime.now().isoformat(),
        parties=[0, 1],
        originator=0,
        body="Hello, I need help with my account."
    ))
    
    # Add audio dialog
    vcon.add_dialog(Dialog(
        type="recording",
        start=datetime.now().isoformat(),
        parties=[0, 1],
        mimetype="audio/mp3",
        filename="conversation.mp3"
    ))
    
    # Add analysis
    vcon.add_analysis(
        type="sentiment",
        dialog=[0, 1],
        vendor="SentimentAnalyzer",
        body={"sentiment": "positive", "confidence": 0.85},
        encoding="json"
    )
    
    return vcon
```

#### Extension-Enabled Conversation Template
```python
def create_extension_enabled_conversation():
    """Create a vCon with both Lawful Basis and WTF extensions."""
    from datetime import datetime, timezone, timedelta
    
    vcon = Vcon.build_new()
    
    # Add parties
    caller = Party(
        tel="+1234567890",
        name="Alice",
        role="caller",
        mailto="alice@example.com"
    )
    agent = Party(
        tel="+1987654321",
        name="Bob", 
        role="agent",
        sip="sip:bob@company.com"
    )
    vcon.add_party(caller)
    vcon.add_party(agent)
    
    # Add recording dialog
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
    
    # Add extensions
    vcon.add_extension("lawful_basis")
    vcon.add_extension("wtf_transcription")
    
    return vcon
```

#### Privacy-Compliant Conversation Template
```python
def create_privacy_compliant_conversation():
    """Create a vCon with comprehensive privacy compliance."""
    from datetime import datetime, timezone, timedelta
    from vcon.extensions.lawful_basis import (
        LawfulBasisAttachment, 
        PurposeGrant, 
        ContentHash,
        ProofMechanism,
        LawfulBasisType,
        ProofType,
        HashAlgorithm
    )
    
    vcon = Vcon.build_new()
    
    # Add parties
    caller = Party(
        tel="+1234567890",
        name="Alice",
        role="caller"
    )
    agent = Party(
        tel="+1987654321",
        name="Bob",
        role="agent"
    )
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
    
    # Create comprehensive lawful basis
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
            conditions=["anonymized_data_only", "retention_30_days"]
        ),
        PurposeGrant(
            purpose="marketing",
            granted=False,
            granted_at=datetime.now(timezone.utc).isoformat()
        )
    ]
    
    # Create content hash for integrity
    content_hash = ContentHash(
        algorithm=HashAlgorithm.SHA_256,
        canonicalization="JCS",
        value="computed_hash_value"
    )
    
    # Create proof mechanism
    proof = ProofMechanism(
        proof_type=ProofType.VERBAL_CONFIRMATION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={
            "dialog_reference": 0,
            "confirmation_text": "I consent to recording for quality assurance"
        }
    )
    
    # Create lawful basis attachment
    attachment = LawfulBasisAttachment(
        lawful_basis=LawfulBasisType.CONSENT,
        expiration=(datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
        purpose_grants=purpose_grants,
        content_hash=content_hash,
        proof_mechanisms=[proof]
    )
    
    # Add to vCon
    vcon.vcon_dict["attachments"].append({
        "type": "lawful_basis",
        "encoding": "json",
        "body": attachment.to_dict(),
        "party": 0,
        "dialog": 0
    })
    
    # Add extension
    vcon.add_extension("lawful_basis")
    
    return vcon
```

#### Transcription-Enabled Conversation Template
```python
def create_transcription_enabled_conversation():
    """Create a vCon with comprehensive transcription support."""
    from datetime import datetime, timezone
    from vcon.extensions.wtf import (
        WTFAttachment, 
        Transcript, 
        Segment, 
        Word, 
        Speaker,
        Quality,
        Metadata
    )
    
    vcon = Vcon.build_new()
    
    # Add parties
    caller = Party(
        tel="+1234567890",
        name="Alice",
        role="caller"
    )
    agent = Party(
        tel="+1987654321",
        name="Bob",
        role="agent"
    )
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
    
    # Create detailed transcript
    transcript = Transcript(
        text="Hello, I need help with my account. Can you assist me?",
        language="en",
        duration=6.5,
        confidence=0.94
    )
    
    # Create segments with words
    segments = [
        Segment(
            id=0,
            start=0.0,
            end=3.2,
            text="Hello, I need help with my account.",
            confidence=0.95,
            speaker=0,
            words=[
                Word(id=0, start=0.0, end=0.5, text="Hello", confidence=0.98, speaker=0),
                Word(id=1, start=0.5, end=0.8, text="I", confidence=0.95, speaker=0),
                Word(id=2, start=0.8, end=1.1, text="need", confidence=0.92, speaker=0),
                Word(id=3, start=1.1, end=1.4, text="help", confidence=0.94, speaker=0),
                Word(id=4, start=1.4, end=1.7, text="with", confidence=0.90, speaker=0),
                Word(id=5, start=1.7, end=2.0, text="my", confidence=0.96, speaker=0),
                Word(id=6, start=2.0, end=2.5, text="account", confidence=0.93, speaker=0)
            ]
        ),
        Segment(
            id=1,
            start=3.2,
            end=6.5,
            text="Can you assist me?",
            confidence=0.92,
            speaker=0,
            words=[
                Word(id=7, start=3.2, end=3.5, text="Can", confidence=0.91, speaker=0),
                Word(id=8, start=3.5, end=3.8, text="you", confidence=0.94, speaker=0),
                Word(id=9, start=3.8, end=4.2, text="assist", confidence=0.89, speaker=0),
                Word(id=10, start=4.2, end=4.5, text="me", confidence=0.95, speaker=0)
            ]
        )
    ]
    
    # Create speaker information
    speakers = [
        Speaker(
            id=0,
            label="Customer",
            segments=[0, 1],
            total_time=6.5,
            confidence=0.93
        )
    ]
    
    # Create quality metrics
    quality = Quality(
        audio_quality="high",
        background_noise=0.05,
        multiple_speakers=False,
        overlapping_speech=False,
        silence_ratio=0.1,
        average_confidence=0.94,
        low_confidence_words=2,
        processing_warnings=[]
    )
    
    # Create metadata
    metadata = Metadata(
        created_at=datetime.now(timezone.utc).isoformat(),
        processed_at=datetime.now(timezone.utc).isoformat(),
        provider="whisper",
        model="whisper-1",
        audio_quality="high",
        background_noise=0.05
    )
    
    # Create comprehensive WTF attachment
    attachment = WTFAttachment(
        transcript=transcript,
        segments=segments,
        metadata=metadata,
        words=[word for segment in segments for word in segment.words],
        speakers=speakers,
        quality=quality
    )
    
    # Add to vCon
    vcon.vcon_dict["attachments"].append({
        "type": "wtf_transcription",
        "encoding": "json",
        "body": attachment.to_dict(),
        "party": 0,
        "dialog": 0
    })
    
    # Add extension
    vcon.add_extension("wtf_transcription")
    
    return vcon
```

### 2. Common LLM Tasks

#### Converting Chat History to vCon
```python
def chat_to_vcon(chat_messages, participants):
    vcon = Vcon.build_new()
    
    # Add participants as parties
    party_map = {}
    for i, participant in enumerate(participants):
        party = Party(
            name=participant.get("name", f"User {i}"),
            role=participant.get("role", "participant")
        )
        vcon.add_party(party)
        party_map[participant["id"]] = i
    
    # Add messages as dialogs
    for message in chat_messages:
        vcon.add_dialog(Dialog(
            type="text",
            start=message["timestamp"],
            parties=[party_map[message["sender_id"]]],
            originator=party_map[message["sender_id"]],
            body=message["content"]
        ))
    
    return vcon
```

#### Adding AI Analysis to vCon
```python
def add_ai_analysis(vcon, analysis_type, results, dialog_indices=None):
    if dialog_indices is None:
        dialog_indices = list(range(len(vcon.dialog)))
    
    vcon.add_analysis(
        type=analysis_type,
        dialog=dialog_indices,
        vendor="AI-Analyzer",
        body=results,
        encoding="json"
    )
    
    # Add extension if using AI features
    vcon.add_extension("ai_analysis")
```

#### Extracting Conversation Data
```python
def extract_conversation_data(vcon):
    data = {
        "uuid": vcon.uuid,
        "created_at": vcon.created_at,
        "parties": [],
        "dialogs": [],
        "analysis": []
    }
    
    # Extract parties
    for party in vcon.parties:
        data["parties"].append({
            "name": getattr(party, "name", None),
            "role": getattr(party, "role", None),
            "tel": getattr(party, "tel", None)
        })
    
    # Extract dialogs
    for dialog in vcon.dialog:
        data["dialogs"].append({
            "type": dialog.get("type"),
            "start": dialog.get("start"),
            "body": dialog.get("body", "")[:100] + "..." if len(dialog.get("body", "")) > 100 else dialog.get("body", ""),
            "parties": dialog.get("parties", [])
        })
    
    # Extract analysis
    for analysis in vcon.analysis:
        data["analysis"].append({
            "type": analysis.get("type"),
            "vendor": analysis.get("vendor"),
            "dialog_count": len(analysis.get("dialog", []))
        })
    
    return data
```

#### Adding Privacy Compliance to vCon
```python
def add_privacy_compliance(vcon, party_index, purposes, expiration_days=365):
    """Add lawful basis attachment for privacy compliance."""
    from datetime import datetime, timezone, timedelta
    
    purpose_grants = []
    for purpose in purposes:
        purpose_grants.append({
            "purpose": purpose,
            "granted": True,
            "granted_at": datetime.now(timezone.utc).isoformat()
        })
    
    vcon.add_lawful_basis_attachment(
        lawful_basis="consent",
        expiration=(datetime.now(timezone.utc) + timedelta(days=expiration_days)).isoformat(),
        purpose_grants=purpose_grants,
        party_index=party_index
    )
    
    vcon.add_extension("lawful_basis")
    return vcon
```

#### Converting Provider Transcription to WTF
```python
def convert_provider_transcription(vcon, provider_data, provider_type, party_index=0, dialog_index=0):
    """Convert provider-specific transcription data to WTF format."""
    from vcon.extensions.wtf import WhisperAdapter, DeepgramAdapter, AssemblyAIAdapter
    
    # Select appropriate adapter
    adapters = {
        "whisper": WhisperAdapter(),
        "deepgram": DeepgramAdapter(),
        "assemblyai": AssemblyAIAdapter()
    }
    
    if provider_type not in adapters:
        raise ValueError(f"Unsupported provider: {provider_type}")
    
    # Convert to WTF format
    adapter = adapters[provider_type]
    wtf_attachment = adapter.convert(provider_data)
    
    # Add to vCon
    vcon.add_wtf_transcription_attachment(
        transcript=wtf_attachment.transcript.to_dict(),
        segments=[segment.to_dict() for segment in wtf_attachment.segments],
        metadata=wtf_attachment.metadata.to_dict(),
        party_index=party_index,
        dialog_index=dialog_index
    )
    
    vcon.add_extension("wtf_transcription")
    return vcon
```

#### Checking Privacy Permissions
```python
def check_privacy_permissions(vcon, party_index, purposes):
    """Check if party has permission for specific purposes."""
    results = {}
    for purpose in purposes:
        results[purpose] = vcon.check_lawful_basis_permission(purpose, party_index)
    return results
```

#### Exporting Transcriptions
```python
def export_transcriptions(vcon, party_index=None, format="srt"):
    """Export transcriptions from vCon to various formats."""
    attachments = vcon.find_wtf_attachments(party_index)
    exports = []
    
    for attachment in attachments:
        from vcon.extensions.wtf import WTFAttachment
        wtf_attachment = WTFAttachment.from_dict(attachment["body"])
        
        if format.lower() == "srt":
            content = wtf_attachment.export_to_srt()
        elif format.lower() == "vtt":
            content = wtf_attachment.export_to_vtt()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        exports.append({
            "party_index": attachment.get("party"),
            "dialog_index": attachment.get("dialog"),
            "format": format,
            "content": content
        })
    
    return exports
```

#### Validating Extensions
```python
def validate_vcon_extensions(vcon):
    """Validate all extensions in a vCon and return detailed results."""
    validation_results = vcon.validate_extensions()
    
    summary = {
        "valid": True,
        "extensions": {},
        "errors": [],
        "warnings": []
    }
    
    for extension, result in validation_results.items():
        if extension != "attachments":
            summary["extensions"][extension] = {
                "valid": result["is_valid"],
                "errors": result["errors"],
                "warnings": result["warnings"]
            }
            
            if not result["is_valid"]:
                summary["valid"] = False
                summary["errors"].extend(result["errors"])
            
            summary["warnings"].extend(result["warnings"])
    
    return summary
```

#### Processing Extensions
```python
def process_vcon_extensions(vcon):
    """Process all extensions in a vCon and return results."""
    processing_results = vcon.process_extensions()
    
    summary = {
        "success": True,
        "results": processing_results,
        "errors": []
    }
    
    # Check for processing errors
    if "error" in processing_results:
        summary["success"] = False
        summary["errors"].append(processing_results["error"])
    
    return summary
```

### 3. Error Handling Patterns

```python
def safe_vcon_operation(operation_func, *args, **kwargs):
    """Safely execute vCon operations with proper error handling."""
    try:
        return operation_func(*args, **kwargs)
    except ValueError as e:
        return {"error": f"Validation error: {str(e)}", "success": False}
    except FileNotFoundError as e:
        return {"error": f"File not found: {str(e)}", "success": False}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "success": False}

# Usage
result = safe_vcon_operation(Vcon.load, "conversation.json")
if not result.get("success", True):
    print(f"Error: {result['error']}")
```

### 4. Validation Patterns

```python
def validate_and_fix_vcon(vcon):
    """Validate vCon and attempt to fix common issues."""
    is_valid, errors = vcon.is_valid()
    
    if is_valid:
        return {"valid": True, "errors": []}
    
    fixes_applied = []
    
    # Fix common issues
    for error in errors:
        if "missing uuid" in error.lower():
            # UUID is auto-generated, this shouldn't happen
            pass
        elif "invalid dialog type" in error.lower():
            # Try to fix invalid dialog types
            for dialog in vcon.dialog:
                if dialog.get("type") not in ["text", "recording", "transfer", "incomplete", "audio", "video"]:
                    dialog["type"] = "text"  # Default to text
                    fixes_applied.append(f"Fixed invalid dialog type: {dialog.get('type')}")
    
    # Re-validate after fixes
    is_valid, remaining_errors = vcon.is_valid()
    
    return {
        "valid": is_valid,
        "errors": remaining_errors,
        "fixes_applied": fixes_applied
    }
```

### 5. Integration Patterns

#### REST API Integration
```python
def vcon_to_api_payload(vcon):
    """Convert vCon to API payload format."""
    return {
        "vcon": vcon.to_dict(),
        "metadata": {
            "version": vcon.vcon,
            "created_at": vcon.created_at,
            "party_count": len(vcon.parties),
            "dialog_count": len(vcon.dialog)
        }
    }

def api_payload_to_vcon(payload):
    """Convert API payload to vCon."""
    return Vcon(payload["vcon"])
```

#### Database Integration
```python
def vcon_to_database_record(vcon):
    """Convert vCon to database record format."""
    return {
        "id": vcon.uuid,
        "version": vcon.vcon,
        "created_at": vcon.created_at,
        "updated_at": vcon.updated_at,
        "data": vcon.to_json(),
        "party_count": len(vcon.parties),
        "dialog_count": len(vcon.dialog),
        "has_attachments": len(vcon.attachments) > 0,
        "has_analysis": len(vcon.analysis) > 0
    }
```

### 6. Performance Considerations

```python
def optimize_vcon_for_storage(vcon):
    """Optimize vCon for storage by converting large content to external references."""
    for i, dialog in enumerate(vcon.dialog):
        if dialog.get("body") and len(dialog["body"]) > 1000000:  # 1MB threshold
            # In real implementation, upload to storage and get URL
            external_url = f"https://storage.example.com/dialog_{i}_content"
            dialog["url"] = external_url
            dialog["content_hash"] = dialog.calculate_content_hash()
            del dialog["body"]
            dialog["encoding"] = None

def optimize_vcon_for_processing(vcon):
    """Optimize vCon for processing by loading external content."""
    for dialog in vcon.dialog:
        if dialog.is_external_data():
            try:
                dialog.to_inline_data()
            except Exception as e:
                print(f"Failed to load external content: {e}")
```

## Conclusion

The vCon library provides a comprehensive framework for working with conversation data. When generating code:

1. **Start Simple**: Begin with `Vcon.build_new()` and basic Party/Dialog objects
2. **Add Rich Metadata**: Use tags, attachments, and analysis for comprehensive data
3. **Handle Multimedia**: Leverage video/image processing capabilities when needed
4. **Ensure Security**: Use digital signatures for integrity verification
5. **Validate Always**: Check vCon validity before saving or transmitting
6. **Handle Errors Gracefully**: Implement proper error handling for robust applications
7. **Consider Performance**: Optimize for storage or processing based on use case
8. **Use Extensions**: Declare optional features and must-support requirements
9. **Track Events**: Use party history for complex multi-party conversations
10. **Integrate Seamlessly**: Follow patterns for API and database integration
11. **Implement Privacy Compliance**: Use Lawful Basis extension for GDPR compliance
12. **Standardize Transcriptions**: Use WTF extension for multi-provider transcription support
13. **Validate Extensions**: Always validate extension data before processing
14. **Export Transcriptions**: Leverage WTF export capabilities for subtitle formats
15. **Check Permissions**: Use lawful basis permission checking for privacy compliance

The vCon 0.3.0 specification provides a robust foundation for modern conversation data management with support for multimedia content, security, and extensibility.