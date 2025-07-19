from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from typing import Union

import pytest
import json
import time
import base64
import tempfile
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import requests

from vcon.vcon import Attachment

"""
This covers testing the main methods of the Vcon class, including:

Building from JSON
Building a new instance
Adding and retrieving tags
Adding and finding attachments
Adding and finding analysis
Adding parties and dialogs
Serializing to JSON
Generating a UUID8 based on a domain name
"""


test_vcon_string = (
    '{"uuid":"0192aa73-e702-8cef-9dd8-dd37220d739c","vcon":"0.3.0",'
    '"created_at":"2024-10-20T15:02:55.490850+00:00","parties":['
    '{"tel":"+14513886516","mailto":"david.scott@pickrandombusinesstype.com",'
    '"name":"David Scott","meta":{"role":"agent"}},'
    '{"tel":"+16171557264","mailto":"diane.allen@gmail.com","name":"Diane Allen",'
    '"meta":{"role":"customer"}}],"dialog":[{"type":"recording",'
    '"start":"2024-10-20T15:02:54.888840","duration":52.68,"parties":[0,1],'
    '"mimetype":"audio/x-wav","filename":"bb1489ad-0b45-47a0-bca6-de124da39a3a.mp3",'
    '"body":"","encoding":"base64url","alg":"sha256",'
    '"signature":"JBzeZEPDNVm8iPEeout0UK-B2Fp6JzeQxqy70SvM_MU=",'
    '"disposition":"ANSWERED"}],"attachments":[{"type":"generation_info","body":'
    '{"agent_name":"David Scott","customer_name":"Diane Allen",'
    '"business":"Auto Repair Shop","problem":"billing","emotion":"disappointed",'
    '"prompt":"\\nGenerate a fake conversation between a customer and an agent.'
    "\\nThe agent should introduce themselves, their company and give the customer"
    "\\ntheir name. The agent should ask for the customer's name.\\nAs part of the "
    "conversation, have the agent ask for two pieces of\\npersonal information.  "
    "Spell out numbers. For example, 1000 should be\\nsaid as one zero zero zero, "
    "not one thousand. The conversation should be\\nat least 10 lines long and be "
    "complete. At the end\\nof the conversation, the agent should thank the customer "
    "for their time\\nand end the conversation. Return the conversation formatted "
    "\\nlike the following example:\\n\\n{'conversation': \\n    [\\n    {'speaker': "
    "'Agent', 'message': 'xxxxx'}, \\n    {'speaker': 'Customer', 'message': "
    "\\\"xxxxx.\\\"}, \\n    {'speaker': 'Agent', 'message': \\\"xxxxxx\\\"}\\n    ] "
    "\\n}\\n\\n\\nIn this conversation, the agent's name is David Scott and the "
    "customer's name is Diane Allen.  The conversation is about a random business "
    '(a Auto Repair Shop ) and is a conversation about billing.",'
    '"created_on":"2024-10-20T15:02:55.490740","model":"gpt-4o-mini"},'
    '"encoding":"none"}],"analysis":[{"type":"analysis_info","dialog":0,'
    '"vendor":"openai","body":[{"speaker":"Agent","message":"Hello! My name is '
    "David Scott, and I'm with Quick Fix Auto Repair. How can I assist you today?\"},"
    '{"speaker":"Customer","message":"Hi David, I\'m Diane Allen. I have a question '
    'about my recent bill."},{"speaker":"Agent","message":"Of course, Diane! I\'d be '
    'happy to help you with that. Can you please provide me with the invoice number?"},'
    '{"speaker":"Customer","message":"Yes, the invoice number is one two three four '
    'five."},{"speaker":"Agent","message":"Thank you for that information. And could '
    'you also confirm your phone number for me?"},{"speaker":"Customer","message":'
    '"Sure, my phone number is two zero two, five six seven, eight nine zero zero."},'
    '{"speaker":"Agent","message":"Great, thank you, Diane. Let me look up your '
    'invoice for a moment."},{"speaker":"Customer","message":"No problem. I appreciate '
    'your help."},{"speaker":"Agent","message":"I see your invoice now. It looks like '
    'there was an extra charge for parts. Would you like me to explain that?"},'
    '{"speaker":"Customer","message":"Yes, I would appreciate that."},'
    '{"speaker":"Agent","message":"The extra charge was for a new battery that was '
    "installed. Thank you for your patience, and please let me know if you have any "
    'more questions."}],"encoding":"none","vendor_schema":{"model":"gpt-4o-mini",'
    '"prompt":"\\nGenerate a fake conversation between a customer and an agent.'
    "\\nThe agent should introduce themselves, their company and give the customer"
    "\\ntheir name. The agent should ask for the customer's name.\\nAs part of the "
    "conversation, have the agent ask for two pieces of\\npersonal information.  "
    "Spell out numbers. For example, 1000 should be\\nsaid as one zero zero zero, "
    "not one thousand. The conversation should be\\nat least 10 lines long and be "
    "complete. At the end\\nof the conversation, the agent should thank the customer "
    "for their time\\nand end the conversation. Return the conversation formatted "
    "\\nlike the following example:\\n\\n{'conversation': \\n    [\\n    {'speaker': "
    "'Agent', 'message': 'xxxxx'}, \\n    {'speaker': 'Customer', 'message': "
    "\\\"xxxxx.\\\"}, \\n    {'speaker': 'Agent', 'message': \\\"xxxxxx\\\"}\\n    ] "
    "\\n}\\n\\n\\nIn this conversation, the agent's name is David Scott and the "
    "customer's name is Diane Allen.  The conversation is about a random business "
    '(a Auto Repair Shop ) and is a conversation about billing."}}]}'
)

