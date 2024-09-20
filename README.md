# vCon Python Library

The vCon (Virtual Conversation) library is a powerful Python tool designed to capture, structure, and manage conversation data in a standardized format. It provides a robust set of features for creating, manipulating, and analyzing digital representations of conversations, making it particularly useful for applications in customer service, call centers, chat systems, and any scenario where structured conversation data is valuable.

At its core, the vCon library allows you to create vCon objects, which serve as containers for all elements of a conversation. These objects can include multiple parties (participants in the conversation), a series of dialogs (individual messages or utterances), metadata (such as tags for easy categorization), attachments (like transcripts or other related files), and even analysis data (such as sentiment analysis results).

Key capabilities of the vCon library include:

1. Creating and managing vCon objects with a flexible, extensible structure.
2. Adding and retrieving conversation participants (parties) with various attributes.
3. Recording and organizing dialog entries with timestamps, content, and sender information.
4. Attaching metadata and tags for easy categorization and searching.
5. Including file attachments related to the conversation.
6. Incorporating analysis data from various sources (e.g., sentiment analysis, topic classification).
7. Signing and verifying vCon objects for data integrity and authenticity.
8. Serializing vCon objects to and from JSON for easy storage and transmission.

The library is designed with extensibility in mind, allowing for easy integration with various analysis tools and systems. It also includes built-in support for handling different types of conversation data, including text, audio, and video.

By providing a standardized way to structure and manage conversation data, the vCon library enables powerful applications in areas such as conversation analytics, quality assurance, compliance monitoring, and machine learning model training for natural language processing tasks.

Whether you're building a customer service platform, a conversation analysis tool, or any application that deals with structured dialog data, the vCon library offers a comprehensive solution for capturing, storing, and working with conversation information in a consistent and powerful way.

## Features

- Create and manipulate vCon objects
- Add parties, dialogs, attachments, and analysis to vCons
- Sign and verify vCons using JWS (JSON Web Signature)
- Generate UUID8 identifiers
- Pack and unpack dialogs
- Add and retrieve tags


## Usage
# vCon API Tutorial

This tutorial will guide you through creating a vCon (Virtual Conversation) object using the vCon API. We'll cover creating a new vCon, adding parties and dialogs, attaching metadata and analysis, and finally signing and verifying the vCon.

## Prerequisites

Before you begin, make sure you have the vCon library installed in your Python environment.

```bash
pip install vcon  # Replace with the actual package name if different
```

## Step 1: Import Required Modules

First, let's import the necessary modules:

```python
import datetime
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from vcon.party import PartyHistory
```

## Step 2: Create a New vCon Object

To start, we'll create a new vCon object:

```python
vcon = Vcon.build_new()
```

## Step 3: Add Parties

Next, we'll add two parties to our vCon: a caller and an agent.

```python
caller = Party(tel="+1234567890", name="Alice", role="caller")
agent = Party(tel="+1987654321", name="Bob", role="agent")
vcon.add_party(caller)
vcon.add_party(agent)
```

## Step 4: Add Dialogs

Now, let's add some dialog to our vCon. 

```python
start_time = datetime.datetime.now(datetime.timezone.utc)
dialog = Dialog(
    type="text",
    start=start_time.isoformat(),
    parties=[0, 1],  # Indices of the parties in the vCon
    originator=0,  # The caller (Alice) is the originator
    mimetype="text/plain",
    body="Hello, I need help with my account.",
)
vcon.add_dialog(dialog)

```

Note that we're using ISO format strings for the datetime values and including UTC timezone information.

## Step 5: Add Metadata

We can add metadata to our vCon using tags:

```python
vcon.add_tag("customer_id", "12345")
vcon.add_tag("interaction_id", "INT-001")
```

## Step 6: Add an Attachment

Let's add a transcript as an attachment:

```python
transcript = "Alice: Hello, I need help with my account.\nBob: Certainly! I'd be happy to help. Can you please provide your account number?"
vcon.add_attachment(body=transcript, type="transcript", encoding="none")
```

## Step 7: Add Analysis

We can also add analysis data to our vCon. Here's an example of adding sentiment analysis:

```python
sentiment_analysis = {
    "overall_sentiment": "positive",
    "customer_sentiment": "neutral",
    "agent_sentiment": "positive"
}
vcon.add_analysis(
    type="sentiment",
    dialog=[0, 1],  # Indices of the dialogs analyzed
    vendor="SentimentAnalyzer",
    body=sentiment_analysis,
    encoding="none"
)
```

