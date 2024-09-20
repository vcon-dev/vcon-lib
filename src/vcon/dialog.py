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
    "audio/x-mp3",
    "audio/x-mp4",
    "audio/ogg",
    "video/x-mp4",
    "video/ogg",
    "multipart/mixed",
    "message/external-body",
]


class Dialog:
    def __init__(self,
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
                 meta: Optional[dict] = None) -> None:
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
        """
        
        # Convert the start time to an ISO 8601 string from a datetime or a string
        if isinstance(start, datetime):
            start = start.isoformat()
        elif isinstance(start, str):
            start = parser.parse(start).isoformat()

        # Set the attributes
        self.type = type
        self.start = start
        self.parties = parties
        self.originator = originator
        self.mimetype = mimetype
        self.filename = filename
        self.body = body
        self.encoding = encoding
        self.url = url
        self.alg = alg
        self.signature = signature
        self.disposition = disposition
        self.party_history = party_history
        self.transferee = transferee
        self.transferor = transferor
        self.transfer_target = transfer_target
        self.original = original
        self.consultation = consultation
        self.target_dialog = target_dialog
        self.campaign = campaign
        self.interaction = interaction
        self.skill = skill
        self.duration = duration
        self.meta = meta

    def to_dict(self):
        """
        Returns a dictionary representation of the Dialog object.

        :return: a dictionary containing the Dialog object's attributes
        :rtype: dict
        """
        # Check to see if the start time provided. If not,
        # set the start time to the current time
        if not self.start:
            self.start = datetime.now().isoformat()

        dialog_dict = {
            "type": self.type,
            "start": self.start,
            "duration": self.duration,
            "parties": self.parties,
            "originator": self.originator,
            "mimetype": self.mimetype,
            "filename": self.filename,
            "body": self.body,
            "encoding": self.encoding,
            "url": self.url,
            "alg": self.alg,
            "signature": self.signature,
            "disposition": self.disposition,
            "party_history": (
                [party_history.to_dict() for party_history in self.party_history]
                if self.party_history
                else None
            ),
            "transferee": self.transferee,
            "transferor": self.transferor,
            "transfer_target": self.transfer_target,
            "original": self.original,
            "consultation": self.consultation,
            "target_dialog": self.target_dialog,
            "campaign": self.campaign,
            "interaction": self.interaction,
            "skill": self.skill,
            "meta": self.meta
        }
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

        # Overide the filename if provided, otherwise use the filename from the URL
        if filename:
            self.filename = filename
        else:
            self.filename = url.split("/")[-1]

        # Overide the mimetype if provided, otherwise use the mimetype from the URL
        if mimetype:
            self.mimetype = mimetype

        # Calculate the SHA-256 hash of the body as the signature
        self.alg = "sha256"
        self.encoding = "base64url"
        self.signature = base64.urlsafe_b64encode(hashlib.sha256(response.text.encode()).digest()).decode()

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
            hashlib.sha256(self.body.encode()).digest()).decode()

    # Check if the dialog is an external data dialog
    def is_external_data(self) -> bool:
        return self.url is not None

    # Check if the dialog is an inline data dialog
    def is_inline_data(self) -> bool:
        return self.body is not None


    # Check if the dialog is a text dialog
    def is_text(self) -> bool:
        return self.mimetype == "text/plain"


    # Check if the dialog is an audio dialog
    def is_audio(self) -> bool:
        return self.mimetype in ["audio/x-wav", "audio/x-mp3", "audio/x-mp4", "audio/ogg"]


    # Check if the dialog is a video dialog
    def is_video(self) -> bool:
        return self.mimetype in ["video/x-mp4", "video/ogg"]

    # Check if the dialog is an email dialog
    def is_email(self) -> bool:
        return self.mimetype == "message/rfc822"

    # Check to see if it's an external data dialog, that the contents are valid by
    # checking the hash of the body against the signature
    def is_external_data_changed(self) -> bool:
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
        # Read the contents from the URL
        response = requests.get(self.url)
        if response.status_code == 200:
            self.body = response.text
            self.mimetype = response.headers["Content-Type"]
        else:
            raise Exception(f"Failed to fetch external data: {response.status_code}")

        # Calculate the SHA-256 hash of the body as the signature
        self.alg = "sha256"
        self.encoding = "base64url"
        self.signature = base64.urlsafe_b64encode(hashlib.sha256(self.body.encode()).digest()).decode()

        # Overide the filename if provided, otherwise use the filename from the URL
        if self.filename:
            self.filename = self.filename
        else:
            self.filename = self.url.split("/")[-1]

        # Overide the mimetype if provided, otherwise use the mimetype from the URL
        if self.mimetype:
            self.mimetype = self.mimetype

        # Add the body to the dialog
        self.add_inline_data(self.body, self.filename, self.mimetype)