GITHUB_WAV_URL = "https://github.com/vcon-dev/vcon-lib/raw/841eca9198397e768f478569a3595a70c6e892cc/tests/sample.mp3"


# Helper function to get the duration of an external audio file. Account for WAV and MP3 files, which have different formats.
# Download the file and calculate the duration.
def get_audio_duration(url: str) -> Union[float, None]:
    """
    Downloads an audio file and calculates its duration.s
    Supports WAV and MP3 formats.

    Args:
        url (str): URL of the audio file

    Returns:
        float: Duration in seconds, or None if file format not supported
    """
    import requests
    import io
    import wave
    from mutagen.mp3 import MP3

    try:
        # Download the file
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to download file from {url}")
            return None

        audio_data = io.BytesIO(response.content)

        # Calculate duration based on file type
        if url.lower().endswith(".wav"):
            with wave.open(audio_data) as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
                print(f"Duration: {duration}")
                return duration

        elif url.lower().endswith(".mp3"):
            audio_data.seek(0)
            mp3 = MP3(audio_data)
            print(f"Duration: {mp3.info.length}")
            return mp3.info.length

        return None

    except Exception:
        return None


def test_build_from_json() -> None:
    """
    Test that we can create a Vcon object from a JSON string.

    The JSON string is a sample vCon object that contains a single dialog
    with several turns.

    The test verifies that the resulting Vcon object has the expected UUID,
    vcon version, and created_at timestamp.
    """
    vcon = Vcon.build_from_json(test_vcon_string)
    assert vcon.uuid == "0192aa73-e702-8cef-9dd8-dd37220d739c"
    assert vcon.vcon == "0.3.0"
    assert vcon.created_at == "2024-10-20T15:02:55.490850+00:00"


def test_build_new() -> None:
    vcon = Vcon.build_new()
    assert vcon.uuid is not None
    assert vcon.vcon == "0.3.0"
    assert vcon.created_at is not None


def test_tags() -> None:
    vcon = Vcon.build_new()
    assert vcon.tags is None

    vcon.add_tag("test_tag", "test_value")
    assert vcon.get_tag("test_tag") == "test_value"


def test_add_attachment():
    vcon = Vcon()
    attachment = vcon.add_attachment(type="test_type", body="test_body")

    assert len(vcon.vcon_dict["attachments"]) == 1
    assert vcon.vcon_dict["attachments"][0] == {
        "type": "test_type",
        "body": "test_body",
        "encoding": "none",
    }
    assert isinstance(attachment, Attachment)


def test_add_analysis() -> None:
    vcon = Vcon.build_new()
    vcon.add_analysis(
        type="test_type", dialog=[1, 2], vendor="test_vendor", body={"key": "value"}
    )
    analysis = vcon.find_analysis_by_type("test_type")
    assert analysis["body"] == {"key": "value"}
    assert analysis["dialog"] == [1, 2]
    assert analysis["vendor"] == "test_vendor"


def test_add_dialog() -> None:
    # Given
    vcon = Vcon.build_new()
    dialog = Dialog(
        start="2023-06-01T10:00:00Z", parties=[0], type="text", body="Hello, world!"
    )
    vcon.add_dialog(dialog)

    # When
    found_dialog = vcon.find_dialog("type", "text")

    # Then these dialogs should be the same values. Check
    assert found_dialog.to_dict() == dialog.to_dict()


def test_to_json() -> None:
    vcon = Vcon.build_new()
    json_string = vcon.to_json()
    assert json.loads(json_string) == vcon.to_dict()


def test_uuid8_domain_name() -> None:
    uuid8 = Vcon.uuid8_domain_name("test.com")
    assert uuid8[14] == "8"  # check version is 8


def test_get_tag() -> None:
    vcon = Vcon.build_new()
    vcon.add_tag("test_tag", "test_value")
    assert vcon.get_tag("test_tag") == "test_value"
    assert vcon.get_tag("nonexistent_tag") is None


def test_find_attachment_by_type() -> None:
    vcon = Vcon.build_new()
    vcon.add_attachment(body={"key": "value"}, type="test_type")
    assert vcon.find_attachment_by_type("test_type") == {
        "type": "test_type",
        "body": {"key": "value"},
        "encoding": "none",
    }
    assert vcon.find_attachment_by_type("nonexistent_type") is None