## Step 8: Sign and Verify the vCon

Finally, let's generate a key pair, sign the vCon, and verify the signature:

```python
# Generate a key pair for signing
private_key, public_key = Vcon.generate_key_pair()

# Sign the vCon
vcon.sign(private_key)

# Verify the signature
is_valid = vcon.verify(public_key)
print(f"Signature is valid: {is_valid}")
```

## Step 9: Serialize to JSON

To see the final result, we can serialize our vCon to JSON:

```python
print(vcon.to_json())
```

## Complete Example

Here's the complete example putting all these steps together:

```python
import datetime
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from vcon.party import PartyHistory

def main():
    # Create a new vCon object
    vcon = Vcon.build_new()

    # Add parties
    caller = Party(tel="+1234567890", name="Alice", role="caller")
    agent = Party(tel="+1987654321", name="Bob", role="agent")
    vcon.add_party(caller)
    vcon.add_party(agent)

    # Add a dialog
    start_time = datetime.datetime.now(datetime.timezone.utc)
    dialog = Dialog(
        type="text",
        start=start_time.isoformat(),
        parties=[0, 1],  # Indices of the parties in the vCon
        originator=0,  # The caller (Alice) is the originator
        mimetype="text/plain",
        body="Hello, I need help with my account.",
    )
    vcon.add_dialog(dialog)

    # Add a response from the agent
    response_time = start_time + datetime.timedelta(minutes=1)
    response = Dialog(
        type="text",
        start=response_time.isoformat(),
        parties=[0, 1],
        originator=1,  # The agent (Bob) is the originator
        mimetype="text/plain",
        body="Certainly! I'd be happy to help. Can you please provide your account number?",
    )
    vcon.add_dialog(response)

    # Add some metadata
    vcon.add_tag("customer_id", "12345")
    vcon.add_tag("interaction_id", "INT-001")

    # Add an attachment (e.g., a transcript)
    transcript = "Alice: Hello, I need help with my account.\nBob: Certainly! I'd be happy to help. Can you please provide your account number?"
    vcon.add_attachment(body=transcript, type="transcript", encoding="none")

    # Add some analysis (e.g., sentiment analysis)
    sentiment_analysis = {
        "overall_sentiment": "positive",
        "customer_sentiment": "neutral",
        "agent_sentiment": "positive"
    }
    vcon.add_analysis(
        type="sentiment",
        dialog=[0, 1],  # Indices of the dialogs analyzed
        vendor="SentimentAnalyzer",
        body=sentiment_analysis,
        encoding="none"
    )

    # Generate a key pair for signing
    private_key, public_key = Vcon.generate_key_pair()

    # Sign the vCon
    vcon.sign(private_key)

    # Verify the signature
    is_valid = vcon.verify(public_key)
    print(f"Signature is valid: {is_valid}")

    # Print the vCon as JSON
    print(vcon.to_json())

if __name__ == "__main__":
    main()
```

# vCon Python Library API Documentation

## Table of Contents

