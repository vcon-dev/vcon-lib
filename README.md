# vCon Python Library

This Python library provides a convenient way to work with vCon (Virtualized Conversation) objects. vCon is a standard for representing conversation data, including metadata, dialog, analysis, and attachments.

## Features

- Create and manipulate vCon objects
- Add parties, dialogs, attachments, and analysis to vCons
- Sign and verify vCons using JWS (JSON Web Signature)
- Generate UUID8 identifiers
- Pack and unpack dialogs
- Add and retrieve tags

## Installation

To install the vCon library, use pip:

```
pip install vcon
```

## Usage
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
import json

# Create a new vCon
vcon = Vcon.build_new()

first_party = Party(name="Alice", tel="+1234567890")
vcon.add_party(first_party)
second_party = Party(name="Bob", tel="+0987654321")
vcon.add_party(second_party)

dialog = Dialog(start="2023-06-01T10:00:00Z",
                parties=[0], 
                type="text",
                body="Hello, world!")

vcon.add_dialog(dialog)


# Add an attachment
vcon.add_attachment(
    body={"call_center": "yarmouth"},
    type="routing"
)

# Add analysis
vcon.add_analysis(
    type="sentiment",
    dialog=[0],
    vendor="AnalysisCompany",
    body={"sentiment": "positive"}
)

# Add a tag
vcon.add_tag("importance", "high")

# Sign the vCon
private_key, public_key = Vcon.generate_key_pair()
vcon.sign(private_key)

# Verify the signature
is_valid = vcon.verify(public_key)

# Convert to JSON
vcon_json = vcon.to_json()

# Create a vCon from JSON
new_vcon = Vcon.build_from_json(vcon_json)

# Print the vCon
print(json.dumps(new_vcon.to_json(), indent=4))


## API Reference

The vcon library provides functionality for working with vCon (Virtualized Conversation) objects.

## Modules

### vcon

The main module containing the Vcon class.

#### Classes

##### Vcon

```python
class Vcon(vcon_dict={})
```

The main class for working with vCon objects.

- `vcon_dict`: A dictionary representing a vCon (default: empty dict)

###### Class Methods

```python
@classmethod
def build_from_json(json_string: str) -> Vcon
```

Initialize a Vcon object from a JSON string.

- `json_string`: A JSON string representing a vCon
- Returns: A Vcon object

```python
@classmethod
def build_new() -> Vcon
```

Initialize a Vcon object with default values.

- Returns: A Vcon object

###### Methods

```python
def get_tag(tag_name) -> Optional[dict]
```

Returns the value of a tag by name.

- `tag_name`: The name of the tag
- Returns: The value of the tag or None if not found

```python
def add_tag(tag_name, tag_value) -> None
```

Adds a tag to the vCon.

- `tag_name`: The name of the tag
- `tag_value`: The value of the tag

```python
def find_attachment_by_type(type: str) -> Optional[dict]
```

Finds an attachment by type.

- `type`: The type of the attachment
- Returns: The attachment or None if not found

```python
def add_attachment(*, body: Union[dict, list, str], type: str, encoding="none") -> None
```

Adds an attachment to the vCon.

- `body`: The body of the attachment
- `type`: The type of the attachment
- `encoding`: The encoding of the attachment body (default: "none")

```python
def find_analysis_by_type(type) -> Any | None
```

Finds an analysis by type.

- `type`: The type of the analysis
- Returns: The analysis or None if not found

```python
def add_analysis(*, type: str, dialog: Union[list, int], vendor: str, body: Union[dict, list, str], encoding="none", extra={}) -> None
```

Adds analysis data to the vCon.

- `type`: The type of the analysis
- `dialog`: The dialog(s) associated with the analysis
- `vendor`: The vendor of the analysis
- `body`: The body of the analysis
- `encoding`: The encoding of the body (default: "none")
- `extra`: Extra key-value pairs to include in the analysis

```python
def add_party(party: Party) -> None
```

Adds a party to the vCon.

- `party`: The party to add

```python
def find_party_index(by: str, val: str) -> Optional[int]
```

Find the index of a party in the vCon given a key-value pair.

- `by`: The key to look for
- `val`: The value to look for
- Returns: The index of the party if found, None otherwise

```python
def find_dialog(by: str, val: str) -> Optional[dict]
```