def test_find_analysis_by_type() -> None:
    vcon = Vcon.build_new()
    vcon.add_analysis(
        type="test_type", dialog=[1, 2], vendor="test_vendor", body={"key": "value"}
    )
    assert vcon.find_analysis_by_type("test_type") == {
        "type": "test_type",
        "dialog": [1, 2],
        "vendor": "test_vendor",
        "body": {"key": "value"},
        "encoding": "none",
    }
    assert vcon.find_analysis_by_type("nonexistent_type") is None


def test_find_party_index() -> None:
    vcon = Vcon.build_new()
    p = Party(name="Alice")
    vcon.add_party(p)
    assert vcon.find_party_index("name", "Alice") == 0
    assert vcon.find_party_index("name", "Bob") is None
    assert vcon.find_party_index("nonexistent_field", "Alice") is None
    assert vcon.find_party_index("name", "nonexistent_party") is None

    vcon.add_party(Party(name="Bob"))
    assert vcon.find_party_index("name", "Bob") == 1
    assert vcon.find_party_index("name", "Alice") == 0

    assert vcon.find_party_index("nonexistent_field", "Alice") is None

    vcon.add_party(Party(name="Charlie"))
    assert vcon.find_party_index("name", "Charlie") == 2
    assert vcon.find_party_index("nonexistent_field", "Alice") is None


def test_properties() -> None:
    vcon = Vcon.build_from_json(test_vcon_string)

    assert vcon.uuid == "0192aa73-e702-8cef-9dd8-dd37220d739c"
    assert vcon.created_at == "2024-10-20T15:02:55.490850+00:00"
    assert len(vcon.parties) == 2

    assert vcon.parties[0].to_dict() == {
        "tel": "+14513886516",
        "mailto": "david.scott@pickrandombusinesstype.com",
        "name": "David Scott",
        "meta": {"role": "agent"},
    }
    assert vcon.parties[1].to_dict() == {
        "tel": "+16171557264",
        "mailto": "diane.allen@gmail.com",
        "name": "Diane Allen",
        "meta": {"role": "customer"},
    }

    assert len(vcon.dialog) == 1
    assert vcon.dialog[0] == {
        "type": "recording",
        "start": "2024-10-20T15:02:54.888840",
        "duration": 52.68,
        "parties": [0, 1],
        "mimetype": "audio/x-wav",
        "filename": "bb1489ad-0b45-47a0-bca6-de124da39a3a.mp3",
        "body": "",
        "encoding": "base64url",
        "alg": "sha256",
        "signature": "JBzeZEPDNVm8iPEeout0UK-B2Fp6JzeQxqy70SvM_MU=",
        "disposition": "ANSWERED",
    }

    assert len(vcon.attachments) == 1
    assert vcon.attachments[0]["type"] == "generation_info"
    assert vcon.attachments[0]["encoding"] == "none"
    assert "body" in vcon.attachments[0]

    assert len(vcon.analysis) == 1
    assert vcon.analysis[0]["type"] == "analysis_info"
    assert vcon.analysis[0]["dialog"] == 0
    assert vcon.analysis[0]["vendor"] == "openai"
    assert vcon.analysis[0]["encoding"] == "none"
    assert len(vcon.analysis[0]["body"]) == 11  # 11 conversation turns
    assert vcon.analysis[0]["vendor_schema"]["model"] == "gpt-4o-mini"

    print("All assertions passed!")


def test_to_dict() -> None:
    vcon = Vcon.build_new()
    vcon_dict = vcon.to_dict()
    assert isinstance(vcon_dict, dict)
    assert vcon_dict == json.loads(vcon.to_json())


def test_dumps() -> None:
    vcon = Vcon.build_new()
    json_string = vcon.dumps()
    assert isinstance(json_string, str)
    assert json_string == vcon.to_json()


def test_error_handling() -> None:
    with pytest.raises(json.JSONDecodeError):
        Vcon.build_from_json("invalid_json")


def test_add_and_find_party_index() -> None:
    # Given
    vcon = Vcon.build_new()
    party = Party(mailto="R0Hl4@example.com")

    # When
    vcon.add_party(party)

    # Then
    assert vcon.find_party_index("mailto", "R0Hl4@example.com") == 0
    assert vcon.find_party_index("mailto", "nonexistent_party") is None


def test_find_dialog() -> None:
    # Given
    vcon = Vcon.build_new()
    dialog = Dialog(
        start="2023-06-01T10:00:00Z", parties=[0], type="text", body="Hello, world!"
    )
    vcon.add_dialog(dialog)

    # When
    found_dialog = vcon.find_dialog("type", "text")

    # Then these dialogs should be the same values. Check
    # that the dialog we found is the same as the dialog we added.
    assert found_dialog.to_dict() == dialog.to_dict()


def test_add_special_character_tag() -> None:
    # Given
    vcon = Vcon.build_new()

    # When
    vcon.add_tag("special_tag!@#", "special_value")

    # Then
    assert vcon.get_tag("special_tag!@#") == "special_value"


def test_add_and_find_party_index_by_name() -> None:
    # Given
    vcon = Vcon.build_new()
    party = Party(name="Alice")

    # When
    vcon.add_party(party)

    # Then
    assert vcon.find_party_index("name", "Alice") == 0
    assert vcon.find_party_index("name", "Bob") is None


