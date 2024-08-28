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
