import pytest
from src.vcon.dialog import Dialog
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


    # Test the meta variable in the dialog
    def test_meta_variable_in_dialog(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog
    
        type = "audio"
        start = datetime.now()
        parties = [1, 2]
        meta = {"key": "value"}
    
        dialog = Dialog(type=type, start=start, parties=parties, meta=meta)
    
        assert dialog.type == type
        assert dialog.start == start
        assert dialog.parties == parties
        assert dialog.meta == meta

    # Successfully fetches external data from a valid URL
    def test_fetch_external_data_success(self, mocker):
        # Arrange
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.headers = {"Content-Type": "text/plain"}
        response_mock.text = "sample data"
        mocker.patch("requests.get", return_value=response_mock)

        # Act
        dialog.add_external_data(url, filename, mimetype)

        # Assert
        assert dialog.mimetype == "text/plain"
        assert dialog.filename == filename
        assert dialog.alg == "sha256"
        assert dialog.encoding == "base64url"
        expected_signature = base64.urlsafe_b64encode(hashlib.sha256("sample data".encode()).digest()).decode()
        assert dialog.signature == expected_signature
        assert dialog.body is None

    # URL returns a non-200 status code
    def test_fetch_external_data_failure(self, mocker):
        # Arrange
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        response_mock = mocker.Mock()
        response_mock.status_code = 404
        mocker.patch("requests.get", return_value=response_mock)

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            dialog.add_external_data(url, filename, mimetype)

        assert str(excinfo.value) == "Failed to fetch external data: 404"

    # Correctly sets the mimetype from the response headers
    def test_correctly_sets_mimetype(self, mocker):
        # Setup
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        url = "http://example.com/data"
        filename = "example_data.txt"
        mimetype = "text/plain"
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.headers = {"Content-Type": mimetype}
        response_mock.text = "dummy data"
        mocker.patch('requests.get', return_value=response_mock)

        # Invoke
        dialog.add_external_data(url, filename, None)

        # Assert
        assert dialog.mimetype == mimetype

    # Overrides the filename if provided
    def test_overrides_filename_if_provided(self, mocker):
        # Setup
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        url = "http://example.com/data"
        filename = "example_data.txt"
        new_filename = "new_data.txt"
        mimetype = "text/plain"
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.headers = {"Content-Type": mimetype}
        response_mock.text = "dummy data"
        mocker.patch('requests.get', return_value=response_mock)

        # Invoke
        dialog.add_external_data(url, filename, None)
        dialog.add_external_data(url, new_filename, None)

        # Assert
        assert dialog.filename == new_filename

    # Correctly sets body, filename, and mimetype attributes
    def test_correctly_sets_attributes(self):
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        body = "sample body"
        filename = "sample.txt"
        mimetype = "text/plain"

        dialog.add_inline_data(body, filename, mimetype)

        assert dialog.body == body
        assert dialog.filename == filename
        assert dialog.mimetype == mimetype

    # Handles empty string for body
    def test_handles_empty_body(self):
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        body = ""
        filename = "empty.txt"
        mimetype = "text/plain"

        dialog.add_inline_data(body, filename, mimetype)

        assert dialog.body == body
        assert dialog.filename == filename
        assert dialog.mimetype == mimetype
        assert dialog.signature == base64.urlsafe_b64encode(
            hashlib.sha256(body.encode()).digest()).decode()

    # Generates a valid SHA-256 hash signature for the body
    def test_valid_sha256_signature(self):
        # Initialize the dialog object
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])

        # Add inline data
        dialog.add_inline_data("example_body", "example_filename", "text/plain")

        # Check if the SHA-256 hash signature is valid
        expected_signature = base64.urlsafe_b64encode(hashlib.sha256("example_body".encode()).digest()).decode()
        assert dialog.signature == expected_signature

    # Sets the encoding to "base64url"
    def test_encoding_base64url(self):
        # Initialize the dialog object
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])

        # Add inline data
        dialog.add_inline_data("example_body", "example_filename", "text/plain")

        # Check if the encoding is set to "base64url"
        assert dialog.encoding == "base64url"