def test_initializes_with_empty_dict() -> None:
    from src.vcon.vcon import Vcon

    vcon = Vcon()
    assert isinstance(vcon.vcon_dict, dict)
    assert "created_at" in vcon.vcon_dict


def test_initializes_with_datetime_created_at() -> None:
    from src.vcon.vcon import Vcon
    from datetime import datetime

    vcon_dict = {"created_at": datetime.now()}
    vcon = Vcon(vcon_dict)
    assert isinstance(vcon.vcon_dict, dict)
    assert "created_at" in vcon.vcon_dict


def test_initializes_with_created_at_string() -> None:
    from src.vcon.vcon import Vcon
    import datetime

    vcon_dict = {"created_at": "2022-01-01T12:00:00Z"}
    vcon = Vcon(vcon_dict)
    assert isinstance(vcon.vcon_dict, dict)
    assert "created_at" in vcon.vcon_dict
    assert isinstance(vcon.vcon_dict["created_at"], str)


def test_initializes_without_created_at() -> None:
    from src.vcon.vcon import Vcon

    vcon = Vcon({})
    assert isinstance(vcon.vcon_dict, dict)
    assert "created_at" in vcon.vcon_dict


def test_converts_created_at_to_iso_format_when_datetime_provided() -> None:
    from src.vcon.vcon import Vcon
    from datetime import datetime

    test_datetime = datetime(2022, 9, 15, 8, 30, 0)
    vcon = Vcon({"created_at": test_datetime})
    assert "created_at" in vcon.vcon_dict
    assert isinstance(vcon.vcon_dict["created_at"], str)
    assert len(vcon.vcon_dict["created_at"]) == 19


def test_sets_created_at_to_current_time() -> None:
    from src.vcon.vcon import Vcon

    vcon = Vcon()
    assert "created_at" in vcon.vcon_dict
    assert isinstance(vcon.vcon_dict["created_at"], str)
    assert datetime.fromisoformat(vcon.vcon_dict["created_at"])


def test_converts_created_at_to_iso_format_with_timezone() -> None:
    from src.vcon.vcon import Vcon
    from datetime import datetime, timezone

    created_at = datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    vcon_dict = {"created_at": created_at}
    vcon = Vcon(vcon_dict)
    assert "created_at" in vcon.vcon_dict
    assert isinstance(vcon.vcon_dict["created_at"], str)
    assert vcon.vcon_dict["created_at"] == created_at.isoformat()


def test_deep_copy_into_vcon_dict() -> None:
    from src.vcon.vcon import Vcon

    vcon_dict = {"created_at": "2022-01-01T12:00:00Z", "data": {"key": "value"}}
    vcon = Vcon(vcon_dict)
    assert vcon.vcon_dict is not vcon_dict, "vcon_dict should be a deep copy"


def test_add_dialog_external_audio() -> None:
    """Test adding a dialog with an external audio file reference"""
    # Given
    vcon = Vcon.build_new()

    external_dialog = Dialog(
        start="2023-06-01T10:00:00Z",
        parties=[0],
        type="recording",
        url=GITHUB_WAV_URL,
        mimetype="audio/wav",
        duration=get_audio_duration(GITHUB_WAV_URL),
        meta={"direction": "in"},
    )

    # When
    vcon.add_dialog(external_dialog)

    # Then
    found_dialog = vcon.find_dialog("type", "recording")
    assert found_dialog.to_dict() == external_dialog.to_dict()
    assert found_dialog.url == GITHUB_WAV_URL
    assert found_dialog.mimetype == "audio/wav"


def test_add_dialog_inline_audio():
    """Test adding a dialog with inline base64 audio data"""
    # Given
    vcon = Vcon.build_new()

    inline_dialog = Dialog(
        start="2023-06-01T10:00:00Z",
        parties=[0],
        type="recording",
        url=GITHUB_WAV_URL,
        mimetype="audio/mp3",
        duration=get_audio_duration(GITHUB_WAV_URL),
        meta={"direction": "out"},
    )

    # When
    vcon.add_dialog(inline_dialog)

    # Then
    found_dialog = vcon.find_dialog("type", "recording")
    assert found_dialog.to_dict() == inline_dialog.to_dict()
    assert found_dialog.url == GITHUB_WAV_URL
    assert found_dialog.mimetype == "audio/mp3"


def test_add_multiple_dialogs():
    """Test adding and finding multiple dialogs"""
    # Given
    vcon = Vcon.build_new()

    text_dialog = Dialog(
        start="2023-06-01T10:00:00Z", parties=[0], type="text", body="Hello, world!"
    )

    audio_dialog = Dialog(
        start="2023-06-01T10:01:00Z",
        parties=[0, 1],
        type="recording",
        url=GITHUB_WAV_URL,
        mimetype="audio/mp3",
        duration=get_audio_duration(GITHUB_WAV_URL),
    )

    # When
    vcon.add_dialog(text_dialog)
    vcon.add_dialog(audio_dialog)

    # Then
    found_text = vcon.find_dialog("type", "text")
    found_audio = vcon.find_dialog("type", "recording")

    assert found_text.to_dict() == text_dialog.to_dict()
    assert found_audio.to_dict() == audio_dialog.to_dict()
    assert len(vcon.dialog) == 2