Find a dialog in the vCon given a key-value pair.

- `by`: The key to look for
- `val`: The value to look for
- Returns: The dialog if found, None otherwise

```python
def add_dialog(dialog: dict) -> None
```

Add a dialog to the vCon.

- `dialog`: The dialog to add

```python
def to_json() -> str
```

Serialize the vCon to a JSON string.

- Returns: A JSON string representation of the vCon

```python
def to_dict() -> dict
```

Serialize the vCon to a dictionary.

- Returns: A dictionary representation of the vCon

```python
def dumps() -> str
```

Alias for `to_json()`.

- Returns: A JSON string representation of the vCon

```python
def sign(private_key) -> None
```

Sign the vCon using JWS.

- `private_key`: The private key used for signing

```python
def verify(public_key) -> bool
```

Verify the JWS signature of the vCon.

- `public_key`: The public key used for verification
- Returns: True if the signature is valid, False otherwise

```python
@classmethod
def generate_key_pair() -> tuple
```

Generate a new RSA key pair for signing vCons.

- Returns: A tuple containing the private key and public key

###### Properties

- `tags`: Returns the tags attachment.
- `parties`: Returns the list of parties.
- `dialog`: Returns the list of dialogs.
- `attachments`: Returns the list of attachments.
- `analysis`: Returns the list of analyses.
- `uuid`: Returns the UUID of the vCon.
- `vcon`: Returns the vCon version.
- `subject`: Returns the subject of the vCon.
- `created_at`: Returns the creation timestamp of the vCon.
- `updated_at`: Returns the last update timestamp of the vCon.
- `redacted`: Returns the redacted information of the vCon.
- `appended`: Returns the appended information of the vCon.
- `group`: Returns the group information of the vCon.
- `meta`: Returns the metadata of the vCon.

### party

Module containing the Party class.

#### Classes

##### Party

```python
class Party(tel: Optional[str] = None, stir: Optional[str] = None, mailto: Optional[str] = None, name: Optional[str] = None, validation: Optional[str] = None, gmlpos: Optional[str] = None, civicaddress: Optional[CivicAddress] = None, uuid: Optional[str] = None, role: Optional[str] = None, contact_list: Optional[str] = None, meta: Optional[dict] = None)
```

Represents a party in a vCon.

- `tel`: Telephone number of the party
- `stir`: STIR identifier of the party
- `mailto`: Email address of the party
- `name`: Display name of the party
- `validation`: Validation information of the party
- `gmlpos`: GML position of the party
- `civicaddress`: Civic address of the party
- `uuid`: UUID of the party
- `role`: Role of the party
- `contact_list`: Contact list of the party
- `meta`: Additional metadata for the party

###### Methods

```python
def to_dict() -> dict
```

Returns a dictionary representation of the Party object.

- Returns: A dictionary containing the Party object's attributes

##### PartyHistory

```python
class PartyHistory(party: int, event: str, time: datetime)
```

Represents the history of a party's participation in a dialog.

- `party`: Index of the party
- `event`: Event type (e.g. "join", "leave")
- `time`: Time of the event

###### Methods

```python
def to_dict() -> dict
```

Returns a dictionary representation of the PartyHistory object.

- Returns: A dictionary containing the PartyHistory object's attributes

### dialog

Module containing the Dialog class.

#### Classes

##### Dialog

```python
class Dialog(type: str, start: datetime, parties: List[int], originator: Optional[int] = None, mimetype: Optional[str] = None, filename: Optional[str] = None, body: Optional[str] = None, encoding: Optional[str] = None, url: Optional[str] = None, alg: Optional[str] = None, signature: Optional[str] = None, disposition: Optional[str] = None, party_history: Optional[List[PartyHistory]] = None, transferee: Optional[int] = None, transferor: Optional[int] = None, transfer_target: Optional[int] = None, original: Optional[int] = None, consultation: Optional[int] = None, target_dialog: Optional[int] = None, campaign: Optional[str] = None, interaction: Optional[str] = None, skill: Optional[str] = None, duration: Optional[float] = None)
```

Represents a dialog in a vCon.

