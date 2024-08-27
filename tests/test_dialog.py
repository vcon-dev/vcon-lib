import pytest
import unittest
from unittest.mock import Mock
from datetime import datetime
from src.vcon.dialog import Dialog
from src.vcon.party import PartyHistory
import json
import hashlib
import base64

class TestDialog:

    # Initialization of Dialog object with all parameters
    def test_initialization_with_all_parameters(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory

        # Given
        party_history = [PartyHistory(1, "join", datetime.now())]
        dialog = Dialog(
            type="text",
            start=datetime.now(),
            duration=120.0,
            parties=[1, 2],
            originator=1,
            mimetype="text/plain",
            filename="example.txt",
            body="Hello, World!",
            encoding="utf-8",
            url="http://example.com",
            alg="sha256",
            signature="signature",
            disposition="inline",
            party_history=party_history,
            transferee=2,
            transferor=1,
            transfer_target=3,
            original=1,
            consultation=2,
            target_dialog=3,
            campaign="campaign1",
            interaction="interaction1",
            skill="skill1"
        )

        # When & Then
        assert dialog.type == "text"
        assert dialog.duration == 120.0
        assert dialog.parties == [1, 2]
        assert dialog.party_history == party_history

    # Initialization with missing optional parameters
    def test_initialization_with_missing_optional_parameters(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog

        # Given
        dialog = Dialog(
            type="audio",
            start=datetime.now(),
            duration=None,
            parties=[1, 2],
            originator=None,
            mimetype=None,
            filename=None,
            body=None,
            encoding=None,
            url=None,
            alg=None,
            signature=None,
            disposition=None,
            party_history=None,
            transferee=None,
            transferor=None,
            transfer_target=None,
            original=None,
            consultation=None,
            target_dialog=None,
            campaign=None,
            interaction=None,
            skill=None
        )

        # When & Then
        assert dialog.type == "audio"
        assert dialog.duration is None
        assert dialog.originator is None
        assert dialog.mimetype is None

    def test_initialization_with_missing_optional_parameters(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog

        dialog = Dialog(
            type="audio",
            start=datetime.now(),
            duration=None,
            parties=[1, 2],
            originator=None,
            mimetype=None,
            filename=None,
            body=None,
            encoding=None,
            url=None,
            alg=None,
            signature=None,
            disposition=None,
            party_history=None,
            transferee=None,
            transferor=None,
            transfer_target=None,
            original=None,
            consultation=None,
            target_dialog=None,
            campaign=None,
            interaction=None,
            skill=None
        )

        # When & Then
        assert dialog.type == "audio"
        assert dialog.duration is None
        assert dialog.originator is None
        assert dialog.mimetype is None

    def test_initialization_with_default_optional_parameters(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog

        dialog = Dialog(
            type="video",
            start=datetime.now(),
            duration=0.0,
            parties=[1],
            originator=1
        )

        # When & Then
        assert dialog.duration == 0.0
        assert dialog.parties == [1]
        assert dialog.originator == 1

    def test_retrieve_dialog_originator_when_set(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog

        dialog = Dialog(
            type="video",
            start=datetime.now(),
            duration=0.0,
            parties=[1],
            originator=1
        )

        # When & Then
        assert dialog.originator == 1

    def test_retrieve_dialog_mimetype_when_set(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog

        dialog = Dialog(
            type="video",
            start=datetime.now(),
            duration=0.0,
            parties=[1],
            originator=1,
            mimetype="video/mp4"
        )

        # When & Then
        assert dialog.mimetype == "video/mp4"

    def test_initialization_with_missing_optional_parameters(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog

        dialog = Dialog(
            type="audio",
            start=datetime.now(),
            duration=None,
            parties=[1, 2],
            originator=None,
            mimetype=None,
            filename=None,
            body=None,
            encoding=None,
            url=None,
            alg=None,
            signature=None,
            disposition=None,
            party_history=None,
            transferee=None,
            transferor=None,
            transfer_target=None,
            original=None,
            consultation=None,
            target_dialog=None,
            campaign=None,
            interaction=None,
            skill=None
        )

        # When
        # Then
        assert dialog.type == "audio"
        assert dialog.duration is None
        assert dialog.originator is None
        assert dialog.mimetype is None

    def test_initialization_with_default_optional_parameters(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog

        dialog = Dialog(
            type="video",
            start=datetime.now(),
            duration=0.0,
            parties=[1],
            originator=1
        )

        # When
        # Then
        assert dialog.duration == 0.0
        assert dialog.parties == [1]
        assert dialog.originator == 1

    # Initialization of Dialog object with all parameters
    def test_initialization_with_all_parameters(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory

        # Given
        party_history = [PartyHistory(1, "join", datetime.now())]
        dialog = Dialog(
            type="text",
            start=datetime.now(),
            duration=120.0,
            parties=[1, 2],
            originator=1,
            mimetype="text/plain",
            filename="example.txt",
            body="Hello, World!",
            encoding="utf-8",
            url="http://example.com",
            alg="sha256",
            signature="signature",
            disposition="inline",
            party_history=party_history,
            transferee=2,
            transferor=1,
            transfer_target=3,
            original=1,
            consultation=2,
            target_dialog=3,
            campaign="campaign1",
            interaction="interaction1",
            skill="skill1"
        )

        # When & Then
        assert dialog.type == "text"
        assert dialog.duration == 120.0
        assert dialog.parties == [1, 2]
        assert dialog.party_history == party_history

    # Initialization with missing optional parameters
    def test_initialization_with_missing_optional_parameters(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog

        # Given
        dialog = Dialog(
            type="audio",
            start=datetime.now(),
            duration=None,
            parties=[1, 2],
            originator=None,
            mimetype=None,
            filename=None,
            body=None,
            encoding=None,
            url=None,
            alg=None,
            signature=None,
            disposition=None,
            party_history=None,
            transferee=None,
            transferor=None,
            transfer_target=None,
            original=None,
            consultation=None,
            target_dialog=None,
            campaign=None,
            interaction=None,
            skill=None
        )

        # When & Then
        assert dialog.type == "audio"
        assert dialog.duration is None
        assert dialog.originator is None
        assert dialog.mimetype is None

    # Conversion of Dialog object to dictionary
    def test_conversion_to_dict(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory

        party_time = datetime.now().isoformat()
        party_history = [PartyHistory(1, "join", party_time)]
        dialog = Dialog(
            type="text",
            start=datetime.now(),
            duration=120.0,
            parties=[1, 2],
            originator=1,
            mimetype="text/plain",
            filename="example.txt",
            body="Hello, World!",
            encoding="utf-8",
            url="http://example.com",
            alg="sha256",
            signature="signature",
            disposition="inline",
            party_history=party_history,
            transferee=2,
            transferor=1,
            transfer_target=3,
            original=1,
            consultation=2,
            target_dialog=3,
            campaign="campaign1",
            interaction="interaction1",
            skill="skill1"
        )

        # When
        dialog_dict = dialog.to_dict()

        # Then
        assert dialog_dict["type"] == "text"
        assert dialog_dict["duration"] == 120.0
        assert dialog_dict["parties"] == [1, 2]
        assert dialog_dict["party_history"] == [{"party": 1, "event": "join", "time": party_time}]

    