def test_is_valid_with_valid_vcon():
    """Test that a valid vCon passes validation"""
    vcon = Vcon.build_from_json(test_vcon_string)
    print(vcon.to_json())
    is_valid, errors = vcon.is_valid()
    print(errors)
    assert is_valid
    assert len(errors) == 0


def test_is_valid_with_missing_required_fields():
    """Test validation fails with missing required fields"""
    vcon = Vcon()
    vcon.vcon_dict = {}  # Empty vCon
    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert len(errors) == 3  # uuid, vcon, created_at
    assert "Missing required field: uuid" in errors
    assert "Missing required field: vcon" in errors
    assert "Missing required field: created_at" in errors


def test_is_valid_with_invalid_created_at():
    """Test validation fails with invalid created_at format"""
    vcon = Vcon.build_new()
    vcon.vcon_dict["created_at"] = "invalid-date"
    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert "Invalid created_at format" in errors[0]


def test_is_valid_with_invalid_dialog_party_reference():
    """Test validation fails with invalid party reference in dialog"""
    vcon = Vcon.build_new()
    vcon.add_party(Party(name="Test Party"))  # Add one party (index 0)

    # Add dialog referencing non-existent party (index 1)
    dialog = Dialog(
        type="text",
        start="2023-06-01T10:00:00Z",
        parties=[0, 1],  # Party index 1 doesn't exist
        body="Test message",
    )
    vcon.add_dialog(dialog)

    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert any("invalid party index: 1" in error for error in errors)


def test_is_valid_with_invalid_analysis_dialog_reference():
    """Test validation fails with invalid dialog reference in analysis"""
    vcon = Vcon.build_new()

    # Add analysis referencing non-existent dialog
    vcon.add_analysis(
        type="test_type",
        dialog=0,  # Dialog index 0 doesn't exist
        vendor="test_vendor",
        body={"key": "value"},
    )

    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert any("invalid dialog index: 0" in error for error in errors)


def test_is_valid_with_invalid_mimetype():
    """Test validation fails with invalid mimetype in dialog"""
    vcon = Vcon.build_new()

    # Add dialog with invalid mimetype
    dialog = Dialog(
        type="text", start="2023-06-01T10:00:00Z", parties=[], mimetype="invalid/type"
    )
    vcon.add_dialog(dialog)

    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert any("Dialog at index 0 has an invalid or missing mimetype" in error for error in errors)


def test_validate_json_with_valid_vcon():
    """Test validation of valid vCon JSON string"""
    is_valid, errors = Vcon.validate_json(test_vcon_string)
    assert is_valid
    assert len(errors) == 0


def test_validate_json_with_invalid_json():
    """Test validation fails with invalid JSON"""
    is_valid, errors = Vcon.validate_json("invalid json")
    assert not is_valid
    assert len(errors) == 1
    assert "Invalid JSON format" in errors[0]


def test_validate_json_with_invalid_vcon():
    """Test validation fails with valid JSON but invalid vCon"""
    invalid_vcon = '{"some": "json"}'
    is_valid, errors = Vcon.validate_json(invalid_vcon)
    assert not is_valid
    assert len(errors) > 0
    assert "Missing required field" in errors[0]


def test_validate_file_with_valid_vcon(tmp_path):
    """Test validation of valid vCon file"""
    # Create a temporary file with valid vCon
    file_path = tmp_path / "valid_vcon.json"
    with open(file_path, "w") as f:
        f.write(test_vcon_string)

    is_valid, errors = Vcon.validate_file(str(file_path))
    assert is_valid
    assert len(errors) == 0


def test_validate_file_with_nonexistent_file():
    """Test validation fails with nonexistent file"""
    is_valid, errors = Vcon.validate_file("nonexistent.json")
    assert not is_valid
    assert len(errors) == 1
    assert "File not found" in errors[0]


def test_validate_file_with_invalid_json(tmp_path):
    """Test validation fails with invalid JSON file"""
    # Create a temporary file with invalid JSON
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w") as f:
        f.write("invalid json")

    is_valid, errors = Vcon.validate_file(str(file_path))
    assert not is_valid
    assert len(errors) == 1
    assert "Invalid JSON format" in errors[0]


def test_validate_file_with_invalid_vcon(tmp_path):
    """Test validation fails with valid JSON but invalid vCon"""
    # Create a temporary file with invalid vCon
    file_path = tmp_path / "invalid_vcon.json"
    with open(file_path, "w") as f:
        f.write('{"some": "json"}')

    is_valid, errors = Vcon.validate_file(str(file_path))
    assert not is_valid
    assert len(errors) > 0
    assert "Missing required field" in errors[0]


