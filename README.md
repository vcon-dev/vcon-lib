# vCon Python Library

## About the Library

The vCon (Virtual Conversation) library is a powerful Python tool designed to capture, structure, and manage conversation data in a standardized format. It provides a robust set of features for creating, manipulating, and analyzing digital representations of conversations, making it particularly useful for applications in customer service, call centers, chat systems, and any scenario where structured conversation data is valuable.

## Features

- **Conversation Container**: Create and manage vCon objects that serve as containers for all conversation elements
- **Party Management**: Add and track conversation participants with detailed attributes (name, role, contact info)
- **Dialog Handling**: Record and organize messages with timestamps, content, and sender information
- **Rich Media Support**: Handle various content types including text, audio, and video with MIME type validation
- **Metadata & Tags**: Add and retrieve metadata and tags for easy categorization
- **File Attachments**: Include and manage related files and documents
- **Analysis Integration**: Incorporate analysis data from various sources (e.g., sentiment analysis)
- **Security**: Sign and verify vCon objects using JWS (JSON Web Signature)
- **Validation**: Comprehensive validation of vCon structure and content
- **UUID8 Support**: Generate and manage unique identifiers for conversations
- **Serialization**: Convert vCon objects to and from JSON for storage and transmission

## Installation

```bash
pip install vcon
```

## Documentation

The full documentation is available at [https://yourusername.github.io/vcon-lib/](https://yourusername.github.io/vcon-lib/).

To build the documentation locally:

```bash
# Install development dependencies
poetry install --with dev

# Build the docs
cd docs
poetry run make html
```

The built documentation will be available in `docs/build/html/index.html`.

## Quick Start

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

# Add a dialog entry
dialog = Dialog(
    type="text",
    start=datetime.now(timezone.utc).isoformat(),
    parties=[0, 1],  # Indices of the parties
    originator=0,    # Caller is the originator
    mimetype="text/plain",
    body="Hello, I need help with my account."
)
vcon.add_dialog(dialog)

# Add metadata
vcon.add_tag("customer_id", "12345")
vcon.add_tag("interaction_id", "INT-001")

# Add an analysis
vcon.add_analysis(
    type="sentiment",
    dialog=[0],  # Reference to the dialog entry
    vendor="SentimentAnalyzer",
    body={"sentiment": "neutral"},
    encoding="json"
)

# Sign the vCon (optional)
private_key, public_key = Vcon.generate_key_pair()
vcon.sign(private_key)

# Validate the vCon
is_valid, errors = vcon.is_valid()
if is_valid:
    print("vCon is valid")
else:
    print("Validation errors:", errors)

# Serialize to JSON
json_data = vcon.to_json()
```

## File Validation

The vCon library provides comprehensive validation capabilities for both files and JSON strings:

```python
# Validate a vCon file
is_valid, errors = Vcon.validate_file("conversation.json")
if not is_valid:
    print("File validation errors:", errors)

# Validate a vCon JSON string
json_str = '{"uuid": "123", "vcon": "0.0.1", ...}'
is_valid, errors = Vcon.validate_json(json_str)
if not is_valid:
    print("JSON validation errors:", errors)

# Load and validate a vCon from file
try:
    vcon = Vcon.load_from_file("conversation.json")
    is_valid, errors = vcon.is_valid()
    if not is_valid:
        print("vCon validation errors:", errors)
except FileNotFoundError:
    print("File not found")
except json.JSONDecodeError:
    print("Invalid JSON format")

# Load and validate a vCon from URL
try:
    vcon = Vcon.load_from_url("https://example.com/conversation.json")
    is_valid, errors = vcon.is_valid()
    if not is_valid:
        print("vCon validation errors:", errors)
except requests.RequestException:
    print("Error fetching from URL")
except json.JSONDecodeError:
    print("Invalid JSON format")
```

The validation checks include:
- Required fields (uuid, vcon version, created_at)
- Data type correctness
- ISO 8601 datetime format validation
- Party references in dialogs
- MIME type validation
- Analysis references to dialogs
- Encoding format validation
- Relationship integrity between different parts of the vCon

## IETF vCon Working Group

The vCon (Virtual Conversation) format is being developed as an open standard through the Internet Engineering Task Force (IETF). The vCon Working Group is focused on creating a standardized format for representing digital conversations across various platforms and use cases.

### Participating in the Working Group

1. **Join the Mailing List**: Subscribe to the vCon working group mailing list at [vcon@ietf.org](mailto:vcon@ietf.org)

2. **Review Documents**: 
   - Working group documents and drafts can be found at: https://datatracker.ietf.org/wg/vcon/documents/
   - The current Internet-Draft can be found at: https://datatracker.ietf.org/doc/draft-ietf-vcon-vcon-container/

3. **Attend Meetings**:
   - The working group meets virtually during IETF meetings
   - Meeting schedules and connection details are announced on the mailing list
   - Past meeting materials and recordings are available on the IETF datatracker

4. **Contribute**:
   - Submit comments and suggestions on the mailing list
   - Propose changes through GitHub pull requests
   - Participate in working group discussions
   - Help with implementations and interoperability testing

For more information about the IETF standardization process and how to participate, visit: https://www.ietf.org/about/participate/

## Advanced Usage

### Working with Attachments

```python
# Add a file attachment
vcon.add_attachment(
    type="transcript",
    body="Conversation transcript content...",
    encoding="none"
)

# Add a base64-encoded attachment
vcon.add_attachment(
    type="recording",
    body="base64_encoded_content...",
    encoding="base64url"
)
```

### Handling Party History

```python
from vcon.party import PartyHistory

# Create a dialog with party history
dialog = Dialog(
    type="transfer",
    start=datetime.now(timezone.utc).isoformat(),
    parties=[0, 1],
    party_history=[
        PartyHistory(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action="transfer",
            from_party=0,
            to_party=1
        )
    ]
)
vcon.add_dialog(dialog)
```

### File Validation

```python
# Validate a vCon JSON file
is_valid, errors = Vcon.validate_file("conversation.json")

# Validate a vCon JSON string
is_valid, errors = Vcon.validate_json(json_string)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

[License Type] - See LICENSE file for details
