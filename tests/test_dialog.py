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

    # Adding external data to Dialog object
    def test_add_external_data_with_valid_data(self, mocker):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory
        import requests
        import hashlib
        import base64

        url = "http://example.com/data"
        filename = "example.txt"
        mimetype = "text/plain"
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.text = "Mocked response text"
        response_mock.headers = {"Content-Type": "text/plain"}
        mocker.patch('requests.get', return_value=response_mock)

        dialog = Dialog(
            type="text",
            start=datetime.now(),
            parties=[1, 2]
        )

        # When
        dialog.add_external_data(url, filename, mimetype)

        # Then
        assert dialog.body == "Mocked response text"
        assert dialog.mimetype == "text/plain"
        assert dialog.filename == "example.txt"
        assert dialog.alg == "sha256"
        assert dialog.encoding == "base64url"
        assert dialog.signature == base64.urlsafe_b64encode(hashlib.sha256("Mocked response text".encode()).digest()).decode()

    # Adding inline data to Dialog object
    def test_add_inline_data(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory
        import requests
        import hashlib
        import base64
        from unittest.mock import patch

        dialog = Dialog(
            type="text",
            start=datetime.now(),
            parties=[1, 2]
        )

        url = "http://example.com"
        filename = "example.txt"
        mimetype = "text/plain"
        body = "Hello, World!"

        with patch('src.vcon.dialog.requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.text = body
            mock_response.headers = {"Content-Type": mimetype}

            # When
            dialog.add_inline_data(body, filename, mimetype)

            # Then
            assert dialog.body == body
            assert dialog.filename == filename
            assert dialog.mimetype == mimetype
            assert dialog.alg == "sha256"
            assert dialog.encoding == "base64url"
            assert dialog.signature == base64.urlsafe_b64encode(hashlib.sha256(body.encode()).digest()).decode()

    # Checking if Dialog is external data
    def test_dialog_is_external_data(self):
        # Given
        from src.vcon.dialog import Dialog
        import requests
        import base64
        import hashlib
    
        dialog = Dialog(
            type="audio",
            start=datetime.now(),
            parties=[1, 2],
            url="http://example.com/audio.mp3"
        )
    
        # When
        is_external = dialog.is_external_data()
    
        # Then
        assert is_external is True

    # Checking if Dialog is inline data
    def test_dialog_is_inline_data(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory
    
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
    
        # When
        is_inline = dialog.is_inline_data()
    
        # Then
        assert is_inline

    # Checking if Dialog is text
    def test_dialog_is_text(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory

        dialog = Dialog(
            type="text",
            start=datetime.now(),
            parties=[1, 2],
            mimetype="text/plain"
        )

        # When
        result = dialog.is_text()

        # Then
        assert result is True

    # Checking if Dialog is audio
    def test_is_audio(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory

        # Create a Dialog object with mimetype as audio
        dialog = Dialog(
            type="audio",
            start=datetime.now(),
            parties=[1, 2],
            mimetype="audio/x-wav",
            party_history=[PartyHistory(1, "join", datetime.now())]
        )

        # When & Then
        assert dialog.is_audio() is True

    # Checking if Dialog is video
    def test_dialog_is_video(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory

        dialog = Dialog(
            type="video",
            start=datetime.now(),
            parties=[1, 2],
            mimetype="video/x-mp4",
            filename="example.mp4",
            body="Video content",
            duration=60.0
        )

        # When
        result = dialog.is_video()

        # Then
        assert result is True

    # Checking if Dialog is email
    def test_is_email(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory
    
        # Mocking the necessary objects
        party_history = [PartyHistory(1, "join", datetime.now())]
        dialog = Dialog(
            type="text",
            start=datetime.now(),
            duration=120.0,
            parties=[1, 2],
            originator=1,
            mimetype="message/rfc822",
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
        assert dialog.is_email() is True
        
    # Successfully fetches external data from a valid URL
    def test_fetch_external_data_success(self, mocker):
        # Given
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        party_history = [PartyHistory(1, "join", start)]
        parties = [1, 2, 3]

        dialog = Dialog(type=type, start=start, duration=120.0, parties=parties, party_history=party_history)
        
        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "sample data"
        mock_response.headers = {"Content-Type": "text/plain"}
        mocker.patch("requests.get", return_value=mock_response)
    
        # When
        dialog.add_external_data(url, filename, mimetype)
        
    
        # Then
        assert dialog.body == "sample data"
        assert dialog.mimetype == "text/plain"
        assert dialog.filename == filename
        assert dialog.alg == "sha256"
        assert dialog.encoding == "base64url"
        expected_signature = base64.urlsafe_b64encode(hashlib.sha256("sample data".encode()).digest()).decode()
        assert dialog.signature == expected_signature

    # Handles non-200 response status codes by raising an exception
    def test_fetch_external_data_failure(self, mocker):
        # Given
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        party_history = [PartyHistory(1, "join", start)]
        parties = [1, 2, 3]

        dialog = Dialog(type=type, start=start, duration=120.0, parties=parties, party_history=party_history)

        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mocker.patch("requests.get", return_value=mock_response)
    
        # When / Then
        with pytest.raises(Exception) as excinfo:
            dialog.add_external_data(url, filename, mimetype)
    
        print(excinfo)
        assert str(excinfo.value) == "Failed to fetch external data: 404"
        
    
    # Successfully fetches external data from a valid URL
    def test_fetch_external_data_success(self, mocker):
        # Given
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        party_history = [PartyHistory(1, "join", start)]
        parties = [1, 2, 3]

        dialog = Dialog(type=type, start=start, duration=120.0, parties=parties, party_history=party_history)

        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "sample data"
        mock_response.headers = {"Content-Type": "text/plain"}
        mocker.patch("requests.get", return_value=mock_response)
    
        # When
        dialog.add_external_data(url, filename, mimetype)
    
        # Then
        assert dialog.body == "sample data"
        assert dialog.mimetype == "text/plain"
        assert dialog.filename == filename
        assert dialog.alg == "sha256"
        assert dialog.encoding == "base64url"
        expected_signature = base64.urlsafe_b64encode(hashlib.sha256("sample data".encode()).digest()).decode()
        assert dialog.signature == expected_signature

    # Handles non-200 response status codes by raising an exception
    def test_fetch_external_data_failure(self, mocker):
        # Given
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        party_history = [PartyHistory(1, "join", start)]
        parties = [1, 2, 3]

        dialog = Dialog(type=type, start=start, duration=120.0, parties=parties, party_history=party_history)

        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mocker.patch("requests.get", return_value=mock_response)
    
        # When / Then
        with pytest.raises(Exception) as excinfo:
            dialog.add_external_data(url, filename, mimetype)
    
        assert str(excinfo.value) == "Failed to fetch external data: 404"

    # Correctly sets the filename from the URL if not provided
    def test_correctly_sets_filename_from_url_if_not_provided(self, mocker):
        # Given
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        party_history = [PartyHistory(1, "join", start)]
        parties = [1, 2, 3]

        dialog = Dialog(type=type, start=start, duration=120.0, parties=parties, party_history=party_history)

        url = "http://example.com/data"
        filename = ""
        mimetype = "text/plain"
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "sample data"
        mock_response.headers = {"Content-Type": "text/plain"}
        mocker.patch("requests.get", return_value=mock_response)
    
        # When
        dialog.add_external_data(url, filename, mimetype)
    
        # Then
        assert dialog.body == "sample data"
        assert dialog.mimetype == "text/plain"
        assert dialog.filename == "data"
        assert dialog.alg == "sha256"
        assert dialog.encoding == "base64url"
        expected_signature = base64.urlsafe_b64encode(hashlib.sha256("sample data".encode()).digest()).decode()
        assert dialog.signature == expected_signature

    # Extracts the filename from the URL path
    def test_extract_filename_from_url(self, mocker):
        # Given
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        party_history = [PartyHistory(1, "join", start)]
        parties = [1, 2, 3]

        dialog = Dialog(type=type, start=start, duration=120.0, parties=parties, party_history=party_history)
        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "sample data"
        mock_response.headers = {"Content-Type": "text/plain"}
        mocker.patch("requests.get", return_value=mock_response)

        # When
        dialog.add_external_data(url, filename, mimetype)

        # Then
        assert dialog.body == "sample data"
        assert dialog.mimetype == "text/plain"
        assert dialog.filename == filename
        assert dialog.alg == "sha256"
        assert dialog.encoding == "base64url"
        expected_signature = base64.urlsafe_b64encode(hashlib.sha256("sample data".encode()).digest()).decode()
        assert dialog.signature == expected_signature

    # Assigns the extracted filename to the filename attribute
    def test_assign_extracted_filename(self, mocker):
        # Given
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        party_history = [PartyHistory(1, "join", start)]
        parties = [1, 2, 3]

        dialog = Dialog(type=type, start=start, duration=120.0, parties=parties, party_history=party_history)

        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "sample data"
        mock_response.headers = {"Content-Type": "text/plain"}
        mocker.patch("requests.get", return_value=mock_response)

        # When
        dialog.add_external_data(url, filename, mimetype)

        # Then
        assert dialog.filename == filename

    # Handles cases where the URL does not contain a filename
    def test_handles_url_without_filename(self, mocker):
        # Given
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        party_history = [PartyHistory(1, "join", start)]
        parties = [1, 2, 3]

        dialog = Dialog(type=type, start=start, duration=120.0, parties=parties, party_history=party_history)

        url = "http://example.com/data.wav"
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "sample data"
        mock_response.headers = {"Content-Type": "audio/x-wav"}
        mocker.patch("requests.get", return_value=mock_response)
    
        # When
        dialog.add_external_data(url, "", "audio/x-wav")
    
        # Then
        assert dialog.body == "sample data"
        assert dialog.mimetype == "audio/x-wav"
        assert dialog.filename == "data.wav"
        assert dialog.alg == "sha256"
        assert dialog.encoding == "base64url"
        expected_signature = base64.urlsafe_b64encode(hashlib.sha256("sample data".encode()).digest()).decode()
        assert dialog.signature == expected_signature

    # Ensures the filename attribute is not None after assignment
    def test_filename_not_none_after_assignment(self, mocker):
        # Given
        type = "audio"
        start = datetime.now().isoformat()
        
        # create the parties
        party_history = [PartyHistory(1, "join", start)]
        parties = [1, 2, 3]

        dialog = Dialog(type=type, start=start, duration=120.0, parties=parties, party_history=party_history)
        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "sample data"
        mock_response.headers = {"Content-Type": "text/plain"}
        mocker.patch("requests.get", return_value=mock_response)

        # When
        dialog.add_external_data(url, filename, mimetype)

        # Then
        assert dialog.filename is not None
       