def test_load_from_file(tmp_path):
    """Test loading a vCon from a file"""
    # Create a temporary file with valid vCon
    file_path = tmp_path / "valid_vcon.json"
    with open(file_path, "w") as f:
        f.write(test_vcon_string)

    vcon = Vcon.load(str(file_path))
    assert isinstance(vcon, Vcon)
    assert vcon.uuid == "0192aa73-e702-8cef-9dd8-dd37220d739c"
    assert vcon.vcon == "0.3.0"


def test_load_from_file_not_found():
    """Test loading from a non-existent file raises FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        Vcon.load("nonexistent.json")


def test_load_from_file_invalid_json(tmp_path):
    """Test loading from a file with invalid JSON raises JSONDecodeError"""
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w") as f:
        f.write("invalid json")

    with pytest.raises(json.JSONDecodeError):
        Vcon.load(str(file_path))


@pytest.mark.vcr()
def test_load_from_url():
    """Test loading a vCon from a URL"""
    # Using a mock URL that returns a valid vCon JSON
    url = "https://example.com/vcon.json"
    with pytest.raises(requests.exceptions.RequestException):
        # This will fail since the URL doesn't exist, but it tests the URL handling
        Vcon.load(url)


def test_load_detects_file_vs_url() -> None:
    """Test that load() correctly differentiates between files and URLs"""
    assert Vcon.load.__doc__ is not None
    file_path = "test.json"
    url = "https://example.com/test.json"
    
    # Mock the underlying methods to verify they're called correctly
    original_load_from_file = Vcon.load_from_file
    original_load_from_url = Vcon.load_from_url
    
    try:
        # Replace methods with mocks as class methods so they bind correctly
        Vcon.load_from_file = classmethod(lambda cls, path, property_handling=None: path)
        Vcon.load_from_url = classmethod(lambda cls, url, property_handling=None: url)
        
        # Test file path
        result = Vcon.load(file_path)
        assert result == file_path
        
        # Test URL
        result = Vcon.load(url)
        assert result == url
    finally:
        # Restore original methods
        Vcon.load_from_file = original_load_from_file
        Vcon.load_from_url = original_load_from_url
        

def test_save_to_file(tmp_path):
    """Test saving a vCon to a file"""
    # Create a vCon with known content
    vcon = Vcon.build_from_json(test_vcon_string)
    
    # Save to a temporary file
    file_path = tmp_path / "saved_vcon.json"
    vcon.save_to_file(str(file_path))
    
    # Verify the file exists and contains correct content
    assert file_path.exists()
    with open(file_path, 'r') as f:
        saved_content = f.read()
    assert json.loads(saved_content) == json.loads(vcon.to_json())


def test_save_to_file_permission_error(tmp_path):
    """Test saving to a file with no write permissions raises IOError"""
    vcon = Vcon.build_new()
    file_path = tmp_path / "readonly.json"
    
    # Create a read-only directory
    file_path.parent.chmod(0o444)
    
    with pytest.raises(IOError):
        vcon.save_to_file(str(file_path))


@pytest.mark.vcr()
def test_post_to_url():
    """Test posting a vCon to a URL"""
    vcon = Vcon.build_new()
    url = "https://httpbin.org/post"  # Test endpoint that echoes back the request
    
    # Test with custom headers
    headers = {
        'x-conserver-api-token': 'test-token',
        'x-custom-header': 'test-value'
    }
    
    response = vcon.post_to_url(url, headers=headers)
    
    # Verify the response
    assert response.status_code == 200
    response_data = response.json()
    
    # Verify the sent data matches our vCon
    assert json.loads(response_data['data']) == json.loads(vcon.to_json())
    
    # Verify headers were sent correctly
    assert response_data['headers']['Content-Type'] == 'application/json'
    assert response_data['headers']['X-Conserver-Api-Token'] == 'test-token'
    assert response_data['headers']['X-Custom-Header'] == 'test-value'


@pytest.mark.vcr()
def test_post_to_url_no_headers():
    """Test posting a vCon to a URL without custom headers"""
    vcon = Vcon.build_new()
    url = "https://httpbin.org/post"
    
    response = vcon.post_to_url(url)
    
    assert response.status_code == 200
    response_data = response.json()
    
    # Verify only default headers were sent
    assert response_data['headers']['Content-Type'] == 'application/json'
    assert 'X-Conserver-Api-Token' not in response_data['headers']


@pytest.mark.vcr()
def test_post_to_url_error():
    """Test posting to an invalid URL raises RequestException"""
    vcon = Vcon.build_new()
    url = "https://nonexistent.example.com"
    
    with pytest.raises(requests.RequestException):
        vcon.post_to_url(url)

# Sample URLs for video files (for testing)
SAMPLE_VIDEOS = {
    "mp4": "https://example.com/sample.mp4",
    "mov": "https://example.com/sample.mov",
    "webm": "https://example.com/sample.webm",
    "avi": "https://example.com/sample.avi",
    "mkv": "https://example.com/sample.mkv",
    "mpeg": "https://example.com/sample.mpeg",
    "flv": "https://example.com/sample.flv"
}

def test_add_video_dialog():
    """Test adding a video dialog to a Vcon."""
    vcon = Vcon.build_new()
    
    # Add a party
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Create a video dialog with basic properties
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],  # First party (index 0)
        mimetype="video/mp4",
        filename="test_video.mp4"
    )
    
    # Add to vCon
    vcon.add_dialog(dialog)
    
    # Verify it was added correctly
    assert len(vcon.dialog) == 1
    assert vcon.dialog[0]["type"] == "video"
    assert vcon.dialog[0]["mimetype"] == "video/mp4"

@pytest.mark.parametrize("format_name,mimetype", [
    ("mp4", "video/mp4"),
    ("mov", "video/quicktime"),
    ("webm", "video/webm"),
    ("avi", "video/x-msvideo"),
    ("mkv", "video/x-matroska"),
    ("mpeg", "video/mpeg"),
    ("flv", "video/x-flv")
])
def test_video_formats_support(format_name, mimetype):
    """Test support for all required video formats."""
    vcon = Vcon.build_new()
    
    # Add a party
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Create a video dialog with the specified format
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype=mimetype,
        filename=f"test_video.{format_name}"
    )
    
    # Add to vCon
    vcon.add_dialog(dialog)
    
    # Verify it was added correctly
    assert vcon.dialog[0]["mimetype"] == mimetype
    
    # Verify the is_video method works
    loaded_dialog = Dialog(**vcon.dialog[0])
    assert loaded_dialog.is_video()

def test_dialog_property_handling():
    """Test that video-related properties are properly handled in Vcon."""
    vcon = Vcon.build_new()
    
    # Add a party
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Create a dialog with video-specific properties
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="video/mp4",
        filename="test_video.mp4"
    )
    
    # Add to vCon
    vcon.add_dialog(dialog)
    
    # Convert to JSON and back to test serialization
    vcon_json = vcon.to_json()
    new_vcon = Vcon.build_from_json(vcon_json)
    
    # Verify properties are preserved
    dialog_dict = new_vcon.dialog[0]
    assert dialog_dict["type"] == "video"
    assert dialog_dict["mimetype"] == "video/mp4"
    assert dialog_dict["filename"] == "test_video.mp4"

def test_multiple_video_formats_in_one_vcon():
    """Test storing multiple video formats in a single vCon."""
    vcon = Vcon.build_new()
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Add videos with different formats
    formats = [
        ("mp4", "video/mp4"),
        ("mov", "video/quicktime"),
        ("webm", "video/webm"),
        ("avi", "video/x-msvideo"),
        ("mkv", "video/x-matroska")
    ]
    
    # Add a dialog for each format
    for extension, mimetype in formats:
        dialog = Dialog(
            type="video",
            start=datetime.now(timezone.utc),
            parties=[0],
            mimetype=mimetype,
            filename=f"video.{extension}"
        )
        vcon.add_dialog(dialog)
    
    # Verify all dialogs were added
    assert len(vcon.dialog) == len(formats)
    
    # Check each dialog has the correct mimetype
    for i, (extension, mimetype) in enumerate(formats):
        assert vcon.dialog[i]["mimetype"] == mimetype
        assert vcon.dialog[i]["filename"] == f"video.{extension}"
        assert Dialog(**vcon.dialog[i]).is_video()

def test_inline_video_serialization():
    """Test serialization of vCon with inline video content."""
    vcon = Vcon.build_new()
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Create mock video data (small for testing)
    video_data = base64.b64encode(b'X' * 1024).decode()
    
    # Create a dialog with inline video
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="video/mp4",
        filename="inline_video.mp4",
        body=video_data,
        encoding="base64url"
    )
    
    # Add to vCon
    vcon.add_dialog(dialog)
    
    # Serialize and deserialize
    vcon_json = vcon.to_json()
    new_vcon = Vcon.build_from_json(vcon_json)
    
    # Verify the inline data was preserved
    assert new_vcon.dialog[0]["body"] == video_data
    assert new_vcon.dialog[0]["encoding"] == "base64url"

def test_external_video_serialization():
    """Test serialization of vCon with external video references."""
    vcon = Vcon.build_new()
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Create a dialog with external video reference
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="video/mp4",
        filename="external_video.mp4",
        url="https://example.com/videos/sample.mp4"
    )
    
    # Add to vCon
    vcon.add_dialog(dialog)
    
    # Serialize and deserialize
    vcon_json = vcon.to_json()
    new_vcon = Vcon.build_from_json(vcon_json)
    
    # Verify the external reference was preserved
    assert new_vcon.dialog[0]["url"] == "https://example.com/videos/sample.mp4"
    assert "body" not in new_vcon.dialog[0]

@patch('requests.get')
def test_video_http_fetching(mock_get):
    """Test fetching video content from HTTP URLs."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'FAKE_VIDEO_DATA'
    mock_response.headers = {"Content-Type": "video/mp4"}
    mock_get.return_value = mock_response
    
    vcon = Vcon.build_new()
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Create a dialog with an external video URL
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        url="https://example.com/videos/sample.mp4",
        mimetype="video/mp4",
        filename="sample.mp4"
    )
    
    # Add to vCon
    vcon.add_dialog(dialog)
    
    # Convert external to inline to test fetching
    dialog_obj = Dialog(**vcon.dialog[0])
    dialog_obj.to_inline_data()
    
    # Update the vCon dialog with the inline version
    vcon.dialog[0] = dialog_obj.to_dict()
    
    # Verify conversion worked
    assert "body" in vcon.dialog[0]
    assert "url" not in vcon.dialog[0]
    assert vcon.dialog[0]["encoding"] == "base64url"
    
    # Check the mock was called correctly
    mock_get.assert_called_once_with("https://example.com/videos/sample.mp4")

