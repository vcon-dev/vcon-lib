# Vcon Library Documentation

The Vcon library provides a Python implementation for working with vCon (Virtualized Conversation) containers. vCons are used to store and manage conversation data, including metadata, dialog, analysis, and attachments.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Vcon Class](#vcon-class)
4. [Methods](#methods)
5. [Properties](#properties)
6. [Utility Methods](#utility-methods)

## Installation

[Instructions for installing the library would go here]

## Usage

```python
from vcon import Vcon

# Create a new vCon
vcon = Vcon.build_new()

# Add a party
vcon.add_party({"name": "Alice", "tel": "+1234567890"})

# Add a dialog
vcon.add_dialog({
    "type": "text",
    "start": "2023-07-21T10:00:00Z",
    "parties": [0],
    "body": "Hello, world!",
    "encoding": "none"
})

# Add an attachment
vcon.add_attachment(type="document", body="Sample content", encoding="none")

# Add analysis
vcon.add_analysis(
    type="sentiment",
    dialog=[0],
    vendor="SentimentAnalyzer",
    body={"score": 0.8},
    encoding="json"
)

# Convert to JSON
json_data = vcon.to_json()
```

## Vcon Class

The `Vcon` class is the main class for working with vCon containers.

### Constructor

- `Vcon(vcon_dict={})`: Creates a new Vcon instance from a dictionary.

### Class Methods

- `build_from_json(json_string)`: Creates a Vcon instance from a JSON string.
- `build_new()`: Creates a new empty Vcon instance with default values.

## Methods

### add_tag(tag_name, tag_value)

Adds a tag to the vCon.

### add_attachment(body, type, encoding="none")

Adds an attachment to the vCon.

### add_analysis(type, dialog, vendor, body, encoding="none", extra={})

Adds analysis data to the vCon.

### add_party(party)

Adds a party to the vCon.

### add_dialog(dialog)

Adds a dialog to the vCon.

### to_json()

Converts the vCon to a JSON string.

### to_dict()

Converts the vCon to a dictionary.

### dumps()

Alias for `to_json()`.

## Properties

- `tags`: Returns the tags attachment.
- `parties`: Returns the list of parties.
- `dialog`: Returns the list of dialogs.
- `attachments`: Returns the list of attachments.
- `analysis`: Returns the list of analysis data.
- `uuid`: Returns the UUID of the vCon.
- `vcon`: Returns the vCon version.
- `subject`: Returns the subject of the vCon.
- `created_at`: Returns the creation timestamp.
- `updated_at`: Returns the last update timestamp.
- `redacted`: Returns redaction information.
- `appended`: Returns appended information.
- `group`: Returns the group information.
- `meta`: Returns metadata information.

## Utility Methods

### find_attachment_by_type(type)

Finds an attachment by its type.

### find_analysis_by_type(type)

Finds analysis data by its type.

### find_party_index(by, val)

Finds the index of a party based on a key-value pair.

### find_dialog(by, val)

Finds a dialog based on a key-value pair.

### get_tag(tag_name)

Gets the value of a specific tag.

### uuid8_domain_name(domain_name)

Generates a version 8 UUID based on a domain name.

### uuid8_time(custom_c_62_bits)

Generates a version 8 UUID based on a custom 62-bit value.

This documentation provides an overview of the Vcon library's functionality. For more detailed information on each method and property, refer to the inline comments and docstrings in the source code.
