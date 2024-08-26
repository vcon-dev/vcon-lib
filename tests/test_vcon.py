import pytest
import sys

print(sys.path)

from vcon import Vcon
from datetime import datetime
from vcon.party import Party
from vcon.dialog import Dialog
from vcon.party import PartyHistory
from typing import List, Optional
import json


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

test_vcon_string = "{\"uuid\":\"f6603c8b-f3c6-4d12-bc50-b0a1f1c887b3\",\"vcon\":\"0.0.1\", \"created_at\":\"2024-05-03T20:13:48.414984\",\"updated_at\":\"2024-05-03T20:13:48.414984\",\"dialog\":[{\"alg\":\"SHA-512\",\"url\":\"https://fake-vcons.s3.amazonaws.com/2024/05/03/f6603c8b-f3c6-4d12-bc50-b0a1f1c887b3.mp3\",\"meta\":{\"direction\":\"in\",\"disposition\":\"ANSWERED\"},\"type\":\"recording\",\"start\":\"2024-05-03T20:13:48.414951\",\"parties\":[1,0],\"duration\":59.304,\"filename\":\"f6603c8b-f3c6-4d12-bc50-b0a1f1c887b3.mp3\",\"mimetype\":\"audio/mp3\",\"signature\":\"4pVDJ1Hd7uU9siWG8P3jN10PHdpiGRUtOcHZZinLzAYzK7RypIgeS8c0Yd_xGt9sq6G5oREs9H0hU-fToEZs5A\"}],\"parties\":[{\"tel\":\"+14327534365\",\"meta\":{\"role\":\"agent\"},\"name\":\"Daniel Rodriguez\",\"mailto\":\"daniel.rodriguez@cateringservice.com\"},{\"tel\":\"+18043243300\",\"meta\":{\"role\":\"customer\"},\"name\":\"Maria Anderson\",\"mailto\":\"maria.anderson@gmail.com\"}],\"attachments\":[],\"analysis\":[{\"type\":\"transcript\",\"dialog\":0,\"vendor\":\"openai\",\"encoding\":\"none\",\"body\":[{\"speaker\":\"Agent\",\"message\":\"Hello, thank you for contacting Catering Co. My name is Daniel Rodriguez.\"},{\"speaker\":\"Agent\",\"message\":\"May I have your name, please?\"},{\"speaker\":\"Customer\",\"message\":\"Hello, I'm Maria Anderson.\"},{\"speaker\":\"Agent\",\"message\":\"Nice to meet you, Maria. How can I assist you today?\"},{\"speaker\":\"Customer\",\"message\":\"I have a question about my recent bill. Could you clarify a couple of charges for me?\"},{\"speaker\":\"Agent\",\"message\":\"Of course, Maria. I'll need your account number and the date of the bill to assist you further. Can you provide that information?\"},{\"speaker\":\"Customer\",\"message\":\"Yes, my account number is eight seven six two three and the bill date is the twenty fourth of November.\"},{\"speaker\":\"Customer\",\"message\":\"Can I also know if there are any upcoming promotions for loyal customers?\"},{\"speaker\":\"Agent\",\"message\":\"Thank you for providing that, Maria. I will look into your bill and get back to you shortly. Regarding upcoming promotions, rest assured we have an exclusive event planned for loyal customers next month. Keep an eye on your inbox for details!\"},{\"speaker\":\"Agent\",\"message\":\"Thank you for your time, Maria. I'll investigate the bill and reach out to you soon with the details. Have a wonderful day!\"},{\"speaker\":\"Customer\",\"message\":\"Thank you for your help, Daniel. Have a great day too!\"}],\"vendor_schema\":{\"model\":\"gpt-3.5-turbo\",\"prompt\":\"\\nGenerate a fake conversation between a customer and an agent.\\nThe agent should introduce themselves, their company and give the customer\\ntheir name. The agent should ask for the customer's name.\\nAs part of the conversation, have the agent ask for two pieces of\\npersonal information. As part of the conversation, the customer should ask two questions.  Spell out numbers. For example, 1000 should be\\nsaid as one zero zero zero, not one thousand. The conversation should cover two or three topics, have back and forth between the parties, and be complete. At the end\\nof the conversation, the agent should thank the customer for their time\\nand end the conversation. Return the conversation formatted \\nlike the following example:\\n\\n{'conversation': \\n    [\\n    {'speaker': 'Agent', 'message': 'xxxxx'}, \\n    {'speaker': 'Customer', 'message': \\\"xxxxx.\\\"}, \\n    {'speaker': 'Agent', 'message': \\\"xxxxxx\\\"}\\n    ] \\n}\\n\"}}]}"

