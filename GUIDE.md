# vCon Library API Guide

## Table of Contents
1. [Core Classes](#core-classes)
2. [Creating and Managing vCons](#creating-and-managing-vcons)
3. [Working with Parties](#working-with-parties)
4. [Managing Dialog](#managing-dialog)
5. [Attachments and Analysis](#attachments-and-analysis)
6. [Security and Validation](#security-and-validation)

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
- `vcon`: Version number
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
vcon = Vcon({"uuid": "...", "vcon": "0.0.1"})

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
    mimetype="text/plain",
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
    mimetype="audio/wav"
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
attachment = vcon.find_attachment_by_type("document")
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
json_str = '{"uuid": "...", "vcon": "0.0.1", ...}'
is_valid, errors = Vcon.validate_json(json_str)
```

The validation checks include:
- Required fields (uuid, vcon, created_at)
- Date format validation
- Party references in dialogs
- MIME type validation
- Attachment and analysis format validation
- Encoding validation
