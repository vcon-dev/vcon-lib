# vCon Library API Guide

## Table of Contents
1. [Core Classes](#core-classes)
2. [Creating and Managing vCons](#creating-and-managing-vcons)
3. [Working with Parties](#working-with-parties)
4. [Managing Dialog](#managing-dialog)
5. [Attachments and Analysis](#attachments-and-analysis)
6. [Extensions](#extensions)
   - [Extension Framework](#extension-framework)
   - [Lawful Basis Extension](#lawful-basis-extension)
   - [WTF Extension](#wtf-extension)
7. [Security and Validation](#security-and-validation)

## Core Classes

### Vcon
The main class for creating and managing virtual conversation containers.

```python
from vcon import Vcon
```

#### Initialization
- `Vcon(vcon_dict={})`: Initialize from a dictionary
- `Vcon.build_new()`: Create a new vCon with default values
- `Vcon.build_from_json(json_string)`: Create from JSON string

#### Properties
- `uuid`: Unique identifier
- `vcon`: Version number (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `parties`: List of participants
- `dialog`: List of dialog entries
- `attachments`: List of attachments
- `analysis`: List of analysis entries
- `redacted`: Redaction information
- `group`: Group information
- `meta`: Metadata
- `tags`: Tags attachment
- `extensions`: List of extensions used
- `critical`: List of must-support extensions

### Party
Represents a participant in the conversation.

```python
from vcon.party import Party
```

#### Initialization Parameters
- `tel`: Telephone number
- `stir`: STIR verification
- `mailto`: Email address
- `name`: Party name
- `validation`: Validation status
- `gmlpos`: Geographic position
- `civicaddress`: Civic address
- `uuid`: Unique identifier
- `role`: Party role
- `contact_list`: Contact list
- `meta`: Additional metadata

### Dialog
Represents a conversation entry.

```python
from vcon.dialog import Dialog
```

#### Supported MIME Types
- `text/plain`
- `audio/x-wav`, `audio/wav`, `audio/wave`
- `audio/mpeg`, `audio/mp3`
- `audio/ogg`
- `audio/webm`
- `audio/x-m4a`
- `audio/aac`
- `video/x-mp4`
- `video/ogg`
- `multipart/mixed`
- `message/rfc822` (for email dialogs)

## Creating and Managing vCons

### Creating a New vCon
```python
# Create empty vCon
vcon = Vcon.build_new()

# Create from dictionary
vcon = Vcon({"uuid": "...", "created_at": "2024-01-01T00:00:00Z"})

# Create from JSON
vcon = Vcon.build_from_json(json_string)
```

### Serialization
```python
# To JSON string
json_str = vcon.to_json()
# or
json_str = vcon.dumps()

# To dictionary
dict_data = vcon.to_dict()

# Save to file
vcon.save_to_file("conversation.json")

# Post to URL with custom headers
response = vcon.post_to_url(
    'https://api.example.com/vcons',
    headers={
        'x-conserver-api-token': 'your-token-here',
        'x-custom-header': 'custom-value'
    }
)
if response.status_code == 200:
    print("Successfully posted vCon")
```

The `save_to_file` method allows you to save a vCon directly to a JSON file:
- Takes a file path as argument
- Automatically handles JSON serialization
- Raises IOError if there are file permission issues

The `post_to_url` method enables sending a vCon to a URL endpoint:
- Automatically sets Content-Type to application/json
- Supports custom headers for authentication and other purposes
- Returns a requests.Response object for handling the server response
- Raises requests.RequestException for network/server errors

### Tags
```python
# Add a tag
vcon.add_tag("category", "support")

# Get a tag value
value = vcon.get_tag("category")

# Get all tags
tags = vcon.tags
```

### Extension Management

```python
# Add extensions
vcon.add_extension("lawful_basis")
vcon.add_extension("wtf_transcription")

# Get list of extensions
extensions = vcon.get_extensions()

# Add must-support extensions
vcon.add_critical("encryption")

# Get must-support extensions
critical = vcon.get_critical()

# Remove extensions
vcon.remove_extension("video")
vcon.remove_critical("encryption")
```

## Working with Parties

### Adding Parties
```python
# Create and add a party
party = Party(
    tel="+1234567890",
    name="John Doe",
    role="customer"
)
vcon.add_party(party)
```

### Finding Parties
```python
# Find party index by attribute
index = vcon.find_party_index("tel", "+1234567890")
```

## Managing Dialog

### Adding Dialog Entries
```python
# Add a text dialog
dialog = Dialog(
    type="text",
    start="2024-03-21T10:00:00Z",
    parties=[0, 1],
    mediatype="text/plain",
    body="Hello, how can I help?"
)
vcon.add_dialog(dialog)
```

### Working with Media
```python
# Add inline data
dialog.add_inline_data(
    body="base64_encoded_content",
    filename="recording.wav",
    mediatype="audio/wav"
)

# Check data type
is_external = dialog.is_external_data()
is_inline = dialog.is_inline_data()
```

## Attachments and Analysis

### Attachments
```python
# Add an attachment
vcon.add_attachment(
    type="document",
    body="content",
    encoding="none"
)

# Find attachment
attachment = vcon.find_attachment_by_purpose("document")
```

### Analysis
```python
# Add analysis
vcon.add_analysis(
    type="sentiment",
    dialog=[0],
    vendor="analyzer",
    body={"score": 0.8},
    encoding="json"
)

# Find analysis
analysis = vcon.find_analysis_by_type("sentiment")
```

## Extensions

The vCon library includes a comprehensive extension framework that allows for standardized implementation of additional functionality. Two major extensions are currently implemented: the Lawful Basis extension for privacy compliance and the WTF (World Transcription Format) extension for standardized transcription data.

### Extension Framework

The extension framework provides a standardized way to add new functionality to vCon objects while maintaining compatibility and validation.

#### Core Extension Classes

```python
from vcon.extensions import get_extension_registry

# Get the global registry
registry = get_extension_registry()

# List all registered extensions
extensions = registry.list_extensions()
```

#### Extension Types
- `COMPATIBLE`: Safe to ignore, no breaking changes
- `INCOMPATIBLE`: Must be supported, breaking changes  
- `EXPERIMENTAL`: Development/testing only

### Lawful Basis Extension

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

### WTF Extension

The WTF (World Transcription Format) extension provides standardized representation of speech-to-text transcription data from multiple providers.

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
    mediatype="audio/mp3"
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

## Security and Validation

### Signing and Verification
```python
# Generate key pair
private_key, public_key = Vcon.generate_key_pair()

# Sign vCon
vcon.sign(private_key)

# Verify signature
is_valid = vcon.verify(public_key)
```

### Validation
```python
# Validate vCon object
is_valid, errors = vcon.is_valid()

# Validate JSON file
is_valid, errors = Vcon.validate_file("conversation.json")

# Validate JSON string
is_valid, errors = Vcon.validate_json(json_string)
```

### UUID Generation
```python
# Generate UUID8 from domain name
uuid = Vcon.uuid8_domain_name("example.com")

# Generate UUID8 with custom bits
uuid = Vcon.uuid8_time(custom_bits)
```

### Loading and Validating vCons

#### Loading vCons
```python
# Load from file or URL
vcon = Vcon.load("path/to/vcon.json")  # or "https://example.com/vcon.json"

# Load specifically from file
vcon = Vcon.load_from_file("path/to/vcon.json")

# Load from URL
vcon = Vcon.load_from_url("https://example.com/vcon.json")
```

#### Validating vCons
```python
# Validate a vCon object
is_valid, errors = vcon.is_valid()
if not is_valid:
    print("Validation errors:", errors)

# Validate a vCon file
is_valid, errors = Vcon.validate_file("path/to/vcon.json")

# Validate a vCon JSON string
json_str = '{"uuid": "123", "created_at": "2024-01-01T00:00:00Z", ...}'
is_valid, errors = Vcon.validate_json(json_str)
```