- `type`: The type of the dialog (e.g. "text", "audio", etc.)
- `start`: The start time of the dialog
- `parties`: The parties involved in the dialog
- `originator`: The party that originated the dialog
- `mimetype`: The MIME type of the dialog body
- `filename`: The filename of the dialog body
- `body`: The body of the dialog
- `encoding`: The encoding of the dialog body
- `url`: The URL of the dialog
- `alg`: The algorithm used to sign the dialog
- `signature`: The signature of the dialog
- `disposition`: The disposition of the dialog
- `party_history`: The history of parties involved in the dialog
- `transferee`: The party that the dialog was transferred to
- `transferor`: The party that transferred the dialog
- `transfer_target`: The target of the transfer
- `original`: The original dialog
- `consultation`: The consultation dialog
- `target_dialog`: The target dialog
- `campaign`: The campaign that the dialog is associated with
- `interaction`: The interaction that the dialog is associated with
- `skill`: The skill that the dialog is associated with
- `duration`: The duration of the dialog

###### Methods

```python
def to_dict() -> dict
```

Returns a dictionary representation of the Dialog object.

- Returns: A dictionary containing the Dialog object's attributes

```python
def add_external_data(url: str, filename: str, mimetype: str) -> None
```

Add external data to the dialog.

- `url`: The URL of the external data
- `filename`: The filename of the external data
- `mimetype`: The MIME type of the external data

```python
def add_inline_data(body: str, filename: str, mimetype: str) -> None
```

Add inline data to the dialog.

- `body`: The body of the inline data
- `filename`: The filename of the inline data
- `mimetype`: The MIME type of the inline data

```python
def is_external_data() -> bool
```

Check if the dialog is an external data dialog.

- Returns: True if the dialog is an external data dialog, False otherwise

```python
def is_inline_data() -> bool
```

Check if the dialog is an inline data dialog.

- Returns: True if the dialog is an inline data dialog, False otherwise

```python
def is_text() -> bool
```

Check if the dialog is a text dialog.

- Returns: True if the dialog is a text dialog, False otherwise

```python
def is_audio() -> bool
```

Check if the dialog is an audio dialog.

- Returns: True if the dialog is an audio dialog, False otherwise

```python
def is_video() -> bool
```

Check if the dialog is a video dialog.

- Returns: True if the dialog is a video dialog, False otherwise

```python
def is_email() -> bool
```

Check if the dialog is an email dialog.

- Returns: True if the dialog is an email dialog, False otherwise

```python
def is_external_data_changed() -> bool
```

Check if the external data dialog contents have changed.

- Returns: True if the contents have changed, False otherwise

```python
def to_inline_data() -> None
```

Convert the dialog from an external data dialog to an inline data dialog.

### civic_address

Module containing the CivicAddress class.

#### Classes

##### CivicAddress

```python
class CivicAddress(country: Optional[str] = None, a1: Optional[str] = None, a2: Optional[str] = None, a3: Optional[str] = None, a4: Optional[str] = None, a5: Optional[str] = None, a6: Optional[str] = None, prd: Optional[str] = None, pod: Optional[str] = None, sts: Optional[str] = None, hno: Optional[str] = None, hns: Optional[str] = None, lmk: Optional[str] = None, loc: Optional[str] = None, flr: Optional[str] = None, nam: Optional[str] = None, pc: Optional[str] = None)
```

Represents a civic address.

- `country`: Country code (ISO 3166-1 alpha-2)
- `a1`: Administrative area 1 (e.g. state or province)
- `a2`: Administrative area 2 (e.g. county or municipality)
- `a3`: Administrative area 3 (e.g. city or town)
- `a4`: Administrative area 4 (e.g. neighborhood or district)
- `a5`: Administrative area 5 (e.g. postal code)
- `a6`: Administrative area 6 (e.g. building or floor)
- `prd`: Premier (e.g. department or suite number)
- `pod`: Post office box identifier
- `sts`: Street name
- `hno`: House number
- `hns`: House name
- `lmk`: Landmark name
- `loc`: Location name
- `flr`: Floor
- `nam`: Name of the location
- `pc`: Postal code

###### Methods

```python
def to_dict() -> dict[str, Optional[str]]
```

Convert the CivicAddress object to a dictionary.

- Returns: A dictionary of the object's attributes

This Markdown version of the API documentation should be easier to read and integrate into various documentation systems or README files. It provides a comprehensive overview of the classes, methods, and attributes available in the vcon library.


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