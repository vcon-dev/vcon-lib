import requests
import hashlib
import base64
from datetime import datetime
from typing import Optional, List, Union
from .party import PartyHistory
from dateutil import parser

MIME_TYPES = [
    "text/plain",
    "audio/x-wav",
    "audio/wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/ogg",
    "audio/webm",
    "audio/x-m4a",
    "audio/aac",
    "video/x-mp4",
    "video/ogg",
    "multipart/mixed",
    "message/rfc822"
]


class Dialog:
    MIME_TYPES = [
        "text/plain",
        "audio/x-wav",
        "audio/wav",
        "audio/wave",
        "audio/mpeg",
        "audio/mp3",
        "audio/ogg",
        "audio/webm",
        "audio/x-m4a",
        "audio/aac",
        "video/x-mp4",
        "video/ogg",
        "multipart/mixed",
        "message/rfc822"
    ]

    def __init__(
        self,
        type: str,
        start: Union[datetime, str],
        parties: List[int],
        originator: Optional[int] = None,
        mimetype: Optional[str] = None,
        filename: Optional[str] = None,
        body: Optional[str] = None,
        encoding: Optional[str] = None,
        url: Optional[str] = None,
        alg: Optional[str] = None,
        signature: Optional[str] = None,
        disposition: Optional[str] = None,
        party_history: Optional[List[PartyHistory]] = None,
        transferee: Optional[int] = None,
        transferor: Optional[int] = None,
        transfer_target: Optional[int] = None,
        original: Optional[int] = None,
        consultation: Optional[int] = None,
        target_dialog: Optional[int] = None,
        campaign: Optional[str] = None,
        interaction: Optional[str] = None,
        skill: Optional[str] = None,
        duration: Optional[float] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a Dialog object.

        :param type: the type of the dialog (e.g. "text", "audio", etc.)
        :type type: str
        :param start: the start time of the dialog
        :type start: datetime
        :param parties: the parties involved in the dialog
        :type parties: List[int]
        :param originator: the party that originated the dialog
        :type originator: int or None
        :param mimetype: the MIME type of the dialog body
        :type mimetype: str or None
        :param filename: the filename of the dialog body
        :type filename: str or None
        :param body: the body of the dialog
        :type body: str or None
        :param encoding: the encoding of the dialog body
        :type encoding: str or None
        :param url: the URL of the dialog
        :type url: str or None
        :param alg: the algorithm used to sign the dialog
        :type alg: str or None
        :param signature: the signature of the dialog
        :type signature: str or None
        :param disposition: the disposition of the dialog
        :type disposition: str or None
        :param party_history: the history of parties involved in the dialog
        :type party_history: List[PartyHistory] or None
        :param transferee: the party that the dialog was transferred to
        :type transferee: int or None
        :param transferor: the party that transferred the dialog
        :type transferor: int or None
        :param transfer_target: the target of the transfer
        :type transfer_target: int or None
        :param original: the original dialog
        :type original: int or None
        :param consultation: the consultation dialog
        :type consultation: int or None
        :param target_dialog: the target dialog
        :type target_dialog: int or None
        :param campaign: the campaign that the dialog is associated with
        :type campaign: str or None
        :param interaction: the interaction that the dialog is associated with
        :type interaction: str or None
        :param skill: the skill that the dialog is associated with
        :type skill: str or None
        :param duration: the duration of the dialog
        :type duration: float or None
        :param meta: additional metadata for the dialog
        :type meta: dict or None
        :param kwargs: Additional attributes to be set on the dialog
        """

        # Convert the start time to an ISO 8601 string from a datetime or a string
        if isinstance(start, datetime):
            start = start.isoformat()
        elif isinstance(start, str):
            start = parser.parse(start).isoformat()

        # Set attributes from named parameters that are not None
        for key, value in locals().items():
            if value is not None and key not in ("self", "kwargs"):
                setattr(self, key, value)

        # Set any additional kwargs as attributes
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

    def to_dict(self):
        """
        Returns a dictionary representation of the Dialog object.

        :return: a dictionary containing all non-None Dialog object attributes
        :rtype: dict
        """
        # Check to see if the start time provided. If not,
        # set the start time to the current time
        if not hasattr(self, "start"):
            self.start = datetime.now().isoformat()

        # Get all attributes of the object
        dialog_dict = self.__dict__.copy()

        # Handle party_history specially
        if hasattr(self, "party_history") and self.party_history:
            dialog_dict["party_history"] = [
                party_history.to_dict() for party_history in self.party_history
            ]

        return {k: v for k, v in dialog_dict.items() if v is not None}

    def add_external_data(self, url: str, filename: str, mimetype: str) -> None:
        """
        Add external data to the dialog.

        :param url: the URL of the external data
        :type url: str
        :return: None
        :rtype: None
        """
        response = requests.get(url)
        if response.status_code == 200:
            self.mimetype = response.headers["Content-Type"]
        else:
            raise Exception(f"Failed to fetch external data: {response.status_code}")

        # Override the filename if provided, otherwise use the filename from the URL
        if filename:
            self.filename = filename
        else:
            # Extract filename from URL, removing any query parameters
            url_path = url.split("?")[0]
            self.filename = url_path.split("/")[-1]

        # Override the mimetype if provided, otherwise use the mimetype from the URL
        if mimetype:
            self.mimetype = mimetype

        # Calculate the SHA-256 hash of the body as the signature
        self.alg = "sha256"
        self.encoding = "base64url"
        self.signature = base64.urlsafe_b64encode(
            hashlib.sha256(response.text.encode()).digest()
        ).decode()

    def add_inline_data(self, body: str, filename: str, mimetype: str) -> None:
        """
        Add inline data to the dialog.

        :param body: the body of the inline data
        :type body: str
        :param filename: the filename of the inline data
        :type filename: str
        :param mimetype: the mimetype of the inline data
        :type mimetype: str
        :return: None
        :rtype: None
        """
        self.body = body
        self.mimetype = mimetype
        self.filename = filename
        self.alg = "sha256"
        self.encoding = "base64url"
        self.signature = base64.urlsafe_b64encode(
            hashlib.sha256(self.body.encode()).digest()
        ).decode()

    def is_external_data(self) -> bool:
        """
        Check if the dialog is an external data dialog.

        :return: True if the dialog is an external data dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "url")

    def is_inline_data(self) -> bool:
        """
        Check if the dialog is an inline data dialog.

        :return: True if the dialog is an inline data dialog, False otherwise
        :rtype: bool
        """
        return not self.is_external_data()

    def is_text(self) -> bool:
        """
        Check if the dialog is a text dialog.

        :return: True if the dialog is a text dialog, False otherwise
        :rtype: bool
        """
        return self.mimetype == "text/plain"

    def is_audio(self) -> bool:
        """
        Check if the dialog is an audio dialog.

        :return: True if the dialog is an audio dialog, False otherwise
        :rtype: bool
        """
        return self.mimetype in [
            "audio/x-wav",
            "audio/wav",
            "audio/wave",
            "audio/mpeg",
            "audio/mp3",
            "audio/ogg",
            "audio/webm",
            "audio/x-m4a",
            "audio/aac",
        ]

    def is_video(self) -> bool:
        """
        Check if the dialog is a video dialog.

        :return: True if the dialog is a video dialog, False otherwise
        :rtype: bool
        """
        return self.mimetype in ["video/x-mp4", "video/ogg"]

    # Check if the dialog is an email dialog
    def is_email(self) -> bool:
        """
        Check if the dialog is an email dialog.

        :return: True if the dialog is an email dialog, False otherwise
        :rtype: bool
        """
        return self.mimetype == "message/rfc822"

    def is_external_data_changed(self) -> bool:
        """
        Check to see if it's an external data dialog, that the contents are valid by
        checking the hash of the body against the signature.

        :return: True if the dialog is an external data dialog and the contents are valid, False otherwise
        :rtype: bool
        """
        if not self.is_external_data():
            return False
        try:
            body_hash = base64.urlsafe_b64decode(self.signature.encode())
            return hashlib.sha256(self.body.encode()).digest() != body_hash
        except Exception as e:
            print(e)
            return True

    # Convert the dialog from an external data dialog to an inline data dialog
    # by reading the contents from the URL then adding the contents to the body
    def to_inline_data(self) -> None:
        """
        Convert the dialog from an external data dialog to an inline data dialog
        by reading the contents from the URL then adding the contents to the body.

        :return: None
        :rtype: None
        """
        # Read the contents from the URL
        response = requests.get(self.url)
        if response.status_code == 200:
            # For binary content, use response.content instead of response.text
            raw_content = response.content
            # Base64url encode the body
            self.body = base64.urlsafe_b64encode(raw_content).decode()
            self.mimetype = response.headers.get("Content-Type")
        else:
            raise Exception(f"Failed to fetch external data: {response.status_code}")

        # Calculate the SHA-256 hash of the original binary content
        self.alg = "sha256"
        self.encoding = "base64url"
        self.signature = base64.urlsafe_b64encode(
            hashlib.sha256(raw_content).digest()
        ).decode()

        # Set the filename if it doesn't exist
        if not hasattr(self, "filename"):
            self.filename = self.url.split("/")[-1]

        # Remove the url since this is now inline data
        delattr(self, "url")