def test_vcon_validation_with_video():
    """Test that vCon validation works correctly with video dialogs."""
    vcon = Vcon.build_new()
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Add a valid video dialog
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="video/mp4",
        filename="valid_video.mp4"
    )
    vcon.add_dialog(dialog)
    
    # Validate the vCon
    is_valid, errors = vcon.is_valid()
    assert is_valid
    assert len(errors) == 0

@pytest.mark.skip("Needs to be tested with real world metadata if available")
def test_video_metadata_in_vcon():
    """Test incorporating video metadata in a vCon."""
    # This test is a placeholder for the real implementation
    vcon = Vcon.build_new()
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Create a dialog with basic video metadata
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="video/mp4",
        filename="test_video.mp4"
    )
    
    # Add to vCon
    vcon.add_dialog(dialog)
    
    # Verify the basic properties
    assert vcon.dialog[0]["type"] == "video"
    assert vcon.dialog[0]["mimetype"] == "video/mp4"

@pytest.mark.skip("Property handling mode tests need vCon implementation check")
def test_property_handling_modes():
    """Test different property handling modes with video properties."""
    # This would need to be tested against your specific implementation
    pass

@pytest.mark.skip("Advanced tests requiring FFmpeg integration")
def test_video_metadata_extraction():
    """Test integration of video metadata extraction."""
    # This would need FFmpeg integration
    pass

