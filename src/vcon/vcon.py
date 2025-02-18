from __future__ import annotations

import copy
from dateutil import parser
import json
from typing import Optional, Union, Any, List, Dict, Tuple
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
import requests
import logging
from .party import Party
from .dialog import Dialog

# Configure logging
logger = logging.getLogger(__name__)

_LAST_V8_TIMESTAMP = None


class Attachment:
    """
    A class representing an attachment in a vCon.
    
    An attachment consists of a type, body content, and an encoding format.
    The encoding format must be one of the supported formats: base64, base64url, or none.
    
    Attributes:
        type (str): The type of the attachment
        body (Any): The content of the attachment
        encoding (str): The encoding format used for the body
    """

    VALID_ENCODINGS = ["base64", "base64url", "none"]

    def __init__(self, type: str, body: Any, encoding: str = "none") -> None:
        """
        Initialize an Attachment object.
        
        Args:
            type: The type of the attachment
            body: The content of the attachment
            encoding: The encoding format used for the body (default: "none")
            
        Raises:
            ValueError: If the specified encoding is not supported
        """
        if encoding not in self.VALID_ENCODINGS:
            logger.error(f"Invalid encoding attempted: {encoding}")
            raise ValueError(f"Invalid encoding: {encoding}. Must be one of {self.VALID_ENCODINGS}")
        self.type = type
        self.body = body
        self.encoding = encoding
        logger.debug(f"Created new attachment of type {type} with {encoding} encoding")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the attachment to a dictionary representation.
        
        Returns:
            Dict containing the attachment's type, body, and encoding
        """
        return {"type": self.type, "body": self.body, "encoding": self.encoding}


class Vcon:
    """
    A class representing a vCon (Virtual Conversation) object.
    
    A vCon is a standardized format for representing conversations and related metadata.
    It includes information about participants (parties), dialog content, attachments,
    and analysis data.
    
    The vCon format supports features such as:
    - Unique identification via UUID
    - Versioning
    - Timestamps for creation and updates
    - Party information
    - Dialog content
    - Attachments
    - Analysis data
    - Digital signatures
    
    Attributes:
        vcon_dict (Dict): The underlying dictionary containing all vCon data
    """

    def __init__(self, vcon_dict: Dict[str, Any] = {}) -> None:
        """
        Initialize a Vcon object from a dictionary.

        This constructor creates a new vCon object from a dictionary representation.
        If no dictionary is provided, it creates an empty vCon with default values.
        The constructor ensures that required fields like created_at and attachments
        are properly initialized.

        Args:
            vcon_dict: A dictionary representing a vCon. Defaults to an empty dict.

        Example:
            >>> vcon = Vcon({"uuid": "123", "vcon": "0.0.1"})
            >>> vcon = Vcon()  # Creates an empty vCon with default values
        """
        logger.debug("Initializing new Vcon object")
        
        # If the vcon_dict contains a created_at in datetime or in string, format it like a ISO 8601
        if vcon_dict.get("created_at"):
            if isinstance(vcon_dict["created_at"], datetime):
                vcon_dict["created_at"] = vcon_dict["created_at"].isoformat()
                logger.debug("Converted datetime created_at to ISO format")
            elif isinstance(vcon_dict["created_at"], str):
                vcon_dict["created_at"] = parser.parse(
                    vcon_dict["created_at"]
                ).isoformat()
                logger.debug("Parsed string created_at to ISO format")
        else:
            vcon_dict["created_at"] = datetime.now(timezone.utc).isoformat()
            logger.debug("Set default created_at timestamp")

        # Ensure attachments array exists
        if "attachments" not in vcon_dict:
            vcon_dict["attachments"] = []
            logger.debug("Initialized empty attachments array")

        self.vcon_dict = json.loads(json.dumps(vcon_dict))
        logger.info(f"Vcon object initialized with UUID: {vcon_dict.get('uuid', 'not set')}")

    @classmethod
    def build_from_json(cls, json_string: str) -> Vcon:
        """
        Initialize a Vcon object from a JSON string.

        This method parses a JSON string representation of a vCon and creates
        a new Vcon object from it.

        Args:
            json_string: A JSON string representing a vCon

        Returns:
            A new Vcon object initialized with the parsed JSON data

        Raises:
            json.JSONDecodeError: If the JSON string is invalid
            
        Example:
            >>> json_str = '{"uuid": "123", "vcon": "0.0.1"}'
            >>> vcon = Vcon.build_from_json(json_str)
        """
        logger.debug("Building Vcon from JSON string")
        try:
            vcon_dict = json.loads(json_string)
            logger.info("Successfully parsed JSON string")
            return cls(vcon_dict)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON string: {str(e)}")
            raise

    @classmethod
    def build_new(cls) -> Vcon:
        """
        Initialize a new Vcon object with default values.

        This method creates a new vCon with a generated UUID, default version,
        and initialized with empty arrays for groups, parties, dialog, attachments,
        and analysis.

        Returns:
            A new Vcon object with default values

        Example:
            >>> vcon = Vcon.build_new()
            >>> print(vcon.uuid)  # Prints a new UUID8
        """
        logger.debug("Building new Vcon with default values")
        uuid = cls.uuid8_domain_name("strolid.com")
        logger.debug(f"Generated UUID8: {uuid}")
        
        vcon_dict = {
            "uuid": uuid,
            "vcon": "0.0.1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "redacted": {},
            "group": [],
            "parties": [],
            "dialog": [],
            "attachments": [],
            "analysis": [],
        }
        logger.info("Created new Vcon with default structure")
        return cls(vcon_dict)

    @property
    def tags(self) -> Optional[Dict[str, Any]]:
        """
        Get the tags attachment from the vCon.

        Returns:
            The tags attachment dictionary if it exists, None otherwise

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_tag("category", "meeting")
            >>> tags = vcon.tags
            >>> print(tags["body"])  # Prints ["category:meeting"]
        """
        logger.debug("Retrieving tags attachment")
        tags = self.find_attachment_by_type("tags")
        if tags:
            logger.debug("Found tags attachment")
        else:
            logger.debug("No tags attachment found")
        return tags

    def get_tag(self, tag_name: str) -> Optional[str]:
        """
        Get the value of a specific tag by name.

        Args:
            tag_name: The name of the tag to retrieve

        Returns:
            The value of the tag if found, None otherwise

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_tag("category", "meeting")
            >>> value = vcon.get_tag("category")
            >>> print(value)  # Prints "meeting"
        """
        logger.debug(f"Retrieving value for tag: {tag_name}")
        tags_attachment = self.find_attachment_by_type("tags")
        if not tags_attachment:
            logger.debug("No tags attachment found")
            return None
            
        tag = next(
            (t for t in tags_attachment["body"] if t.startswith(f"{tag_name}:")), None
        )
        if not tag:
            logger.debug(f"Tag {tag_name} not found")
            return None
            
        tag_value = tag.split(":")[1]
        logger.debug(f"Found value for tag {tag_name}: {tag_value}")
        return tag_value

    def add_tag(self, tag_name: str, tag_value: str) -> None:
        """
        Add a tag to the vCon.

        This method adds a tag with the specified name and value to the vCon's tags
        attachment. If no tags attachment exists, it creates one.

        Args:
            tag_name: The name of the tag
            tag_value: The value to associate with the tag

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_tag("category", "meeting")
            >>> vcon.add_tag("priority", "high")
        """
        logger.debug(f"Adding tag {tag_name}:{tag_value}")
        tags_attachment = self.find_attachment_by_type("tags")
        if not tags_attachment:
            logger.debug("Creating new tags attachment")
            tags_attachment = {
                "type": "tags",
                "body": [],
                "encoding": "json",
            }
            self.vcon_dict["attachments"].append(tags_attachment)
        tags_attachment["body"].append(f"{tag_name}:{tag_value}")
        logger.info(f"Added tag {tag_name}:{tag_value}")

    def find_attachment_by_type(self, type: str) -> Optional[Dict[str, Any]]:
        """
        Find an attachment in the vCon by its type.

        This method searches through the vCon's attachments and returns the first
        attachment matching the specified type.

        Args:
            type: The type of attachment to find

        Returns:
            The matching attachment dictionary if found, None otherwise

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_attachment("metadata", {"version": "1.0"})
            >>> metadata = vcon.find_attachment_by_type("metadata")
        """
        logger.debug(f"Searching for attachment of type: {type}")
        attachment = next(
            (a for a in self.vcon_dict["attachments"] if a["type"] == type), None
        )
        if attachment:
            logger.debug(f"Found attachment of type: {type}")
        else:
            logger.debug(f"No attachment found of type: {type}")
        return attachment

    def add_attachment(self, type: str, body: Any, encoding: str = "none") -> Attachment:
        """
        Add an attachment to the vCon.

        This method creates a new attachment with the specified type, body, and encoding
        and adds it to the vCon's attachments list.

        Args:
            type: The type of the attachment
            body: The content of the attachment
            encoding: The encoding format for the body (default: "none")

        Returns:
            The created Attachment object

        Raises:
            ValueError: If the specified encoding is not supported

        Example:
            >>> vcon = Vcon.build_new()
            >>> attachment = vcon.add_attachment("metadata", {"version": "1.0"}, "json")
            >>> print(attachment.type)  # Prints "metadata"
        """
        logger.debug(f"Creating new attachment of type {type} with {encoding} encoding")
        
        attachment = Attachment(type, body, encoding)
        self.vcon_dict["attachments"].append(attachment.to_dict())
        
        logger.info(f"Added new attachment of type {type}")
        return attachment

    def find_analysis_by_type(self, type: str) -> Optional[Dict[str, Any]]:
        """
        Find an analysis entry in the vCon by its type.

        This method searches through the vCon's analysis entries and returns the first
        one matching the specified type.

        Args:
            type: The type of analysis to find

        Returns:
            The matching analysis dictionary if found, None otherwise

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_analysis(type="sentiment", dialog=[0], vendor="acme", body={"score": 0.8})
            >>> sentiment = vcon.find_analysis_by_type("sentiment")
        """
        logger.debug(f"Searching for analysis of type: {type}")
        analysis = next(
            (a for a in self.vcon_dict["analysis"] if a["type"] == type), None
        )
        if analysis:
            logger.debug(f"Found analysis of type: {type}")
        else:
            logger.debug(f"No analysis found of type: {type}")
        return analysis

    def add_analysis(
        self,
        *,
        type: str,
        dialog: Union[List[int], int],
        vendor: str,
        body: Union[Dict[str, Any], List[Any], str],
        encoding: str = "none",
        extra: Dict[str, Any] = {},
    ) -> None:
        """
        Add analysis data to the vCon.

        This method adds analysis data with the specified parameters to the vCon's
        analysis list. Analysis data can be associated with one or more dialog entries
        and includes metadata about the vendor who performed the analysis.

        Args:
            type: The type of analysis
            dialog: Index or list of indices of the associated dialog entries
            vendor: The name of the vendor who performed the analysis
            body: The analysis data
            encoding: The encoding format of the body (default: "none")
            extra: Additional key-value pairs to include in the analysis (default: {})

        Raises:
            Exception: If the encoding is invalid or if the body format is invalid for the specified encoding

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_analysis(
            ...     type="sentiment",
            ...     dialog=[0],
            ...     vendor="acme",
            ...     body={"score": 0.8},
            ...     encoding="json"
            ... )
        """
        logger.debug(f"Adding analysis of type {type} from vendor {vendor}")

        if encoding not in ["json", "none", "base64url"]:
            logger.error(f"Invalid encoding: {encoding}")
            raise Exception("Invalid encoding")

        if encoding == "json":
            try:
                json.loads(body)
            except Exception as e:
                logger.error(f"Invalid JSON body: {str(e)}")
                raise Exception("Invalid JSON body: ", e)

        if encoding == "base64url":
            try:
                base64.urlsafe_b64decode(body)
            except Exception as e:
                logger.error(f"Invalid base64url body: {str(e)}")
                raise Exception("Invalid base64url body: ", e)

        analysis = {
            "type": type,
            "dialog": dialog,
            "vendor": vendor,
            "body": body,
            "encoding": encoding,
            **extra,
        }
        self.vcon_dict["analysis"].append(analysis)
        logger.info(f"Added analysis of type {type} from vendor {vendor}")

    def add_party(self, party: Party) -> None:
        """
        Add a party to the vCon.

        This method adds a party object to the vCon's parties list. A party represents
        a participant in the conversation.

        Args:
            party: The Party object to add

        Example:
            >>> vcon = Vcon.build_new()
            >>> party = Party(type="person", name="John Doe")
            >>> vcon.add_party(party)
        """
        logger.debug(f"Adding party: {party.to_dict()}")
        self.vcon_dict["parties"].append(party.to_dict())

    def find_party_index(self, by: str, val: str) -> Optional[int]:
        """
        Find the index of a party in the vCon's parties list.

        This method searches through the parties list and returns the index of the first
        party that matches the specified key-value pair.

        Args:
            by: The key to search by (e.g., "name", "type")
            val: The value to match

        Returns:
            The index of the matching party if found, None otherwise

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_party(Party(type="person", name="John Doe"))
            >>> index = vcon.find_party_index("name", "John Doe")
            >>> print(index)  # Prints 0
        """
        logger.debug(f"Searching for party with {by}={val}")
        index = next(
            (
                ind
                for ind, party in enumerate(self.vcon_dict["parties"])
                if _get(party, by) == val
            ),
            None,
        )
        if index is not None:
            logger.debug(f"Found party at index {index}")
        else:
            logger.debug(f"No party found with {by}={val}")
        return index

    def find_dialog(self, by: str, val: str) -> Optional[Dialog]:
        """
        Find a dialog entry in the vCon by a key-value pair.

        This method searches through the dialog list and returns the first dialog
        entry that matches the specified key-value pair, converted to a Dialog object.

        Args:
            by: The key to search by (e.g., "type", "start")
            val: The value to match

        Returns:
            A Dialog object if found, None otherwise

        Example:
            >>> vcon = Vcon.build_new()
            >>> dialog = Dialog(type="text", start="2023-01-01T00:00:00Z", parties=[0])
            >>> vcon.add_dialog(dialog)
            >>> found = vcon.find_dialog("type", "text")
            >>> print(found.type)  # Prints "text"
        """
        logger.debug(f"Searching for dialog with {by}={val}")
        dialog = next(
            (dialog for dialog in self.vcon_dict["dialog"] if _get(dialog, by) == val),
            None,
        )
        if dialog:
            logger.debug(f"Found dialog with {by}={val}")
            return Dialog(**dialog)
        logger.debug(f"No dialog found with {by}={val}")
        return None

    def add_dialog(self, dialog: Dialog) -> None:
        """
        Add a dialog entry to the vCon.

        This method adds a Dialog object to the vCon's dialog list. A dialog entry
        represents a segment of the conversation with its associated metadata.

        Args:
            dialog: The Dialog object to add

        Example:
            >>> vcon = Vcon.build_new()
            >>> dialog = Dialog(type="text", start="2023-01-01T00:00:00Z", parties=[0])
            >>> vcon.add_dialog(dialog)
        """
        logger.debug(f"Adding dialog: {dialog.to_dict()}")
        self.vcon_dict["dialog"].append(dialog.to_dict())
        logger.info(f"Added dialog of type {dialog.type}")

    def to_json(self) -> str:
        """
        Serialize the vCon to a JSON string.

        This method converts the entire vCon object to a JSON string representation,
        which can be used for storage or transmission.

        Returns:
            A JSON string representation of the vCon

        Example:
            >>> vcon = Vcon.build_new()
            >>> json_str = vcon.to_json()
            >>> print(type(json_str))  # Prints "<class 'str'>"
        """
        logger.debug("Converting vCon to JSON string")
        tmp_vcon_dict = copy.copy(self.vcon_dict)
        json_str = json.dumps(tmp_vcon_dict)
        logger.debug("Successfully converted vCon to JSON string")
        return json_str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the vCon to a dictionary.

        This method returns a dictionary representation of the vCon object,
        which can be used for direct manipulation or inspection.

        Returns:
            A dictionary representation of the vCon

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon_dict = vcon.to_dict()
            >>> print(vcon_dict["vcon"])  # Prints "0.0.1"
        """
        logger.debug("Converting vCon to dictionary")
        return json.loads(self.to_json())

    def dumps(self) -> str:
        """
        Alias for to_json().

        This method is an alias for to_json() and converts the vCon object to a
        JSON string representation.

        Returns:
            A JSON string representation of the vCon

        Example:
            >>> vcon = Vcon.build_new()
            >>> json_str = vcon.dumps()
            >>> print(type(json_str))  # Prints "<class 'str'>"
        """
        logger.debug("Dumping vCon to JSON string")
        return self.to_json()

    @property
    def parties(self) -> List[Party]:
        """
        Get the list of parties in the vCon.

        Returns:
            A list of Party objects representing all participants in the conversation

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_party(Party(type="person", name="John Doe"))
            >>> parties = vcon.parties
            >>> print(parties[0].name)  # Prints "John Doe"
        """
        return [Party(**party) for party in self.vcon_dict.get("parties", [])]

    @property
    def dialog(self) -> List[Dict[str, Any]]:
        """
        Get the list of dialog entries in the vCon.

        Returns:
            A list of dialog entries representing the conversation content

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_dialog(Dialog(type="text", start="2023-01-01T00:00:00Z", parties=[0]))
            >>> dialog = vcon.dialog
            >>> print(dialog[0]["type"])  # Prints "text"
        """
        return self.vcon_dict.get("dialog", [])

    @property
    def attachments(self) -> List[Dict[str, Any]]:
        """
        Get the list of attachments in the vCon.

        Returns:
            A list of attachment dictionaries

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_attachment("metadata", {"version": "1.0"})
            >>> attachments = vcon.attachments
            >>> print(attachments[0]["type"])  # Prints "metadata"
        """
        return self.vcon_dict.get("attachments", [])

    @property
    def analysis(self) -> List[Dict[str, Any]]:
        """
        Get the list of analysis entries in the vCon.

        Returns:
            A list of analysis dictionaries

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_analysis(type="sentiment", dialog=[0], vendor="acme", body={"score": 0.8})
            >>> analysis = vcon.analysis
            >>> print(analysis[0]["type"])  # Prints "sentiment"
        """
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

    def sign(self, private_key: Union[rsa.RSAPrivateKey, bytes]) -> None:
        """
        Sign the vCon using JWS (JSON Web Signature).

        This method signs the vCon using the provided private key, adding the signature
        information to the vCon. The signature can later be verified using the
        corresponding public key.

        Args:
            private_key: The RSA private key or its PEM representation

        Raises:
            Exception: If there is an error during the signing process

        Example:
            >>> from cryptography.hazmat.primitives.asymmetric import rsa
            >>> private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            >>> vcon = Vcon.build_new()
            >>> vcon.sign(private_key)
        """
        logger.debug("Signing vCon with JWS")
        try:
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
            logger.info("Successfully signed vCon")
        except Exception as e:
            logger.error(f"Failed to sign vCon: {str(e)}")
            raise

    def verify(self, public_key: Union[rsa.RSAPublicKey, bytes]) -> bool:
        """
        Verify the JWS signature of the vCon.

        This method verifies the vCon's signature using the provided public key.
        The vCon must have been previously signed using the corresponding private key.

        Args:
            public_key: The RSA public key or its PEM representation

        Returns:
            True if the signature is valid, False otherwise

        Raises:
            ValueError: If the vCon is not signed

        Example:
            >>> private_key, public_key = Vcon.generate_key_pair()
            >>> vcon = Vcon.build_new()
            >>> vcon.sign(private_key)
            >>> is_valid = vcon.verify(public_key)
            >>> print(is_valid)  # Prints True
        """
        logger.debug("Verifying vCon signature")
        
        if "signatures" not in self.vcon_dict or "payload" not in self.vcon_dict:
            logger.error("Cannot verify: vCon is not signed")
            raise ValueError("vCon is not signed")
        
        try:
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

            jws.deserialize_compact(signed_data, pem)
            logger.info("Successfully verified vCon signature")
            return True
        except BadSignatureError:
            logger.warning("Invalid signature detected")
            return False
        except Exception as e:
            logger.error(f"Error during signature verification: {str(e)}")
            return False

    @classmethod
    def generate_key_pair(cls) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """
        Generate a new RSA key pair for signing vCons.

        This method generates a new RSA key pair that can be used for signing
        and verifying vCons.

        Returns:
            A tuple containing the private key and public key

        Example:
            >>> private_key, public_key = Vcon.generate_key_pair()
            >>> vcon = Vcon.build_new()
            >>> vcon.sign(private_key)
            >>> is_valid = vcon.verify(public_key)
        """
        logger.debug("Generating new RSA key pair")
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        logger.info("Successfully generated RSA key pair")
        return private_key, public_key

    def is_valid(self) -> Tuple[bool, List[str]]:
        """
        Validate the vCon syntax according to the standard.

        Checks required fields, ensures data types are correct, and verifies
        relationships between different parts of the vCon (for example, dialog party
        references and attachment fields).

        Returns:
            Tuple[bool, List[str]]: A tuple where the first element is True if the vCon
            is valid and False otherwise, and the second element is a list of error messages.
        """
        logger.debug("Validating vCon")
        errors = []

        # Validate required fields.
        required_fields = ["uuid", "vcon", "created_at"]
        for field in required_fields:
            if field not in self.vcon_dict:
                error = f"Missing required field: {field}"
                logger.error(error)
                errors.append(error)

        # Validate created_at format.
        if "created_at" in self.vcon_dict:
            try:
                parser.parse(self.vcon_dict["created_at"])
            except Exception as e:
                error = f"Invalid created_at format. Must be an ISO 8601 datetime string: {str(e)}"
                logger.error(error)
                errors.append(error)

        # Validate parties.
        if "parties" in self.vcon_dict:
            if not isinstance(self.vcon_dict["parties"], list):
                error = "Field 'parties' must be a list."
                logger.error(error)
                errors.append(error)
            else:
                for i, party in enumerate(self.vcon_dict["parties"]):
                    if not isinstance(party, dict):
                        error = f"Party at index {i} must be a dictionary."
                        logger.error(error)
                        errors.append(error)

        # Validate dialogs.
        dialogs = self.vcon_dict.get("dialog", [])
        for i, dialog in enumerate(dialogs):
            if not isinstance(dialog, dict):
                errors.append(f"Dialog at index {i} must be a dictionary.")
                continue

            # Validate party references in dialog.
            if "parties" in dialog:
                if not isinstance(dialog["parties"], list):
                    errors.append(f"Dialog at index {i} field 'parties' must be a list.")
                else:
                    party_count = len(self.vcon_dict.get("parties", []))
                    for party_idx in dialog["parties"]:
                        if not isinstance(party_idx, int) or party_idx < 0 or party_idx >= party_count:
                            errors.append(f"Dialog at index {i} references invalid party index: {party_idx}")

            # Validate start time format if present.
            if "start" in dialog:
                try:
                    parser.parse(dialog["start"])
                except Exception:
                    errors.append(f"Dialog at index {i} has an invalid 'start' format. Must be an ISO 8601 datetime string.")

            # Validate mimetype.
            if ("mimetype" not in dialog or
                not isinstance(dialog["mimetype"], str) or
                dialog["mimetype"] not in Dialog.MIME_TYPES):
                errors.append(f"Dialog at index {i} has an invalid or missing mimetype: {dialog.get('mimetype', 'missing')}")

        # Validate attachments.
        if "attachments" in self.vcon_dict:
            if not isinstance(self.vcon_dict["attachments"], list):
                errors.append("Field 'attachments' must be a list.")
            else:
                for i, attachment in enumerate(self.vcon_dict["attachments"]):
                    if not isinstance(attachment, dict):
                        errors.append(f"Attachment at index {i} must be a dictionary.")
                    else:
                        # Check for required attachment fields.
                        required_attachment_fields = ["type", "body", "encoding"]
                        for field in required_attachment_fields:
                            if field not in attachment:
                                errors.append(f"Attachment at index {i} is missing required field: {field}")
                        # Validate encoding.
                        if ("encoding" in attachment and
                            attachment["encoding"] not in ["json", "none", "base64url"]):
                            errors.append(f"Attachment at index {i} has invalid encoding: {attachment['encoding']}")

        # Validate analysis.
        if "analysis" in self.vcon_dict:
            if not isinstance(self.vcon_dict["analysis"], list):
                errors.append("Field 'analysis' must be a list.")
            else:
                for i, analysis in enumerate(self.vcon_dict["analysis"]):
                    if not isinstance(analysis, dict):
                        errors.append(f"Analysis at index {i} must be a dictionary.")
                    else:
                        # Required analysis fields.
                        required_analysis_fields = ["type", "dialog", "vendor", "body", "encoding"]
                        for field in required_analysis_fields:
                            if field not in analysis:
                                errors.append(f"Analysis at index {i} is missing required field: {field}")
                        # Validate encoding.
                        if ("encoding" in analysis and
                            analysis["encoding"] not in ["json", "none", "base64url"]):
                            errors.append(f"Analysis at index {i} has invalid encoding: {analysis['encoding']}")
                        # Validate dialog references within analysis.
                        dialog_count = len(dialogs)
                        if "dialog" in analysis:
                            if isinstance(analysis["dialog"], list):
                                for dialog_idx in analysis["dialog"]:
                                    if not isinstance(dialog_idx, int) or dialog_idx < 0 or dialog_idx >= dialog_count:
                                        errors.append(f"Analysis at index {i} references invalid dialog index: {dialog_idx}")
                            elif isinstance(analysis["dialog"], int):
                                if analysis["dialog"] < 0 or analysis["dialog"] >= dialog_count:
                                    errors.append(f"Analysis at index {i} references invalid dialog index: {analysis['dialog']}")
                            else:
                                errors.append(f"Analysis at index {i} has an invalid 'dialog' reference type.")

        if len(errors) == 0:
            logger.info("vCon validation successful.")
        else:
            logger.warning(f"vCon validation failed with {len(errors)} error(s).")
        return len(errors) == 0, errors

    @staticmethod
    def validate_file(file_path: str) -> tuple[bool, list[str]]:
        """
        Validate a vCon file at the given path.

        :param file_path: Path to the vCon JSON file
        :type file_path: str
        :return: A tuple containing (is_valid, list_of_errors)
        :rtype: tuple[bool, list[str]]
        """
        try:
            with open(file_path, "r") as f:
                json_str = f.read()
            return Vcon.validate_json(json_str)
        except FileNotFoundError:
            return False, ["File not found"]
        except json.JSONDecodeError:
            return False, ["Invalid JSON format"]
        except Exception as e:
            return False, [f"Error reading file: {str(e)}"]

    @staticmethod
    def validate_json(json_str: str) -> tuple[bool, list[str]]:
        """
        Validate a vCon from a JSON string.

        :param json_str: JSON string representing a vCon
        :type json_str: str
        :return: A tuple containing (is_valid, list_of_errors)
        :rtype: tuple[bool, list[str]]
        """
        try:
            vcon = Vcon.build_from_json(json_str)
            return vcon.is_valid()
        except json.JSONDecodeError:
            return False, ["Invalid JSON format"]
        except Exception as e:
            return False, [f"Error parsing vCon: {str(e)}"]

    @classmethod
    def load(cls, source: str) -> Vcon:
        """
        Load a vCon from either a file path or URL.

        :param source: File path or URL to load the vCon from
        :type source: str
        :return: A Vcon object
        :rtype: Vcon
        :raises ValueError: If the source is invalid or cannot be loaded
        :raises requests.RequestException: If there is an error fetching from URL
        :raises json.JSONDecodeError: If the source contains invalid JSON
        """
        if source.startswith(('http://', 'https://')):
            return cls.load_from_url(source)
        else:
            return cls.load_from_file(source)

    @classmethod
    def load_from_file(cls, file_path: str) -> Vcon:
        """
        Load a vCon from a file.

        :param file_path: Path to the vCon JSON file
        :type file_path: str
        :return: A Vcon object
        :rtype: Vcon
        :raises FileNotFoundError: If the file does not exist
        :raises json.JSONDecodeError: If the file contains invalid JSON
        """
        try:
            with open(file_path, 'r') as f:
                json_str = f.read()
            return cls.build_from_json(json_str)
        except FileNotFoundError:
            raise FileNotFoundError(f"vCon file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in vCon file: {str(e)}", e.doc, e.pos)

    @classmethod
    def load_from_url(cls, url: str) -> Vcon:
        """
        Load a vCon from a URL.

        :param url: URL to fetch the vCon JSON from
        :type url: str
        :return: A Vcon object
        :rtype: Vcon
        :raises requests.RequestException: If there is an error fetching from URL
        :raises json.JSONDecodeError: If the response contains invalid JSON
        """
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return cls.build_from_json(response.text)

    def save_to_file(self, file_path: str) -> None:
        """
        Save the vCon to a JSON file.

        :param file_path: Path where the vCon JSON should be saved
        :type file_path: str
        :raises IOError: If there is an error writing to the file
        """
        logger.debug(f"Saving vCon to file: {file_path}")
        try:
            with open(file_path, 'w') as f:
                f.write(self.to_json())
            logger.info(f"Successfully saved vCon to {file_path}")
        except IOError as e:
            logger.error(f"Failed to save vCon to file: {str(e)}")
            raise

    def post_to_url(self, url: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Post the vCon as JSON to a URL with optional headers.

        :param url: The URL to post the vCon to
        :type url: str
        :param headers: Optional dictionary of HTTP headers (e.g., {'x-conserver-api-token': 'token123'})
        :type headers: Optional[Dict[str, str]]
        :return: The HTTP response from the server
        :rtype: requests.Response
        :raises requests.RequestException: If there is an error making the HTTP request
        
        Example:
            >>> vcon = Vcon.build_new()
            >>> response = vcon.post_to_url(
            ...     'https://api.example.com/vcons',
            ...     headers={'x-conserver-api-token': 'your-token-here'}
            ... )
            >>> print(response.status_code)  # Prints HTTP status code (e.g., 200 for success)
        """
        logger.debug(f"Posting vCon to URL: {url}")
        
        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json'
        }
        if headers:
            request_headers.update(headers)
        
        try:
            response = requests.post(
                url,
                data=self.to_json(),
                headers=request_headers
            )
            response.raise_for_status()
            logger.info(f"Successfully posted vCon to {url}")
            return response
        except requests.RequestException as e:
            logger.error(f"Failed to post vCon to URL: {str(e)}")
            raise
