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

# Create a new vcon
vcon = Vcon.build_new()

# Add a party to the vcon
party = Party(mailto="example@example.com")
vcon.add_party(party)

# Add a dialog to the vcon
dialog = {
    "id": "dialog1",
    "type": "text",
    "start": "2024-05-03T20:13:48.414984",
    "parties": [0],
    "body": "Hello, world!",
    "encoding": "none"
}
vcon.add_dialog(dialog)

# Add an attachment to the vcon
attachment = {
    "type": "tags",
    "body": ["tag1:value1", "tag2:value2"],
    "encoding": "json"
}
vcon.add_attachment(attachment)

# Add analysis to the vcon
analysis = {
    "type": "transcript",
    "dialog": 0,
    "vendor": "openai",
    "body": {"key": "value"},
    "encoding": "json"
}
vcon.add_analysis(analysis)

# Serialize the vcon to JSON
json_string = vcon.to_json()
print(json_string)

# Create a new vcon from the JSON string
new_vcon = Vcon.build_from_json(json_string)

# Print the new vcon's UUID
print(new_vcon.uuid)


## API Reference

For detailed information about the available methods and their usage, please refer to the docstrings in the source code.

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