@pytest.mark.skip("Advanced tests requiring FFmpeg integration")
def test_helper_function_integration():
    """Test integration of video helper functions with vCon."""
    # This would need FFmpeg integration
    pass

def test_load_save_file_with_videos(tmp_path):
    """Test saving and loading a vCon file with video dialogs."""
    vcon = Vcon.build_new()
    party = Party(name="Test User")
    vcon.add_party(party)
    
    # Add a video dialog
    dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="video/mp4",
        filename="test_video.mp4"
    )
    vcon.add_dialog(dialog)
    
    # Save to a temporary file
    temp_file = tmp_path / "vcon_with_video.json"
    vcon.save_to_file(str(temp_file))
    
    # Load it back
    loaded_vcon = Vcon.load_from_file(str(temp_file))
    
    # Verify video properties were preserved
    assert loaded_vcon.dialog[0]["type"] == "video"
    assert loaded_vcon.dialog[0]["mimetype"] == "video/mp4"
    assert loaded_vcon.dialog[0]["filename"] == "test_video.mp4"

def test_integration_basic_video_workflow():
    """Test a simple workflow with video content in a vCon."""
    # Create a vCon
    vcon = Vcon.build_new()
    
    # Add parties
    agent = Party(type="person", name="Agent")
    customer = Party(type="person", name="Customer")
    vcon.add_party(agent)
    vcon.add_party(customer)
    
    # Mock video data
    mock_video_data = base64.b64encode(b'FAKE_VIDEO_DATA').decode()
    
    # 1. Add an initial greeting text
    text_dialog = Dialog(
        type="text",
        start=datetime.now(timezone.utc),
        parties=[0, 1],  # Both parties
        body="Hello, I'd like to demonstrate our product",
        mimetype="text/plain"
    )
    vcon.add_dialog(text_dialog)
    
    # 2. Add a product demo video
    video_dialog = Dialog(
        type="video",
        start=datetime.now(timezone.utc),
        parties=[0],  # From agent
        mimetype="video/mp4",
        filename="product_demo.mp4",
        body=mock_video_data,
        encoding="base64url"
    )
    vcon.add_dialog(video_dialog)
    
    # 3. Add customer's response
    response_dialog = Dialog(
        type="text",
        start=datetime.now(timezone.utc),
        parties=[1],  # From customer
        body="Thanks for the demo. I have a few questions.",
        mimetype="text/plain"
    )
    vcon.add_dialog(response_dialog)
    
    # Verify the conversation flow
    assert len(vcon.dialog) == 3
    assert vcon.dialog[0]["type"] == "text"
    assert vcon.dialog[1]["type"] == "video"
    assert vcon.dialog[2]["type"] == "text"
    
    # Verify the video properties
    assert vcon.dialog[1]["mimetype"] == "video/mp4"
    assert vcon.dialog[1]["body"] == mock_video_data
    assert vcon.dialog[1]["encoding"] == "base64url"
    
    # Serialize and deserialize
    vcon_json = vcon.to_json()
    new_vcon = Vcon.build_from_json(vcon_json)
    
    # Verify everything is preserved
    assert len(new_vcon.dialog) == 3
    assert new_vcon.dialog[1]["type"] == "video"
    assert new_vcon.dialog[1]["mimetype"] == "video/mp4"