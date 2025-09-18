import base64
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime, timezone
from mutagen.mp3 import MP3


# Create a new vCon
vcon = Vcon.build_new()

# Add participants
caller = Party(tel="+1234567890", name="Alice", role="caller")
agent = Party(tel="+1987654321", name="Bob", role="agent")
vcon.add_party(caller)
vcon.add_party(agent)


# Add a dialog entry with the caller as the originator, and the agent as the recipient
# The parties are the indices of the parties in the vCon
# The filename is the name of the file in the vCon
filename = "c81c84f5-bb32-40a6-8a26-76749cc642c2.mp3"
# Base64 encode the file
with open(filename, "rb") as file:
    data = base64.b64encode(file.read()).decode()

# calculate the duration of the recording from the MP3 file
audio = MP3(filename)
duration = audio.info.length  # Duration in seconds

dialog = Dialog(
    type="recording",
    start=datetime.now(timezone.utc).isoformat(),
    duration=duration,
    parties=[0, 1],  # Indices of the parties
    originator=0,  # Caller is the originator
)
new_filename = "new_" + filename
dialog.add_inline_data(body=data, filename=new_filename, mimetype="audio/mp3")
vcon.add_dialog(dialog)


# Validate the vCon
is_valid, errors = vcon.is_valid()
if is_valid:
    print("vCon is valid")
else:
    print("Validation errors:", errors)

# Save the vCon to a file
output_filename = "packed.vcon.json"
with open(output_filename, "w") as file:
    file.write(vcon.to_json())

# Get the dialog and the inline data
dialog = vcon.find_dialog(by="type", val="recording")
inline_data = dialog.body
dialog_filename = dialog.filename

# Decode the inline data and save it to a file with the same name as the original file
with open(dialog_filename, "wb") as file:
    file.write(base64.b64decode(inline_data))
