from __future__ import annotations

import copy
import json
from typing import Optional, Union, Any
import hashlib
import time
import uuid6
from datetime import datetime
from datetime import timezone
from pydash import get as _get
import base64
from authlib.jose import JsonWebSignature
from authlib.jose.errors import BadSignatureError
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from .party import Party
from .dialog import Dialog
from dateutil import parser

_LAST_V8_TIMESTAMP = None

from __future__ import annotations
import copy
import json
from typing import Optional, Union, Any
from datetime import datetime, timezone
from dateutil import parser

_ALLOWED_PROPERTIES = {
    "uuid",
    "vcon",
    "created_at",
    "updated_at",
    "redacted",
    "group",
    "parties",
    "dialog",
    "attachments",
    "analysis",
    "signatures",
    "payload",
}

class Vcon:
    def __init__(self, vcon_dict: dict = None):
        # Existing initialization code
        if vcon_dict is None:
            vcon_dict = {}
        
        # Deep copy to avoid modifying the original dictionary
        self.vcon_dict = copy.deepcopy(vcon_dict)
        
        # Existing creation_at handling logic
        if "created_at" not in self.vcon_dict:
            self.vcon_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        elif isinstance(self.vcon_dict["created_at"], datetime):
            self.vcon_dict["created_at"] = self.vcon_dict["created_at"].isoformat()

    def set_updated_at(self, timestamp: Union[str, datetime]) -> None:
        """
        Set the updated_at timestamp.
        
        Args:
            timestamp: The timestamp to set, either as ISO 8601 string or datetime object
            
        Raises:
            ValueError: If the timestamp is not a valid datetime object or ISO 8601 string
        
        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.set_updated_at(datetime.now(timezone.utc))
            >>> vcon.set_updated_at("2025-02-18T12:00:00Z")
        """
        if isinstance(timestamp, datetime):
            # Ensure timezone is set to UTC if not already specified
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            self.vcon_dict["updated_at"] = timestamp.isoformat()
        elif isinstance(timestamp, str):
            try:
                # Validate the timestamp format and convert to UTC
                parsed_timestamp = parser.parse(timestamp)
                if parsed_timestamp.tzinfo is None:
                    parsed_timestamp = parsed_timestamp.replace(tzinfo=timezone.utc)
                self.vcon_dict["updated_at"] = parsed_timestamp.isoformat()
            except ValueError:
                raise ValueError("Invalid timestamp format. Use ISO 8601 format.")
        else:
            raise ValueError("Timestamp must be either a datetime object or ISO 8601 string")

    @property
    def updated_at(self) -> Optional[str]:
        """
        Getter for the updated_at timestamp.
        
        Returns:
            str or None: The updated_at timestamp in ISO 8601 format, or None if not set
        """
        return self.vcon_dict.get("updated_at")

    def _process_properties(self, vcon_dict: dict) -> dict:
        standard_properties = {}
        non_standard_properties = {}

        for k, v in vcon_dict.items():
            if k in _ALLOWED_PROPERTIES:
                standard_properties[k] = v
            else:
                non_standard_properties[k] = v

        if self.property_handling == "meta" and non_standard_properties:
            standard_properties.setdefault("meta", {}).update(non_standard_properties)

        return standard_properties

    @classmethod
    def build_from_json(cls, json_string: str) -> Vcon:
        """
        Initialize a Vcon object from a JSON string.

        :param json_string: JSON string representing a vCon.
        :return: Vcon object.
        """
        return cls(json.loads(json_string))

    @classmethod
    def build_new(cls, created_at: Optional[Union[str, datetime]] = None) -> Vcon:
        """
        Initialize a Vcon object with default values.

        :param created_at: Optional timestamp in ISO 8601 string or datetime object.
        :return: Vcon object.
        """
        vcon_dict = {
            "uuid": cls.uuid8_domain_name("strolid.com"),
            "vcon": "0.0.1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "redacted": {},
            "group": [],
            "parties": [],
            "dialog": [],
            "attachments": [],
            "analysis": [],
        }
        return cls(vcon_dict, created_at)

    def get_created_at(self) -> str:
        """
        Retrieve the created_at timestamp.
        :return: Created_at timestamp as an ISO 8601 string.
        """
        return self.vcon_dict.get("created_at")

    def set_created_at(self, created_at: Union[str, datetime]) -> None:
        """
        Set or update the created_at timestamp.

        :param created_at: Timestamp in ISO 8601 string or datetime object.
        """
        if isinstance(created_at, datetime):
            self.vcon_dict["created_at"] = created_at.isoformat()
        elif isinstance(created_at, str):
            try:
                # Ensure it's a valid ISO 8601 timestamp
                parser.parse(created_at)
                self.vcon_dict["created_at"] = created_at
            except ValueError:
                raise ValueError("Invalid ISO 8601 timestamp.")
        else:
            raise ValueError("created_at must be a string or datetime object.")

    def set_updated_at(self, timestamp: Union[str, datetime]) -> None:
        """
        Set the updated_at timestamp.
    
        Args:
        timestamp: The timestamp to set, either as ISO 8601 string or datetime object
        
        Example:
        >>> vcon = Vcon.build_new()
        >>> vcon.set_updated_at(datetime.now(timezone.utc))
        >>> vcon.set_updated_at("2025-02-18T12:00:00Z")
        """
        if isinstance(timestamp, datetime):
            self.vcon_dict["updated_at"] = timestamp.isoformat()
        elif isinstance(timestamp, str):
            # Validate the timestamp format
            parser.parse(timestamp)  # This will raise ValueError if invalid
            self.vcon_dict["updated_at"] = timestamp
        else:
            raise ValueError("Timestamp must be either a datetime object or ISO 8601 string")

    @property
    def tags(self) -> Optional[dict]:
        """
        Returns the tags attachment.

        :return: the tags attachment
        :rtype: dict or None
        """
        return self.find_attachment_by_type("tags")

    def get_tag(self, tag_name) -> Optional[dict]:
        """
        Returns the value of a tag by name.

        :param tag_name: the name of the tag
        :type tag_name: str
        :return: the value of the tag or None if not found
        :rtype: str or None
        """
        tags_attachment = self.find_attachment_by_type("tags")
        if not tags_attachment:
            return None
        tag = next(
            (t for t in tags_attachment["body"] if t.startswith(f"{tag_name}:")), None
        )
        if not tag:
            return None
        tag_value = tag.split(":")[1]
        return tag_value

    def add_tag(self, tag_name, tag_value) -> None:
        """
        Adds a tag to the vCon.

        :param tag_name: the name of the tag
        :type tag_name: str
        :param tag_value: the value of the tag
        :type tag_value: str
        :return: None
        :rtype: None
        """
        tags_attachment = self.find_attachment_by_type("tags")
        if not tags_attachment:
            tags_attachment = {
                "type": "tags",
                "body": [],
                "encoding": "json",
            }
            self.vcon_dict["attachments"].append(tags_attachment)
        tags_attachment["body"].append(f"{tag_name}:{tag_value}")

    def find_attachment_by_type(self, type: str) -> Optional[dict]:
        """
        Finds an attachment by type.

        :param type: the type of the attachment
        :type type: str
        :return: the attachment or None if not found
        :rtype: dict or None
        """
        return next(
            (a for a in self.vcon_dict["attachments"] if a["type"] == type), None
        )

    def add_attachment(
        self, *, body: Union[dict, list, str], type: str, encoding="none"
    ) -> None:
        """
        Adds an attachment to the vCon.

        :param body: the body of the attachment
        :type body: Union[dict, list, str]
        :param type: the type of the attachment
        :type type: str
        :param encoding: the encoding of the attachment body
        :type encoding: str
        :return: None
        :rtype: None
        """
        if encoding not in ["json", "none", "base64url"]:
            raise Exception("Invalid encoding")

        if encoding in ["json", "base64url"]:
            try:
                json.loads(body) if encoding == "json" else base64.urlsafe_b64decode(body)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid {encoding} body: {e}")

        attachment = {
            "type": type,
            "body": body,
            "encoding": encoding,
        }
        self.vcon_dict["attachments"].append(attachment)

    def find_analysis_by_type(self, type) -> Any | None:
        """
        Finds an analysis by type.

        :param type: the type of the analysis
        :type type: str
        :return: the analysis or None if not found
        :rtype: dict or None
        """
        return next((a for a in self.vcon_dict["analysis"] if a["type"] == type), None)

    def add_analysis(
        self,
        *,
        type: str,
        dialog: Union[int, list[int]],
        vendor: str,
        body: Union[dict, list, str],
        encoding="none",
        extra=None,
    ) -> None:
        """
        Adds analysis data to the vCon.

        :param type: The type of the analysis.
        :param dialog: The dialog(s) associated with the analysis (int or list of int).
        :param vendor: The vendor of the analysis.
        :param body: The body of the analysis (dict, list, or str).
        :param encoding: The encoding of the body ('json', 'none', 'base64url').
        :param extra: Extra key-value pairs to include in the analysis (optional dict).
        :return: None
        """
        # Normalize encoding input
        encoding = encoding.strip().lower()
        valid_encodings = {"json", "none", "base64url"}
        if encoding not in valid_encodings:
            raise ValueError(f"Invalid encoding '{encoding}'. Must be one of {valid_encodings}.")

        if not body:
            raise ValueError("Body cannot be empty.")

        # Validate and normalize dialog input
        if isinstance(dialog, int):
            dialog = [dialog]
        elif not isinstance(dialog, list) or not all(isinstance(d, int) for d in dialog):
            raise ValueError("Dialog must be an int or a list of ints.")

        # Validate and normalize extra input
        if extra is None:
            extra = {}
        elif not isinstance(extra, dict):
            raise TypeError("Extra must be a dictionary if provided.")

       # Perform body validation based on encoding
        if encoding == "json":
            try:
                if isinstance(body, str):
                    body = json.loads(body)  # Convert from JSON string to dict/list
                elif isinstance(body, (dict, list)):
                    json.dumps(body)  # Ensure it's serializable
                else:
                    raise ValueError("Body must be a JSON-compatible dict, list, or JSON string.")
            except Exception as e:
                raise ValueError(f"Invalid JSON body: {e}")

        elif encoding == "base64url":
            if not isinstance(body, str):
                raise TypeError("Base64url encoded body must be a string.")
            try:
                base64.urlsafe_b64decode(body.encode())
            except Exception as e:
                raise ValueError(f"Invalid base64url body: {e}")

    # Append to analysis
    analysis = {
        "type": type,
        "dialog": dialog,
        "vendor": vendor,
        "body": body,
        "encoding": encoding,
        **extra,
    }
    self.vcon_dict["analysis"].append(analysis)


    def add_party(self, party: Party) -> None:
        """
        Adds a party to the vCon.

        :param party: the party to add
        :type party: Party
        :return: None
        :rtype: None
        """
        self.vcon_dict["parties"].append(party.to_dict())
        if not isinstance(party, Party):
            raise TypeError("party must be an instance of Party")


    def find_party_index(self, by: str, val: str) -> Optional[int]:
        """
        Find the index of a party in the vCon given a key-value pair.

        :param by: the key to look for
        :type by: str
        :param val: the value to look for
        :type val: str
        :return: The index of the party if found, None otherwise
        :rtype: Optional[int]
        """
        return next(
            (
                ind
                for ind, party in enumerate(self.vcon_dict["parties"])
                if _get(party, by) == val
            ),
            None,
        )

    def find_dialog(self, by: str, val: str) -> Optional[Dialog]:
        """
        Find a dialog in the vCon given a key-value pair. Convert the dialog to a Dialog object.

        :param by: the key to look for
        :type by: str
        :param val: the value to look for
        :type val: str
        :return: The dialog if found, None otherwise
        :rtype: Optional[dict]
        """
        dialog = next(
            (dialog for dialog in self.vcon_dict["dialog"] if _get(dialog, by) == val),
            None,
        )
        if dialog:
            return Dialog(**dialog)
        return None

    def add_dialog(self, dialog: Dialog) -> None:
        """
        Add a dialog to the vCon.

        :param dialog: the dialog to add
        :type dialog: dict
        :return: None
        :rtype: None
        """
        self.vcon_dict["dialog"].append(dialog.to_dict())
        if not isinstance(dialog, Dialog):
            raise TypeError("dialog must be an instance of Dialog")

    def to_json(self) -> str:
        """
        Serialize the vCon to a JSON string.

        :return: a JSON string representation of the vCon
        :rtype: str
        """
        tmp_vcon_dict = copy.copy(self.vcon_dict)
        return json.dumps(tmp_vcon_dict)

    def to_dict(self) -> dict:
        """
        Serialize the vCon to a dictionary.

        :return: a dictionary representation of the vCon
        :rtype: dict
        """
        return json.loads(self.to_json())

    def dumps(self) -> str:
        """
        Alias for `to_json()`.

        :return: a JSON string representation of the vCon
        :rtype: str
        """
        return self.to_json()

    @property
    def parties(self) -> list[Party]:
        """
        Returns the list of parties.

        :return: a list of parties
        :rtype: list[Party]
        """
        return [Party(**party) for party in self.vcon_dict.get("parties", [])]

    @property
    def dialog(self) -> list:
        return self.vcon_dict.get("dialog", [])

    @property
    def attachments(self) -> list:
        return self.vcon_dict.get("attachments", [])

    @property
    def analysis(self):
        return self.vcon_dict.get("analysis", [])

    @property
    def uuid(self) -> str:
        return self.vcon_dict["uuid"]

    @property
    def vcon(self) -> str:
        return self.vcon_dict["vcon"]

    @property
    def subject(self) -> Optional[str]:
        return self.vcon_dict.get("subject")

    @property
    def created_at(self):
        return self.vcon_dict.get("created_at")

    @property
    def updated_at(self):
        return self.vcon_dict.get("updated_at")

    @property
    def redacted(self):
        return self.vcon_dict.get("redacted")

    @property
    def appended(self):
        return self.vcon_dict.get("appended")

    @property
    def group(self):
        return self.vcon_dict.get("group", [])

    @property
    def meta(self):
        return self.vcon_dict.get("meta", {})

    @staticmethod
    def uuid8_domain_name(domain_name: str) -> str:
        sha1_hasher = hashlib.sha1()
        sha1_hasher.update(bytes(domain_name, "utf-8"))
        dn_sha1 = sha1_hasher.digest()

        hash_upper_64 = dn_sha1[0:8]
        int64 = int.from_bytes(hash_upper_64, byteorder="big")

        uuid8_domain = Vcon.uuid8_time(int64)

        return uuid8_domain

    @staticmethod
    def uuid8_time(custom_c_62_bits: int) -> str:
        global _LAST_V8_TIMESTAMP

        ns = time.time_ns()
        if _LAST_V8_TIMESTAMP is not None and ns <= _LAST_V8_TIMESTAMP:
            ns = _LAST_V8_TIMESTAMP + 1
        timestamp_ms, timestamp_ns = divmod(ns, 10**6)
        subsec = uuid6._subsec_encode(timestamp_ns)

        subsec_a = subsec >> 8
        uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
        uuid_int |= subsec_a << 64
        uuid_int |= custom_c_62_bits

        uuid_str = str(uuid6.UUID(int=uuid_int, version=7))
        assert uuid_str[14] == "7"
        uuid_str = uuid_str[:14] + "8" + uuid_str[15:]

        return uuid_str

    def sign(self, private_key) -> None:
        """
        Sign the vCon using JWS.

        :param private_key: the private key used for signing
        :type private_key: Union[rsa.RSAPrivateKey, bytes]
        :return: None
        :rtype: None
        """
        """Sign the vCon using JWS."""
        payload = self.to_json()
        jws = JsonWebSignature()
        protected = {"alg": "RS256", "typ": "JWS"}

        # Convert private key to PEM format if it's not already
        if isinstance(private_key, rsa.RSAPrivateKey):
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        else:
            pem = private_key

        signed = jws.serialize_compact(protected, payload, pem)
        signed_str = signed.decode("utf-8")
        header, payload, signature = signed_str.split(".")

        self.vcon_dict["signatures"] = [{"protected": header, "signature": signature}]
        self.vcon_dict["payload"] = payload

    def verify(self, public_key) -> bool:
        """Verify the JWS signature of the vCon.

        :param public_key: the public key used for verification
        :type public_key: Union[rsa.RSAPublicKey, bytes]
        :return: True if the signature is valid, False otherwise
        :rtype: bool
        """
        """Verify the JWS signature of the vCon."""
        if "signatures" not in self.vcon_dict or "payload" not in self.vcon_dict:
            raise ValueError("vCon is not signed")

        jws = JsonWebSignature()
        signed_data = f"{self.vcon_dict['signatures'][0]['protected']}.{self.vcon_dict['payload']}.{self.vcon_dict['signatures'][0]['signature']}"

        # Convert public key to PEM format if it's not already
        if isinstance(public_key, rsa.RSAPublicKey):
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        else:
            pem = public_key

        try:
            jws.deserialize_compact(signed_data, pem)
            return True
        except BadSignatureError:
            return False

    @classmethod
    def generate_key_pair(cls) -> tuple:
        """
        Generate a new RSA key pair for signing vCons.

        :return: a tuple containing the private key and public key
        :rtype: tuple[rSA.RSAPrivateKey, rsa.RSAPublicKey]
        """
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        return private_key, public_key