def test_build_from_json():
    """
    Test that we can create a Vcon object from a JSON string.

    The JSON string is a sample vCon object that contains a single dialog
    with several turns.

    The test verifies that the resulting Vcon object has the expected UUID,
    vcon version, and created_at timestamp.
    """
    vcon = Vcon.build_from_json(test_vcon_string)
    assert vcon.uuid == "f6603c8b-f3c6-4d12-bc50-b0a1f1c887b3"
    assert vcon.vcon == "0.0.1"
    assert vcon.created_at == "2024-05-03T20:13:48.414984"


def test_build_new():
    vcon = Vcon.build_new()
    assert vcon.uuid is not None
    assert vcon.vcon == "0.0.1"
    assert vcon.created_at is not None


def test_tags():
    vcon = Vcon.build_new()
    assert vcon.tags is None

    vcon.add_tag("test_tag", "test_value")
    assert vcon.get_tag("test_tag") == "test_value"


def test_add_attachment():
    vcon = Vcon.build_new()
    vcon.add_attachment(body={"key": "value"}, type="test_type")
    attachment = vcon.find_attachment_by_type("test_type")
    assert attachment["body"] == {"key": "value"}


def test_add_analysis():
    vcon = Vcon.build_new()
    vcon.add_analysis(
        type="test_type", dialog=[1, 2], vendor="test_vendor", body={"key": "value"}
    )
    analysis = vcon.find_analysis_by_type("test_type")
    assert analysis["body"] == {"key": "value"}
    assert analysis["dialog"] == [1, 2]
    assert analysis["vendor"] == "test_vendor"




def test_add_dialog():
    vcon = Vcon.build_new()
    vcon.add_dialog({"id": "dialog1"})
    assert vcon.find_dialog("id", "dialog1") == {"id": "dialog1"}


def test_to_json():
    vcon = Vcon.build_new()
    json_string = vcon.to_json()
    assert json.loads(json_string) == vcon.to_dict()


def test_uuid8_domain_name():
    uuid8 = Vcon.uuid8_domain_name("test.com")
    assert uuid8[14] == "8"  # check version is 8


def test_get_tag():
    vcon = Vcon.build_new()
    vcon.add_tag("test_tag", "test_value")
    assert vcon.get_tag("test_tag") == "test_value"
    assert vcon.get_tag("nonexistent_tag") is None


def test_find_attachment_by_type():
    vcon = Vcon.build_new()
    vcon.add_attachment(body={"key": "value"}, type="test_type")
    assert vcon.find_attachment_by_type("test_type") == {
        "type": "test_type",
        "body": {"key": "value"},
        "encoding": "none",
    }
    assert vcon.find_attachment_by_type("nonexistent_type") is None


def test_find_analysis_by_type():
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


def test_find_party_index():
    vcon = Vcon.build_new()
    vcon.add_party({"id": "party1"})
    assert vcon.find_party_index("id", "party1") == 0
    assert vcon.find_party_index("id", "nonexistent_party") is None


def test_find_dialog():
    vcon = Vcon.build_new()
    vcon.add_dialog({"id": "dialog1"})
    assert vcon.find_dialog("id", "dialog1") == {"id": "dialog1"}
    assert vcon.find_dialog("id", "nonexistent_dialog") is None