1. [Vcon Class](#vcon-class)
2. [Dialog Class](#dialog-class)
3. [Party Class](#party-class)
4. [PartyHistory Class](#partyhistory-class)
5. [Constants](#constants)

## Vcon Class

The `Vcon` class is the root class representing a vCon (Virtual Conversation) object.

### Constructor

```python
Vcon(vcon_dict: dict = {})
```

Initializes a Vcon object from a dictionary.

### Class Methods

- `build_from_json(json_string: str) -> Vcon`: Initialize a Vcon object from a JSON string.
- `build_new() -> Vcon`: Initialize a Vcon object with default values.
- `generate_key_pair() -> tuple`: Generate a new RSA key pair for signing vCons.

### Instance Methods

- `to_json() -> str`: Serialize the vCon to a JSON string.
- `to_dict() -> dict`: Serialize the vCon to a dictionary.
- `dumps() -> str`: Alias for `to_json()`.
- `get_tag(tag_name: str) -> Optional[dict]`: Returns the value of a tag by name.
- `add_tag(tag_name: str, tag_value: str) -> None`: Adds a tag to the vCon.
- `find_attachment_by_type(type: str) -> Optional[dict]`: Finds an attachment by type.
- `add_attachment(body: Union[dict, list, str], type: str, encoding: str = "none") -> None`: Adds an attachment to the vCon.
- `find_analysis_by_type(type: str) -> Any | None`: Finds an analysis by type.
- `add_analysis(type: str, dialog: Union[list, int], vendor: str, body: Union[dict, list, str], encoding: str = "none", extra: dict = {}) -> None`: Adds analysis data to the vCon.
- `add_party(party: Party) -> None`: Adds a party to the vCon.
- `find_party_index(by: str, val: str) -> Optional[int]`: Find the index of a party in the vCon given a key-value pair.
- `find_dialog(by: str, val: str) -> Optional[Dialog]`: Find a dialog in the vCon given a key-value pair.
- `add_dialog(dialog: Dialog) -> None`: Add a dialog to the vCon.
- `sign(private_key: Union[rsa.RSAPrivateKey, bytes]) -> None`: Sign the vCon using JWS.
- `verify(public_key: Union[rsa.RSAPublicKey, bytes]) -> bool`: Verify the JWS signature of the vCon.

### Properties

- `tags: Optional[dict]`: Returns the tags attachment.
- `parties: list[Party]`: Returns the list of parties.
- `dialog: list`: Returns the list of dialogs.
- `attachments: list`: Returns the list of attachments.
- `analysis: list`: Returns the list of analyses.
- `uuid: str`: Returns the UUID of the vCon.
- `vcon: str`: Returns the vCon version.
- `subject: Optional[str]`: Returns the subject of the vCon.
- `created_at`: Returns the creation timestamp of the vCon.
- `updated_at`: Returns the last update timestamp of the vCon.
- `redacted`: Returns the redacted information of the vCon.
- `appended`: Returns the appended information of the vCon.
- `group`: Returns the group information of the vCon.
- `meta`: Returns the metadata of the vCon.

### Static Methods

- `uuid8_domain_name(domain_name: str) -> str`: Generate a UUID8 from a domain name.
- `uuid8_time(custom_c_62_bits: int) -> str`: Generate a UUID8 from a custom 62-bit integer.

## Dialog Class

The `Dialog` class represents a dialog in the system.

### Constructor

```python
Dialog(type: str, 
       start: datetime, 
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
       meta: Optional[dict] = None)
```

Initializes a Dialog object with the given parameters.

### Methods

- `to_dict()`: Returns a dictionary representation of the Dialog object.
- `add_external_data(url: str, filename: str, mimetype: str) -> None`: Adds external data to the dialog.
- `add_inline_data(body: str, filename: str, mimetype: str) -> None`: Adds inline data to the dialog.
- `is_external_data() -> bool`: Checks if the dialog is an external data dialog.
- `is_inline_data() -> bool`: Checks if the dialog is an inline data dialog.
- `is_text() -> bool`: Checks if the dialog is a text dialog.
- `is_audio() -> bool`: Checks if the dialog is an audio dialog.
- `is_video() -> bool`: Checks if the dialog is a video dialog.
- `is_email() -> bool`: Checks if the dialog is an email dialog.
- `is_external_data_changed() -> bool`: Checks if the external data dialog's contents have changed.
- `to_inline_data() -> None`: Converts the dialog from an external data dialog to an inline data dialog.

## Party Class

The `Party` class represents a party in the system.

### Constructor

```python
Party(tel: Optional[str] = None,
      stir: Optional[str] = None,
      mailto: Optional[str] = None,
      name: Optional[str] = None,
      validation: Optional[str] = None,
      gmlpos: Optional[str] = None,
      civicaddress: Optional[CivicAddress] = None,
      uuid: Optional[str] = None,
      role: Optional[str] = None,
      contact_list: Optional[str] = None,
      meta: Optional[dict] = None)
```

Initializes a Party object with the given parameters.

### Methods

- `to_dict()`: Returns a dictionary representation of the Party object.

## PartyHistory Class

The `PartyHistory` class represents the history of a party's participation in a dialog.

### Constructor

```python
PartyHistory(party: int, event: str, time: datetime)
```

Initializes a PartyHistory object with the given parameters.

### Methods

- `to_dict()`: Returns a dictionary representation of the PartyHistory object.

## Constants

- `MIME_TYPES`: A list of supported MIME types for dialogs.

```python
MIME_TYPES = [
    "text/plain",
    "audio/x-wav",
    "audio/x-mp3",
    "audio/x-mp4",
    "audio/ogg",
    "video/x-mp4",
    "video/ogg",
    "multipart/mixed",
    "message/external-body",
]
```


## Contributing

Contributions to the vCon library are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the MIT License:

MIT License

Copyright (c) 2023 Thomas McCarthy-Howe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contact

For questions or support, please contact:

Thomas McCarthy-Howe
Email: ghostofbasho@gmail.com