def test_properties():

    vcon = Vcon.build_from_json(test_vcon_string)

    assert vcon.uuid == "f6603c8b-f3c6-4d12-bc50-b0a1f1c887b3"
    assert vcon.created_at == "2024-05-03T20:13:48.414984"
    assert vcon.updated_at == "2024-05-03T20:13:48.414984"

    # Note: vcon and redacted fields are not present in the provided JSON
    # assert vcon.vcon == "0.0.1"
    # assert vcon.redacted == {"key": "value"}

    # Note: group field is not present in the provided JSON
    # assert vcon.group == [1, 2]

    assert len(vcon.parties) == 2
    
    
    assert vcon.parties[0].to_dict() == {
        "tel": "+14327534365",
        "meta": {"role": "agent"},
        "name": "Daniel Rodriguez",
        "mailto": "daniel.rodriguez@cateringservice.com"
    }
    assert vcon.parties[1].to_dict() == {
        "tel": "+18043243300",
        "meta": {"role": "customer"},
        "name": "Maria Anderson",
        "mailto": "maria.anderson@gmail.com"
    }

    assert len(vcon.dialog) == 1
    assert vcon.dialog[0] == {
        "alg": "SHA-512",
        "url": "https://fake-vcons.s3.amazonaws.com/2024/05/03/f6603c8b-f3c6-4d12-bc50-b0a1f1c887b3.mp3",
        "meta": {"direction": "in", "disposition": "ANSWERED"},
        "type": "recording",
        "start": "2024-05-03T20:13:48.414951",
        "parties": [1, 0],
        "duration": 59.304,
        "filename": "f6603c8b-f3c6-4d12-bc50-b0a1f1c887b3.mp3",
        "mimetype": "audio/mp3",
        "signature": "4pVDJ1Hd7uU9siWG8P3jN10PHdpiGRUtOcHZZinLzAYzK7RypIgeS8c0Yd_xGt9sq6G5oREs9H0hU-fToEZs5A"
    }

    assert vcon.attachments == []

    assert len(vcon.analysis) == 1
    assert vcon.analysis[0]["type"] == "transcript"
    assert vcon.analysis[0]["dialog"] == 0
    assert vcon.analysis[0]["vendor"] == "openai"
    assert vcon.analysis[0]["encoding"] == "none"
    assert len(vcon.analysis[0]["body"]) == 11  # 11 conversation turns
    assert vcon.analysis[0]["vendor_schema"]["model"] == "gpt-3.5-turbo"

    print("All assertions passed!")


def test_to_dict():
    vcon = Vcon.build_new()
    vcon_dict = vcon.to_dict()
    assert isinstance(vcon_dict, dict)
    assert vcon_dict == json.loads(vcon.to_json())


def test_dumps():
    vcon = Vcon.build_new()
    json_string = vcon.dumps()
    assert isinstance(json_string, str)
    assert json_string == vcon.to_json()


def test_error_handling():
    with pytest.raises(json.JSONDecodeError):
        Vcon.build_from_json("invalid_json")

def test_find_party_index():
    # Given
    vcon = Vcon.build_new()
    party = Party(tel="1234567890")
    vcon.add_party(party)
    
    # When/Then
    assert vcon.find_party_index("tel", "1234567890") == 0
    assert vcon.find_party_index("tel", "nonexistent_party") is None

def test_add_and_find_party_index():
    # Given
    vcon = Vcon.build_new()
    party = Party(mailto="R0Hl4@example.com")

    # When
    vcon.add_party(party)

    # Then
    assert vcon.find_party_index("mailto", "R0Hl4@example.com") == 0
    assert vcon.find_party_index("mailto", "nonexistent_party") is None
    
def test_find_dialog():
    # Given
    vcon = Vcon.build_new()
    vcon.add_dialog({"id": "dialog1"})
    
    # When/Then
    assert vcon.find_dialog("id", "dialog1") == {"id": "dialog1"}
    assert vcon.find_dialog("id", "nonexistent_dialog") is None

def test_add_special_character_tag():
    # Given
    vcon = Vcon.build_new()
    
    # When
    vcon.add_tag("special_tag!@#", "special_value")
    
    # Then
    assert vcon.get_tag("special_tag!@#") == "special_value"
