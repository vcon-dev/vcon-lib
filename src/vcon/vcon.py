from __future__ import annotations

import copy
from dateutil import parser
import json
from typing import Optional, List, Dict, Union, Any, Tuple
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
from .dialog import Dialog, b64url_encode
from .body import decode_body
from .session import Session
from .event import Event
from .migration import (
    MigrationError,
    MigrationReport,
    migrate_0_4_0_to_0_5_0 as _migrate_0_4_0_to_0_5_0,
)
from .validation import validate_vcon_dict

# Set up logger
logger = logging.getLogger(__name__)

# Import extension framework
try:
    from .extensions.registry import get_extension_registry
    from .extensions.base import ValidationResult
    EXTENSIONS_AVAILABLE = True
except ImportError:
    EXTENSIONS_AVAILABLE = False
    logger.warning("Extensions not available - install required dependencies")

# Define constants for property handling modes
PROPERTY_HANDLING_DEFAULT = "default"  # Keep non-standard properties
PROPERTY_HANDLING_STRICT = "strict"    # Remove non-standard properties
PROPERTY_HANDLING_META = "meta"        # Move non-standard properties to meta

# Define allowed properties for each object type
_ALLOWED_VCON_PROPERTIES = {
    "uuid", "vcon", "created_at", "updated_at", "redacted_from",
    "group", "parties", "dialog", "attachments", "analysis",
    "signatures", "payload", "meta", "subject", "amended_from",
    "extensions", "critical", "sessions", "events", "redacted_strings"
}

_ALLOWED_SESSION_PROPERTIES = {
    "start", "duration", "parties", "originator", "session_id",
    "sessions", "dialog"
}

_ALLOWED_EVENT_PROPERTIES = {
    "type", "time", "sessions", "party", "dialog", "channel",
    "contributors", "button", "transferee", "transfer_target",
    "consultation", "target_session"
}

_ALLOWED_PARTY_PROPERTIES = {
    "type", "name", "contact", "meta", "external_id", "party_id",
    "tel", "stir", "mailto", "validation", "gmlpos", "civicaddress",
    "uuid", "role", "contact_list", "sip", "did", "jCard", "timezone",
    "org", "dept"
}

_ALLOWED_DIALOG_PROPERTIES = {
    "type", "start", "parties", "duration", "mediatype", "filename",
    "body", "encoding", "url", "content_hash", "disposition",
    "campaign", "interaction", "skill", "meta", "metadata",
    "signaling", "resolution", "frame_rate",
    "codec", "bitrate", "thumbnail", "streaming", "video",
    "session_id", "application", "message_id", "redacted_segments"
}

_ALLOWED_ATTACHMENT_PROPERTIES = {
    "purpose", "body", "encoding", "start", "party", "dialog", "session",
    "mediatype", "filename", "url", "content_hash"
}

_ALLOWED_ANALYSIS_PROPERTIES = {
    "type", "dialog", "sessions", "attachment", "analysis", "vendor",
    "product", "body", "encoding", "schema", "mediatype", "filename",
    "url", "content_hash", "meta"
}

# Configure logging
logger = logging.getLogger(__name__)

_LAST_V8_TIMESTAMP = None

#: JWS algorithms accepted for signing and verifying. "none" is excluded:
#: core-05 section 6.2.2, "The alg parameter MUST NOT have the value none".
PERMITTED_JWS_ALGORITHMS = (
    "RS256", "RS384", "RS512",
    "PS256", "PS384", "PS512",
    "ES256", "ES384", "ES512",
    "EdDSA",
)


class AlgorithmNotPermittedError(ValueError):
    """A JWS used ``alg`` "none" (forbidden by core-05) or an unsupported algorithm."""


class Attachment:
    """
    A class representing an attachment in a vCon.
    
    An attachment consists of a purpose, body content, and an encoding format.
    The encoding format must be one of the supported formats: base64url, json, or none.
    
    Attributes:
        purpose (str): The purpose of the attachment
        body (Any): The content of the attachment
        encoding (str): The encoding format used for the body
    """

    VALID_ENCODINGS = ["base64url", "json", "none"]

    def __init__(
        self,
        purpose: str,
        body: Any = None,
        encoding: str = "none",
        mediatype: Optional[str] = None,
        filename: Optional[str] = None,
        url: Optional[str] = None,
        content_hash: Optional[str] = None,
        start: Optional[str] = None,
        party: Optional[int] = None,
        dialog: Optional[int] = None,
        session: Optional[Union[int, List[int]]] = None,
    ) -> None:
        """
        Initialize an Attachment object.

        Under core-05 (section 4.6) an attachment needs ``party`` and at least
        one of ``dialog`` or ``session``. ``party`` defaults to 0. Neither
        ``dialog`` nor ``session`` is defaulted here, because the right index
        depends on the vCon; ``Vcon.add_attachment()`` fills in the vCon's
        Sessions when neither is given.
        
        Args:
            purpose: The purpose of the attachment
            body: The content of the attachment
            encoding: The encoding format used for the body (default: "none")
            
        Raises:
            ValueError: If the specified encoding is not supported
        """
        if encoding not in self.VALID_ENCODINGS:
            logger.error(f"Invalid encoding attempted: {encoding}")
            raise ValueError(f"Invalid encoding: {encoding}. Must be one of {self.VALID_ENCODINGS}")

        # Fill in defaults required by the WG JSON schema (every attachment
        # requires start and party; inline content requires mediatype).
        # party defaults to 0 (the add_tag() convention). dialog is no longer
        # defaulted: core-05 allows session in its place.
        if mediatype is None and encoding == "json":
            mediatype = "application/json"

        self.purpose = purpose
        self.body = body
        self.encoding = encoding
        self.mediatype = mediatype
        self.filename = filename
        self.url = url
        self.content_hash = content_hash
        self.start = start
        self.party = party if party is not None else 0
        self.dialog = dialog
        self.session = session
        logger.debug(f"Created new attachment of purpose {purpose} with {encoding} encoding")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the attachment to a dictionary representation.
        
        Returns:
            Dict containing the attachment's purpose, body, and encoding
        """
        attachment_dict = {
            "purpose": self.purpose,
            "body": self.body,
            "encoding": self.encoding,
            "mediatype": self.mediatype,
            "filename": self.filename,
            "url": self.url,
            "content_hash": self.content_hash,
            "start": self.start,
            "party": self.party,
            "dialog": self.dialog,
            "session": self.session,
        }
        return {k: v for k, v in attachment_dict.items() if v is not None}
        
    @classmethod
    def from_image(cls, image_path: str, purpose: str = "image") -> 'Attachment':
        """
        Create an Attachment from an image file.
        
        Args:
            image_path: Path to the image file
            type: The type of the attachment (default: "image")
            
        Returns:
            An Attachment object containing the image
            
        Raises:
            ValueError: If the image format is not supported
            FileNotFoundError: If the image file cannot be found
        """
        import os
        import mimetypes
        
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Detect mimetype
        mimetype, _ = mimetypes.guess_type(image_path)
        if not mimetype or mimetype not in ["image/jpeg", "image/tiff", "application/pdf"]:
            raise ValueError(f"Unsupported image format: {mimetype}. Must be JPEG, TIFF, or PDF.")
            
        # Read image data
        with open(image_path, 'rb') as f:
            image_data = f.read()
            
        filename = os.path.basename(image_path)
        # Create and return attachment
        return cls(
            purpose=purpose,
            body=b64url_encode(image_data),
            encoding="base64url",
            mediatype=mimetype,
            filename=filename,
        )


class Vcon:
    """
    A class representing a vCon (Virtual Conversation) object according to the vCon specification.
    
    A vCon is a standardized format for representing conversations and related metadata.
    It includes information about participants (parties), dialog content, attachments,
    and analysis data.
    
    The vCon format supports features such as:
    - Unique identification via UUID
    - Optional versioning (version field is optional)
    - Timestamps for creation and updates
    - Party information with contact details (tel, name, sip, did, jCard, timezone)
    - Dialog content with media types and session information
    - Attachments for ancillary documents
    - Analysis data for conversation insights
    - Digital signatures and encryption
    - Extensions and critical for extensibility
    - Civic address information for location data
    - Sessions (``sessions``) grouping dialog and events, and Events
      (``events``) for joins, drops, holds, key presses and transfers
    
    New in vCon 0.5.0 (draft-ietf-vcon-vcon-core-05):
    - ``sessions`` and ``events`` arrays; ``Session`` and ``Event`` classes
    - ``redacted_from`` and ``amended_from`` replace ``redacted`` and ``amended``
    - Attachments need ``party`` and ``dialog`` or ``session``
    - ``extensions`` MUST list every extension in use; ``alg: "none"`` is rejected
    - Dialog ``parties`` are contributors only; empty ``{}`` Dialog placeholders
    - 0.4.0 input is migrated on load (see ``migrate_0_4_0_to_0_5_0``)
    
    Attributes:
        vcon_dict (Dict): The underlying dictionary containing all vCon data
        property_handling (str): How non-standard properties are handled
    """

    def __init__(
        self,
        vcon_dict: Dict[str, Any] = None,
        property_handling: str = PROPERTY_HANDLING_DEFAULT,
        migrate_legacy: bool = True,
        strict_migration: bool = False,
    ) -> None:
        """
        Initialize a Vcon object from a dictionary.

        A dict that declares ``"vcon": "0.4.0"`` (or a signed vCon whose payload
        does) is migrated to 0.5.0 here, using ``migrate_0_4_0_to_0_5_0``. The
        report is kept in ``self.migration_report``. A dict with any other (or no)
        ``vcon`` value is taken as is.

        Args:
            vcon_dict: A dictionary representing a vCon. Defaults to an empty dict.
            property_handling: How to handle non-standard properties. 
                                Options are:
                                - "default": Keep non-standard properties (default)
                                - "strict": Remove non-standard properties
                                - "meta": Move non-standard properties to meta object
            migrate_legacy: Migrate 0.4.0 input to 0.5.0 (default True). When
                False the 0.4.0 dict is kept untouched and ``is_valid()`` will
                report it as not 0.5.0.
            strict_migration: Passed to the migration as ``strict``; raises
                ``MigrationError`` when a required field has no source.

        Example:
                    >>> vcon = Vcon({"uuid": "123", "custom_field": "value"})
        >>> strict_vcon = Vcon({"uuid": "123", "custom_field": "value"}, property_handling="strict")
        >>> meta_vcon = Vcon({"uuid": "123", "custom_field": "value"}, property_handling="meta")
        """
        logger.debug("Initializing new Vcon object")

        # Store property handling mode for later use
        self.property_handling = property_handling
        
        # Initialize with empty dict if none provided
        if vcon_dict is None:
            vcon_dict = {}

        #: MigrationReport when the input was migrated from 0.4.0, else None.
        self.migration_report: Optional[MigrationReport] = None
        if migrate_legacy and self._is_legacy_0_4_0(vcon_dict):
            migrated, self.migration_report = _migrate_0_4_0_to_0_5_0(
                vcon_dict, strict=strict_migration
            )
            logger.warning(
                "Migrated vCon %s from 0.4.0 to 0.5.0 on load (%s)",
                migrated.get("uuid"), self.migration_report.summary(),
            )
            vcon_dict = migrated
        
        # Version field is now optional - no version management required
        
        # Handle created_at
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
            
        # Process the vcon itself for non-standard properties
        processed_vcon = self._process_properties(vcon_dict, _ALLOWED_VCON_PROPERTIES)
            
        # Process embedded objects based on property_handling
        if "parties" in processed_vcon:
            processed_vcon["parties"] = [
                self._process_properties(party, _ALLOWED_PARTY_PROPERTIES) 
                for party in processed_vcon["parties"]
            ]
            
        if "dialog" in processed_vcon:
            processed_vcon["dialog"] = [
                self._process_properties(dialog, _ALLOWED_DIALOG_PROPERTIES)
                for dialog in processed_vcon["dialog"]
            ]
            
        if "sessions" in processed_vcon:
            processed_vcon["sessions"] = [
                self._process_properties(sess, _ALLOWED_SESSION_PROPERTIES)
                for sess in processed_vcon["sessions"]
            ]

        if "events" in processed_vcon:
            processed_vcon["events"] = [
                self._process_properties(event, _ALLOWED_EVENT_PROPERTIES)
                for event in processed_vcon["events"]
            ]

        if "attachments" in processed_vcon:
            processed_vcon["attachments"] = [
                self._process_properties(attachment, _ALLOWED_ATTACHMENT_PROPERTIES)
                for attachment in processed_vcon["attachments"]
            ]
            
        if "analysis" in processed_vcon:
            processed_vcon["analysis"] = [
                self._process_properties(analysis, _ALLOWED_ANALYSIS_PROPERTIES)
                for analysis in processed_vcon["analysis"]
            ]

        self.vcon_dict = json.loads(json.dumps(processed_vcon))
        logger.info(f"Vcon object initialized with UUID: {processed_vcon.get('uuid', 'not set')}")

    @staticmethod
    def _is_legacy_0_4_0(vcon_dict: Any) -> bool:
        """True if the dict declares syntax 0.4.0, directly or in a signed payload."""
        if not isinstance(vcon_dict, dict):
            return False
        if vcon_dict.get("vcon") == "0.4.0":
            return True
        if "vcon" not in vcon_dict and isinstance(vcon_dict.get("payload"), str) and "signatures" in vcon_dict:
            try:
                raw = vcon_dict["payload"]
                payload = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
                return isinstance(payload, dict) and payload.get("vcon") == "0.4.0"
            except Exception:
                return False
        return False

    @classmethod
    def migrate_0_4_0_to_0_5_0(
        cls,
        source: Union[str, Dict[str, Any]],
        strict: bool = False,
        property_handling: str = PROPERTY_HANDLING_DEFAULT,
    ) -> "Vcon":
        """
        Explicitly migrate a 0.4.0 vCon (dict or JSON string) and return a Vcon.

        The migration report is available as ``vcon.migration_report``. Unlike
        the implicit migration on load, this also accepts input with no
        ``vcon`` parameter. See :func:`vcon.migration.migrate_0_4_0_to_0_5_0`.
        """
        migrated, report = _migrate_0_4_0_to_0_5_0(source, strict=strict)
        obj = cls(migrated, property_handling=property_handling, migrate_legacy=False)
        obj.migration_report = report
        return obj

    def set_created_at(self, created_at: Union[str, datetime]) -> None:
        """
        Set the created_at field in the vCon.

        Args:
            created_at (Union[str, datetime]): The timestamp to set, either as a string in ISO format
                                           or as a datetime object.
        """
        if isinstance(created_at, datetime):
            self.vcon_dict["created_at"] = created_at.isoformat()
        else:
            self.vcon_dict["created_at"] = created_at

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

    def _process_properties(self, obj_dict: Dict[str, Any], allowed_properties: set) -> Dict[str, Any]:
        """
        Process an object dictionary based on the property handling mode.
        
        Args:
            obj_dict: The dictionary to process
            allowed_properties: Set of allowed property names
            
        Returns:
            The processed dictionary
        """
        if not isinstance(obj_dict, dict):
            return obj_dict
            
        result = {}
        non_standard = {}
        
        # Separate standard and non-standard properties
        for k, v in obj_dict.items():
            if k in allowed_properties:
                result[k] = v
            else:
                non_standard[k] = v
                
        # Handle non-standard properties based on mode
        if self.property_handling == PROPERTY_HANDLING_STRICT:
            # Ignore non-standard properties
            pass
        elif self.property_handling == PROPERTY_HANDLING_META:
            # Move non-standard properties to meta
            if non_standard:
                result.setdefault("meta", {}).update(non_standard)
        else:  # Default: Keep non-standard properties
            result.update(non_standard)
            
        return result
    
    @classmethod
    def build_from_json(
        cls,
        json_string: str,
        property_handling: str = PROPERTY_HANDLING_DEFAULT,
        migrate_legacy: bool = True,
        strict_migration: bool = False,
    ) -> "Vcon":
        """
        Initialize a Vcon object from a JSON string.

        This method parses a JSON string representation of a vCon and creates
        a new Vcon object from it.

        Args:
            json_string: A JSON string representing a vCon
            property_handling: How to handle non-standard properties.

        Returns:
            A new Vcon object initialized with the parsed JSON data

        Raises:
            json.JSONDecodeError: If the JSON string is invalid
            
        Example:
            >>> json_str = '{"uuid": "123"}'
            >>> vcon = Vcon.build_from_json(json_str)
        """
        logger.debug("Building Vcon from JSON string")
        try:
            vcon_dict = json.loads(json_string)
            logger.info("Successfully parsed JSON string")
            return cls(
                vcon_dict,
                property_handling=property_handling,
                migrate_legacy=migrate_legacy,
                strict_migration=strict_migration,
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON string: {str(e)}")
            raise

    @classmethod
    def build_new(
        cls,
        created_at: Union[str, datetime] = None,
        property_handling: str = PROPERTY_HANDLING_DEFAULT,
    ) -> "Vcon":
        """
        Initialize a new Vcon object with default values.

        This method creates a new vCon with a generated UUID and initialized 
        with empty arrays for groups, parties, dialog, attachments, and analysis.

        Args:
            created_at (Union[str, datetime], optional): The timestamp to set for creation, 
                                                    either as a string in ISO format 
                                                    or as a datetime object.
                                                    Defaults to current time.
            property_handling: How to handle non-standard properties.

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
            "vcon": "0.5.0",
            "uuid": uuid,
            "parties": [],
            "dialog": [],
            "attachments": [],
            "analysis": [],
        }

        # Create the Vcon object
        vcon = cls(
            vcon_dict,
            property_handling=property_handling,
        )

        # Set created_at if provided, otherwise it will use the default from __init__
        if created_at is not None:
            vcon.set_created_at(created_at)
        logger.info("Created new Vcon with default structure")
        return vcon

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
        tags = self.find_attachment_by_purpose("tags")
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
        tags_attachment = self.find_attachment_by_purpose("tags")
        if not tags_attachment:
            logger.debug("No tags attachment found")
            return None

        # Accept both the -04 shape (body is already the list) and legacy
        # vCons where the tags body was written as a JSON-encoded string.
        tags = decode_body(tags_attachment)
        if not isinstance(tags, list):
            logger.debug("Tags attachment body is not a list")
            return None

        tag = next(
            (t for t in tags if isinstance(t, str) and t.startswith(f"{tag_name}:")), None
        )
        if not tag:
            logger.debug(f"Tag {tag_name} not found")
            return None
            
        tag_value = tag.split(":")[1]
        logger.debug(f"Found value for tag {tag_name}: {tag_value}")
        return tag_value

    def _resolve_attachment_scope(
        self,
        dialog: Optional[int] = None,
        session: Optional[Union[int, List[int]]] = None,
    ) -> Dict[str, Any]:
        """
        Work out the ``dialog`` / ``session`` scope for a new attachment.

        Core-05 section 4.6 needs at least one of the two. When the caller gives
        neither, the attachment is scoped to every Session in the vCon; if the
        vCon has no Session yet, an empty placeholder Session is added (an empty
        Session Object is permitted) and referenced.
        """
        scope: Dict[str, Any] = {}
        if dialog is not None:
            scope["dialog"] = dialog
        if session is not None:
            scope["session"] = session
        if not scope:
            sessions = self.vcon_dict.setdefault("sessions", [])
            if not sessions:
                sessions.append({})
                logger.info("Added placeholder Session to scope an attachment")
            scope["session"] = list(range(len(sessions)))
        return scope

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
        tags_attachment = self.find_attachment_by_purpose("tags")
        if not tags_attachment:
            logger.debug("Creating new tags attachment")
            tags_attachment = {
                "purpose": "tags",
                "body": [],
                "encoding": "json",
                "mediatype": "application/json",
                "start": self.vcon_dict.get("created_at"),
                "party": 0,
            }
            tags_attachment.update(self._resolve_attachment_scope())
            self.vcon_dict["attachments"].append(tags_attachment)
        else:
            # Normalize a legacy (pre-0.10.0 / -02 convention) JSON-string
            # body to the -04 list-valued body in place, preserving
            # existing tags.
            current_tags = decode_body(tags_attachment)
            if not isinstance(current_tags, list):
                current_tags = []
            tags_attachment["body"] = current_tags
            tags_attachment.setdefault("mediatype", "application/json")
            tags_attachment.setdefault("start", self.vcon_dict.get("created_at"))
        tags_attachment["body"].append(f"{tag_name}:{tag_value}")
        logger.info(f"Added tag {tag_name}:{tag_value}")

    def get_extensions(self) -> List[str]:
        """
        Get the list of extensions used in this vCon.

        Returns:
            List of extension names, empty list if none are defined

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_extension("video")
            >>> extensions = vcon.get_extensions()
            >>> print(extensions)  # Prints ["video"]
        """
        return self.vcon_dict.get("extensions", [])

    def add_extension(self, extension: str) -> None:
        """
        Add an extension to the vCon.

        Args:
            extension: The name of the extension to add

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_extension("video")
            >>> vcon.add_extension("encryption")
        """
        if "extensions" not in self.vcon_dict:
            self.vcon_dict["extensions"] = []
        
        if extension not in self.vcon_dict["extensions"]:
            self.vcon_dict["extensions"].append(extension)
            logger.info(f"Added extension: {extension}")

    def remove_extension(self, extension: str) -> None:
        """
        Remove an extension from the vCon.

        Args:
            extension: The name of the extension to remove

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_extension("video")
            >>> vcon.remove_extension("video")
        """
        if "extensions" in self.vcon_dict and extension in self.vcon_dict["extensions"]:
            self.vcon_dict["extensions"].remove(extension)
            logger.info(f"Removed extension: {extension}")

    def get_critical(self) -> List[str]:
        """
        Get the list of critical extensions that must be supported.

        Returns:
            List of extension names that must be supported, empty list if none are defined

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_critical("encryption")
            >>> critical = vcon.get_critical()
            >>> print(critical)  # Prints ["encryption"]
        """
        return self.vcon_dict.get("critical", [])

    def add_critical(self, extension: str) -> None:
        """
        Add an extension to the critical list.

        Args:
            extension: The name of the extension that must be supported

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_critical("encryption")
            >>> vcon.add_critical("video")
        """
        if "critical" not in self.vcon_dict:
            self.vcon_dict["critical"] = []

        if extension not in self.vcon_dict["critical"]:
            self.vcon_dict["critical"].append(extension)
            logger.info(f"Added critical extension: {extension}")

    def remove_critical(self, extension: str) -> None:
        """
        Remove an extension from the critical list.

        Args:
            extension: The name of the extension to remove from critical

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_critical("encryption")
            >>> vcon.remove_critical("encryption")
        """
        if "critical" in self.vcon_dict and extension in self.vcon_dict["critical"]:
            self.vcon_dict["critical"].remove(extension)
            logger.info(f"Removed critical extension: {extension}")

    # Extension-specific methods
    def add_lawful_basis_attachment(
        self,
        lawful_basis: str,
        expiration: str,
        purpose_grants: list,
        party_index: Optional[int] = None,
        dialog_index: Optional[int] = None,
        session_index: Optional[Union[int, List[int]]] = None,
        **kwargs
    ) -> None:
        """
        Add a lawful basis attachment to the vCon.

        The attachment has ``purpose`` ``"lawful_basis"`` and, under core-05,
        is scoped to Sessions with ``session`` plus ``party``. ``party`` is the
        party recording the basis (default 0). ``session`` is ``session_index``
        if given; otherwise the Sessions that list ``dialog_index`` (when given
        and found); otherwise every Session in the vCon (an empty placeholder
        Session is added if there is none). ``dialog`` is added only when
        ``dialog_index`` is given. The ``lawful_basis`` extension name is added
        to ``extensions``.

        Args:
            lawful_basis: The lawful basis type (consent, contract, etc.)
            expiration: ISO 8601 timestamp when the lawful basis expires
            purpose_grants: List of purpose grant dictionaries
            party_index: Index of the party that records the basis (default 0)
            dialog_index: Index of the dialog this applies to (optional)
            session_index: Session index or list of indices this applies to (optional)
            **kwargs: Additional lawful basis parameters

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_lawful_basis_attachment(
            ...     lawful_basis="consent",
            ...     expiration="2026-01-01T00:00:00Z",
            ...     purpose_grants=[
            ...         {"purpose": "recording", "granted": True, "granted_at": "2025-01-01T00:00:00Z"}
            ...     ]
            ... )
        """
        if not EXTENSIONS_AVAILABLE:
            raise RuntimeError("Extensions not available")
        
        try:
            from .extensions.lawful_basis import LawfulBasisExtension
            extension = LawfulBasisExtension()
            attachment = extension.create_lawful_basis_attachment(
                lawful_basis=lawful_basis,
                expiration=expiration,
                purpose_grants=purpose_grants,
                **kwargs
            )

            # party is required (default 0, add_tag()'s convention); core-05
            # also needs dialog or session, and the basis is scoped to Sessions.
            attachment["party"] = party_index if party_index is not None else 0
            attachment.update(
                self._resolve_attachment_scope(
                    dialog=dialog_index,
                    session=session_index if session_index is not None
                    else self._sessions_for_dialog(dialog_index),
                )
            )

            # Fill in mediatype/start, also required by the schema, unless
            # already set via **kwargs.
            attachment.setdefault("mediatype", "application/json")
            attachment.setdefault("start", self.vcon_dict.get("created_at"))

            self.vcon_dict["attachments"].append(attachment)
            
            # Add extension to extensions list if not already present
            if "lawful_basis" not in self.get_extensions():
                self.add_extension("lawful_basis")
            
            logger.info("Added lawful basis attachment")
            
        except ImportError:
            raise RuntimeError("Lawful basis extension not available")

    def add_wtf_transcription_attachment(
        self,
        transcript: Dict[str, Any],
        segments: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        party_index: Optional[int] = None,
        dialog_index: Optional[int] = None,
        session_index: Optional[Union[int, List[int]]] = None,
        **kwargs
    ) -> None:
        """
        Add a WTF transcription attachment to the vCon.

        Scoped like ``add_lawful_basis_attachment``: ``dialog_index`` and/or
        ``session_index``, else every Session in the vCon.

        Args:
            transcript: Transcript information dictionary
            segments: List of segment dictionaries
            metadata: Metadata dictionary
            party_index: Index of the party this applies to (optional)
            dialog_index: Index of the dialog this applies to (optional)
            session_index: Session index or list of indices (optional)
            **kwargs: Additional WTF parameters

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_wtf_transcription_attachment(
            ...     transcript={"text": "Hello world", "language": "en", "duration": 2.0, "confidence": 0.95},
            ...     segments=[{"id": 0, "start": 0.0, "end": 2.0, "text": "Hello world", "confidence": 0.95}],
            ...     metadata={"created_at": "2025-01-01T00:00:00Z", "processed_at": "2025-01-01T00:00:01Z", 
            ...              "provider": "whisper", "model": "whisper-1"}
            ... )
        """
        if not EXTENSIONS_AVAILABLE:
            raise RuntimeError("Extensions not available")
        
        try:
            from .extensions.wtf import WTFExtension
            extension = WTFExtension()
            attachment = extension.create_wtf_attachment(
                transcript=transcript,
                segments=segments,
                metadata=metadata,
                **kwargs
            )

            attachment["party"] = party_index if party_index is not None else 0
            attachment.update(
                self._resolve_attachment_scope(
                    dialog=dialog_index,
                    session=session_index if session_index is not None
                    else self._sessions_for_dialog(dialog_index),
                )
            )

            # Fill in mediatype/start, also required by the schema, unless
            # already set via **kwargs.
            attachment.setdefault("mediatype", "application/json")
            attachment.setdefault("start", self.vcon_dict.get("created_at"))

            self.vcon_dict["attachments"].append(attachment)
            
            # Add extension to extensions list if not already present
            if "wtf_transcription" not in self.get_extensions():
                self.add_extension("wtf_transcription")
            
            logger.info("Added WTF transcription attachment")

        except ImportError:
            raise RuntimeError("WTF extension not available")

    WTF_SCHEMA_URL = "https://datatracker.ietf.org/doc/html/draft-howe-vcon-wtf-extension"

    def add_wtf_transcription_analysis(
        self,
        transcript: Dict[str, Any],
        segments: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        dialog_index: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Add a WTF transcription as an analysis entry (vs. an attachment).

        Use ``add_wtf_transcription_attachment`` for canonical placement
        (matches the speckit example, attachments[]). Use this method if your
        pipeline treats transcripts as derived analysis output and prefers
        analysis[] placement.

        Emits a spec-shaped analysis entry: ``type="transcription"``,
        ``vendor`` and ``product`` taken from ``metadata["provider"]`` /
        ``metadata["model"]``, ``schema`` set to the WTF draft URL,
        ``encoding="json"``, and ``body`` as a JSON-serialized WTF document.

        Args:
            transcript: Transcript information dictionary
            segments: List of segment dictionaries
            metadata: Metadata dictionary; ``provider`` and ``model`` keys
                map to ``vendor`` and ``product`` on the analysis entry
            dialog_index: Index of the dialog this transcription applies to
            **kwargs: Additional WTF parameters (words, speakers, quality, etc.)
        """
        if not EXTENSIONS_AVAILABLE:
            raise RuntimeError("Extensions not available")

        try:
            from .extensions.wtf import WTFExtension
            extension = WTFExtension()
            wtf_attachment = extension.create_wtf_attachment(
                transcript=transcript,
                segments=segments,
                metadata=metadata,
                **kwargs
            )

            wtf_body = wtf_attachment["body"]
            dialog_ref = [dialog_index] if dialog_index is not None else None

            self.add_analysis(
                type="transcription",
                dialog=dialog_ref,
                vendor=metadata.get("provider", "unknown"),
                product=metadata.get("model"),
                body=json.dumps(wtf_body),
                encoding="json",
                schema=self.WTF_SCHEMA_URL,
            )

            if "wtf_transcription" not in self.get_extensions():
                self.add_extension("wtf_transcription")

            logger.info("Added WTF transcription analysis entry")

        except ImportError:
            raise RuntimeError("WTF extension not available")

    def _sessions_for_dialog(self, dialog_index: Optional[int]) -> Optional[List[int]]:
        """Indices of the Sessions that list ``dialog_index``, or None if there are none."""
        if dialog_index is None:
            return None
        found = [
            n for n, s in enumerate(self.vcon_dict.get("sessions", []))
            if isinstance(s, dict) and dialog_index in (s.get("dialog") or [])
        ]
        return found or None

    def find_lawful_basis_attachments(self, party_index: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find lawful basis attachments in the vCon.

        Args:
            party_index: Filter by party index (optional)

        Returns:
            List of lawful basis attachment dictionaries
        """
        attachments = []
        for attachment in self.vcon_dict.get("attachments", []):
            if attachment.get("purpose") == "lawful_basis":
                if party_index is None or attachment.get("party") == party_index:
                    attachments.append(attachment)
        return attachments

    def find_wtf_attachments(self, party_index: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find WTF transcription attachments in the vCon.

        Args:
            party_index: Filter by party index (optional)

        Returns:
            List of WTF attachment dictionaries
        """
        attachments = []
        for attachment in self.vcon_dict.get("attachments", []):
            if attachment.get("purpose") == "wtf_transcription":
                if party_index is None or attachment.get("party") == party_index:
                    attachments.append(attachment)
        return attachments

    def check_lawful_basis_permission(
        self,
        purpose: str,
        party_index: Optional[int] = None
    ) -> bool:
        """
        Check if permission is granted for a specific purpose.

        Args:
            purpose: The purpose to check permission for
            party_index: Index of the party to check (optional)

        Returns:
            True if permission is granted, False otherwise
        """
        if not EXTENSIONS_AVAILABLE:
            return False
        
        try:
            from .extensions.lawful_basis import LawfulBasisExtension
            extension = LawfulBasisExtension()
            return extension.check_permission(self.vcon_dict, purpose, party_index)
        except ImportError:
            return False

    def validate_extensions(self) -> Dict[str, Any]:
        """
        Validate all extensions in the vCon.

        Returns:
            Dictionary with validation results for each extension
        """
        if not EXTENSIONS_AVAILABLE:
            return {"error": "Extensions not available"}
        
        try:
            registry = get_extension_registry()
            results = {}
            
            # Validate each extension
            for extension_name in self.get_extensions():
                result = registry.validate_extension(extension_name, self.vcon_dict)
                results[extension_name] = {
                    "is_valid": result.is_valid,
                    "errors": result.errors,
                    "warnings": result.warnings
                }
            
            # Validate all attachments
            attachment_results = []
            for attachment in self.vcon_dict.get("attachments", []):
                result = registry.validate_attachment(attachment)
                attachment_results.append({
                    "purpose": attachment.get("purpose"),
                    "is_valid": result.is_valid,
                    "errors": result.errors,
                    "warnings": result.warnings
                })
            
            results["attachments"] = attachment_results
            
            return results
            
        except Exception as e:
            logger.error(f"Error validating extensions: {str(e)}")
            return {"error": str(e)}

    def process_extensions(self) -> Dict[str, Any]:
        """
        Process all extensions in the vCon.

        Returns:
            Dictionary with processing results for each extension
        """
        if not EXTENSIONS_AVAILABLE:
            return {"error": "Extensions not available"}
        
        try:
            registry = get_extension_registry()
            return registry.process_extensions(self.vcon_dict)
        except Exception as e:
            logger.error(f"Error processing extensions: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def decoded_body(entry: Optional[Dict[str, Any]]) -> Any:
        """
        Return the decoded ``body`` of an attachment, analysis, or dialog entry.

        Under ``draft-ietf-vcon-vcon-core-04``, a ``"json"``-encoded body is
        the JSON value itself, not a ``json.dumps`` string. This accepts
        both that shape and the JSON-string bodies written under -02
        conventions (or by this library prior to 0.10.0), so callers don't
        need to special-case legacy vCons.

        Args:
            entry: An attachment, analysis, or dialog dictionary

        Returns:
            The decoded body, or None if there is no body

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_tag("category", "meeting")
            >>> Vcon.decoded_body(vcon.tags)  # ["category:meeting"]
        """
        return decode_body(entry)

    def find_attachment_by_purpose(self, purpose: str) -> Optional[Dict[str, Any]]:
        """
        Find an attachment in the vCon by its purpose.

        This method searches through the vCon's attachments and returns the first
        attachment matching the specified type.

        Args:
            purpose: The purpose of attachment to find

        Returns:
            The matching attachment dictionary if found, None otherwise

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_attachment("metadata", {"version": "1.0"})
            >>> metadata = vcon.find_attachment_by_purpose("metadata")
        """
        logger.debug(f"Searching for attachment of purpose: {purpose}")
        attachment = next(
            (a for a in self.vcon_dict["attachments"] if a["purpose"] == purpose), None
        )
        if attachment:
            logger.debug(f"Found attachment of purpose: {purpose}")
        else:
            logger.debug(f"No attachment found of purpose: {purpose}")
        return attachment

    def add_attachment(
        self,
        purpose: str,
        body: Any = None,
        encoding: str = "none",
        mediatype: Optional[str] = None,
        filename: Optional[str] = None,
        url: Optional[str] = None,
        content_hash: Optional[str] = None,
        start: Optional[str] = None,
        party: Optional[int] = None,
        dialog: Optional[int] = None,
        session: Optional[Union[int, List[int]]] = None,
    ) -> Attachment:
        """
        Add an attachment to the vCon.

        This method creates a new attachment with the specified type, body, and encoding
        and adds it to the vCon's attachments list.

        Core-05 needs ``party`` plus ``dialog`` or ``session``. ``party`` defaults
        to 0. If neither ``dialog`` nor ``session`` is given, the attachment is
        scoped to every Session in the vCon (an empty placeholder Session is added
        if there is none).

        Args:
            purpose: The purpose of the attachment
            body: The content of the attachment
            encoding: The encoding format for the body (default: "none")
            mediatype: Optional media type of the attachment
            filename: Optional file name of the attachment
            url: Optional URL for external attachments
            content_hash: Optional content hash for external attachments
            start: Optional timestamp for the attachment
            party: Optional party index (default 0)
            dialog: Optional dialog index
            session: Optional Session index or list of indices

        Returns:
            The created Attachment object

        Raises:
            ValueError: If the specified encoding is not supported

        Example:
            >>> vcon = Vcon.build_new()
            >>> attachment = vcon.add_attachment("metadata", {"version": "1.0"}, "json")
            >>> print(attachment.purpose)  # Prints "metadata"
        """
        logger.debug(f"Creating new attachment of purpose {purpose} with {encoding} encoding")

        # The WG JSON schema requires start on every attachment; default to
        # this vCon's created_at when the caller doesn't supply one.
        if start is None:
            start = self.vcon_dict.get("created_at")

        if dialog is None and session is None:
            session = self._resolve_attachment_scope()["session"]

        attachment = Attachment(
            purpose=purpose,
            body=body,
            encoding=encoding,
            mediatype=mediatype,
            filename=filename,
            url=url,
            content_hash=content_hash,
            start=start,
            party=party,
            dialog=dialog,
            session=session,
        )
        attachment_dict = attachment.to_dict()
    
        # Process attachment dict according to property handling mode
        processed_attachment = self._process_properties(attachment_dict, _ALLOWED_ATTACHMENT_PROPERTIES)
    
        self.vcon_dict["attachments"].append(processed_attachment)
    
        logger.info(f"Added new attachment of purpose {purpose}")
        return attachment

    def add_image(self, image_path: str, purpose: str = "image") -> Attachment:
        """
        Add an image attachment to the vCon.
        
        This method creates a new attachment with the specified image
        and adds it to the vCon's attachments list.
        
        Args:
            image_path: Path to the image file
            purpose: The purpose of the attachment (default: "image")
            
        Returns:
            The created Attachment object
            
        Raises:
            FileNotFoundError: If the image file cannot be found
            ValueError: If the image format is not supported
            
        Example:
            >>> vcon = Vcon.build_new()
            >>> attachment = vcon.add_image("document.pdf", "identification")
            >>> print(attachment.mediatype)  # Prints "application/pdf"
        """
        attachment = Attachment.from_image(image_path, purpose)
        # The WG JSON schema requires start on every attachment; default to
        # this vCon's created_at (party/dialog already default to 0 in
        # Attachment.__init__).
        if attachment.start is None:
            attachment.start = self.vcon_dict.get("created_at")
        self.vcon_dict["attachments"].append(attachment.to_dict())
        logger.info(f"Added new image attachment of purpose {purpose}")
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
        vendor: str,
        body: Union[Dict[str, Any], List[Any], str],
        dialog: Optional[Union[List[int], int]] = None,
        sessions: Optional[Union[List[int], int]] = None,
        attachment: Optional[Union[List[int], int]] = None,
        analysis: Optional[Union[List[int], int]] = None,
        encoding: str = "none",
        mediatype: Optional[str] = None,
        filename: Optional[str] = None,
        product: Optional[str] = None,
        url: Optional[str] = None,
        content_hash: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        **extra,
    ) -> None:
        """
        Add analysis data to the vCon.

        This method adds analysis data with the specified parameters to the vCon's
        analysis list. Analysis data can be associated with one or more dialog entries
        and includes metadata about the vendor who performed the analysis.

        Args:
            type: The type of analysis
            dialog: Index or list of indices of the associated dialog entries (optional)
            sessions: Index or list of indices of the Sessions analysed (optional)
            attachment: Index or list of indices of the attachments analysed (optional)
            analysis: Index or list of indices of other Analysis Objects used (optional)
            vendor: The name of the vendor who performed the analysis
            body: The analysis data
            encoding: The encoding format of the body (default: "none")
            mediatype: Optional media type of the analysis content
            filename: Optional filename for the analysis content
            product: Optional product name of the vendor
            url: Optional URL for external analysis content
            content_hash: Optional content hash for external analysis content
            schema: Optional schema information about the analysis (default: None)
            meta: Optional metadata about the analysis (default: None)
            **extra: Additional key-value pairs to include in the analysis

        Raises:
            Exception: If the encoding is invalid or if the body format is invalid for the specified encoding

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_analysis(
            ...     type="sentiment",
            ...     dialog=[0],
            ...     vendor="acme",
            ...     body={"score": 0.8},
            ...     encoding="json",
            ...     schema={"version": "1.0"},
            ...     meta={"confidence": "high"}
            ... )
        """
        logger.debug(f"Adding analysis of type {type} from vendor {vendor}")

        if encoding not in ["json", "none", "base64url"]:
            logger.error(f"Invalid encoding: {encoding}")
            raise Exception("Invalid encoding")

        if encoding == "json" and isinstance(body, str):
            try:
                json.loads(body)
            except Exception as e:
                logger.error(f"Invalid JSON body: {str(e)}")
                raise Exception("Invalid JSON body: ", e)

        if encoding == "base64url" and isinstance(body, str):
            try:
                base64.urlsafe_b64decode(body)
            except Exception as e:
                logger.error(f"Invalid base64url body: {str(e)}")
                raise Exception("Invalid base64url body: ", e)

        # Build the analysis object
        analysis_obj: Dict[str, Any] = {"type": type}
        if dialog is not None:
            analysis_obj["dialog"] = dialog
        if sessions is not None:
            analysis_obj["sessions"] = sessions
        if attachment is not None:
            analysis_obj["attachment"] = attachment
        if analysis is not None:
            analysis_obj["analysis"] = analysis
        analysis_obj.update({
            "vendor": vendor,
            "body": body,
            "encoding": encoding,
        })
        analysis = analysis_obj

        if mediatype is not None:
            analysis["mediatype"] = mediatype
        if filename is not None:
            analysis["filename"] = filename
        if product is not None:
            analysis["product"] = product
        if url is not None:
            analysis["url"] = url
        if content_hash is not None:
            analysis["content_hash"] = content_hash
        
        # Add schema if provided
        if schema is not None:
            analysis["schema"] = schema
            
        # Add meta if provided
        if meta is not None:
            analysis["meta"] = meta
            
        # Add any additional parameters
        analysis.update(extra)

        # Process analysis dict according to property handling mode
        processed_analysis = self._process_properties(analysis, _ALLOWED_ANALYSIS_PROPERTIES)

        self.vcon_dict["analysis"].append(processed_analysis)
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
    
        # Process party dict according to property handling mode
        party_dict = party.to_dict()
        processed_party = self._process_properties(party_dict, _ALLOWED_PARTY_PROPERTIES)
    
        self.vcon_dict["parties"].append(processed_party)
        logger.info("Added party")


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
            (dialog for dialog in self.vcon_dict["dialog"] if dialog and _get(dialog, by) == val),
            None,
        )
        if dialog:
            logger.debug(f"Found dialog with {by}={val}")
            return Dialog(**dialog)
        logger.debug(f"No dialog found with {by}={val}")
        return None

    def find_dialogs_by_type(self, type: str) -> List[Dict[str, Any]]:
        """
        Find all dialog entries in the vCon by type.
        This method searches through the dialog list and returns all dialog
        entries matching the specified type.
        Args:
            type: The type of dialogs to find
        Returns:
            A list of matching dialog dictionaries
        Example:
            >>> vcon = Vcon.build_new()
            >>> incomplete = vcon.find_dialogs_by_type("incomplete")
        """
        return [dialog for dialog in self.vcon_dict["dialog"] if dialog.get("type") == type]

    def add_dialog(self, dialog: Dialog, session: Optional[int] = None) -> int:
        """
        Add a dialog entry to the vCon.

        This method adds a Dialog object to the vCon's dialog list. A dialog entry
        represents a segment of the conversation with its associated metadata.
        Use ``Dialog.placeholder()`` to add an empty Dialog Object (``{}``) that
        holds an array position.

        Args:
            dialog: The Dialog object to add
            session: Optional index of an existing Session; the new Dialog's
                index is appended to that Session's ``dialog`` list. Core-05
                requires at least one Session when the vCon has Dialogs, so add
                Sessions with ``add_session()``.

        Returns:
            The index of the new Dialog in the ``dialog`` array.

        Example:
            >>> vcon = Vcon.build_new()
            >>> dialog = Dialog(type="text", start="2023-01-01T00:00:00Z", parties=[0])
            >>> index = vcon.add_dialog(dialog)
        """
        logger.debug(f"Adding dialog: {dialog.to_dict()}")
    
        # Process dialog dict according to property handling mode
        dialog_dict = dialog.to_dict()
        processed_dialog = self._process_properties(dialog_dict, _ALLOWED_DIALOG_PROPERTIES)

        if session is not None:
            sessions = self.vcon_dict.get("sessions", [])
            if not isinstance(session, int) or not 0 <= session < len(sessions):
                raise ValueError(f"Invalid session index: {session}")
    
        self.vcon_dict["dialog"].append(processed_dialog)
        index = len(self.vcon_dict["dialog"]) - 1
        if session is not None:
            self.vcon_dict["sessions"][session].setdefault("dialog", []).append(index)
        logger.info(f"Added dialog of type {getattr(dialog, 'type', 'placeholder')}")
        return index

    def add_session(self, session: Union[Session, Dict[str, Any], None] = None) -> int:
        """
        Add a Session Object and return its index in the ``sessions`` array.

        With no argument an empty placeholder Session (``{}``) is added, which
        core-05 permits.

        Example:
            >>> vcon = Vcon.build_new()
            >>> s = vcon.add_session(Session(start="2023-01-01T00:00:00Z", parties=[0, 1]))
        """
        if session is None:
            session_dict: Dict[str, Any] = {}
        elif isinstance(session, Session):
            session_dict = session.to_dict()
        else:
            session_dict = dict(session)
        processed = self._process_properties(session_dict, _ALLOWED_SESSION_PROPERTIES)
        self.vcon_dict.setdefault("sessions", []).append(processed)
        logger.info("Added session")
        return len(self.vcon_dict["sessions"]) - 1

    def add_event(self, event: Union[Event, Dict[str, Any]]) -> int:
        """
        Add an Event Object and return its index in the ``events`` array.

        An ``Event`` is checked against the per-type parameter table when it is
        built; a plain dict is checked by ``is_valid()``.

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_event(Event(type="join", time="2023-01-01T00:00:00Z", sessions=0, party=0))
        """
        event_dict = event.to_dict() if isinstance(event, Event) else dict(event)
        processed = self._process_properties(event_dict, _ALLOWED_EVENT_PROPERTIES)
        self.vcon_dict.setdefault("events", []).append(processed)
        logger.info(f"Added event of type {processed.get('type')}")
        return len(self.vcon_dict["events"]) - 1

    def add_incomplete_dialog(
        self,
        start: Union[str, datetime],
        disposition: str,
        details: Optional[Dict[str, Any]] = None,
        parties: List[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session: Optional[int] = None,
    ) -> int:
        """
        Add an incomplete dialog entry to the vCon.

        This method creates a dialog entry of type "incomplete" for conversations
        that failed to be set up. Under core-05 an incomplete Dialog has no
        content (no body, mediatype, filename, encoding, url or content_hash), and
        its ``parties`` is the party that attempted the call, the originator.
        ``details`` is kept under ``metadata["details"]``.

        Args:
            start: When the attempt occurred (ISO 8601 string or datetime)
            disposition: Reason for the incomplete conversation (for example "no-answer")
            details: Additional details about the failure (optional)
            parties: The party (or parties) that attempted the conversation (optional)
            metadata: Additional metadata (optional)
            session: Optional Session index to add the Dialog to

        Returns:
            The index of the new Dialog.

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_incomplete_dialog(
            ...     start="2023-01-20T14:00:00Z",
            ...     disposition="no-answer",
            ...     details={"ringDuration": 45000},
            ...     parties=[0]
            ... )
        """
        if parties is None:
            parties = []

        meta = dict(metadata) if metadata else {}
        if details:
            meta["details"] = details

        dialog = Dialog(
            type="incomplete",
            start=start,
            parties=parties,
            disposition=disposition,
            metadata=meta or None,
        )

        return self.add_dialog(dialog, session=session)

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
            >>> print(vcon_dict["vcon"])  # Prints "0.5.0"
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
    def parties(self) -> List[Dict[str, Any]]:
        """
        Get the list of parties in the vCon.

        Returns:
            A list of party dictionaries representing all participants in the conversation.
            These are mutable references to the internal data structure, allowing in-place modifications.

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_party(Party(type="person", name="John Doe"))
            >>> parties = vcon.parties
            >>> print(parties[0]["name"])  # Prints "John Doe"
            >>> parties[0]["name"] = "Jane Doe"  # In-place modification works
            >>> print(vcon.parties[0]["name"])  # Prints "Jane Doe"
        """
        return self.vcon_dict.get("parties", [])

    def get_party_objects(self) -> List[Party]:
        """
        Get the list of parties as Party objects.
        
        This method creates Party objects from the underlying dictionary data.
        Use this when you need Party objects instead of raw dictionaries.
        
        Returns:
            A list of Party objects representing all participants in the conversation
            
        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_party(Party(type="person", name="John Doe"))
            >>> party_objects = vcon.get_party_objects()
            >>> print(party_objects[0].name)  # Prints "John Doe"
        """
        return [Party(**party) for party in self.vcon_dict.get("parties", [])]

    @property
    def dialog(self) -> List[Dict[str, Any]]:
        """
        Get the list of dialog entries in the vCon.

        Returns:
            A list of dialog dictionaries representing the conversation content.
            These are mutable references to the internal data structure, allowing in-place modifications.

        Example:
            >>> vcon = Vcon.build_new()
            >>> vcon.add_dialog(Dialog(type="text", start="2023-01-01T00:00:00Z", parties=[0]))
            >>> dialog = vcon.dialog
            >>> print(dialog[0]["type"])  # Prints "text"
            >>> dialog[0]["body"] = "Modified content"  # In-place modification works
            >>> print(vcon.dialog[0]["body"])  # Prints "Modified content"
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
            >>> print(attachments[0]["purpose"])  # Prints "metadata"
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
    def vcon(self) -> Optional[str]:
        return self.vcon_dict.get("vcon")

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
    def sessions(self) -> List[Dict[str, Any]]:
        """The ``sessions`` array (Session Objects)."""
        return self.vcon_dict.get("sessions", [])

    @property
    def events(self) -> List[Dict[str, Any]]:
        """The ``events`` array (Event Objects)."""
        return self.vcon_dict.get("events", [])

    @property
    def redacted_from(self):
        return self.vcon_dict.get("redacted_from")

    @property
    def amended_from(self):
        return self.vcon_dict.get("amended_from")

    @property
    def redacted_strings(self) -> List[Dict[str, Any]]:
        return self.vcon_dict.get("redacted_strings", [])

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
        _LAST_V8_TIMESTAMP = ns
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

    def sign(self, private_key: Union[rsa.RSAPrivateKey, bytes], alg: str = "RS256") -> None:
        """
        Sign the vCon using JWS (JSON Web Signature).

        This method signs the vCon using the provided private key, adding the signature
        information to the vCon. The signature can later be verified using the
        corresponding public key.

        Args:
            private_key: The RSA private key or its PEM representation
            alg: JWS algorithm (default "RS256", the value core-05 says SHOULD be
                used). "none" is rejected (6.2.2).

        Raises:
            AlgorithmNotPermittedError: If ``alg`` is "none" (any case) or is not
                a permitted algorithm.
            Exception: If there is an error during the signing process

        Example:
            >>> from cryptography.hazmat.primitives.asymmetric import rsa
            >>> private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            >>> vcon = Vcon.build_new()
            >>> vcon.sign(private_key)
        """
        logger.debug("Signing vCon with JWS")
        self._check_jws_alg(alg)
        try:
            payload = self.to_json()
            jws = JsonWebSignature(algorithms=list(PERMITTED_JWS_ALGORITHMS))
            protected = {"alg": alg, "typ": "JWS"}
            
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

    @staticmethod
    def _check_jws_alg(alg: Any) -> None:
        if not isinstance(alg, str) or alg.strip().lower() == "none":
            raise AlgorithmNotPermittedError(
                'JWS alg "none" is not permitted (core-05 section 6.2.2)'
            )
        if alg not in PERMITTED_JWS_ALGORITHMS:
            raise AlgorithmNotPermittedError(
                f"JWS alg {alg!r} is not supported; use one of {PERMITTED_JWS_ALGORITHMS}"
            )

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
            AlgorithmNotPermittedError: If the signature declares ``alg`` "none"
                (in the protected header or the signature's header), which
                core-05 forbids. Verification is refused rather than skipped.

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
        
        # Refuse alg "none" before anything else, from either header location.
        sig0 = self.vcon_dict["signatures"][0]
        declared = []
        try:
            hdr = sig0.get("protected")
            if hdr:
                declared.append(json.loads(base64.urlsafe_b64decode(hdr + "=" * (-len(hdr) % 4))).get("alg"))
        except Exception:
            logger.error("Cannot verify: protected header is not valid base64url JSON")
            return False
        if isinstance(sig0.get("header"), dict) and "alg" in sig0["header"]:
            declared.append(sig0["header"]["alg"])
        for declared_alg in declared:
            if isinstance(declared_alg, str) and declared_alg.strip().lower() == "none":
                logger.error('Refusing to verify: JWS alg "none" is not permitted')
                raise AlgorithmNotPermittedError(
                    'JWS alg "none" is not permitted (core-05 section 6.2.2)'
                )
        if not declared:
            logger.error("Cannot verify: no alg in the JWS protected header or header")
            return False

        try:
            jws = JsonWebSignature(algorithms=list(PERMITTED_JWS_ALGORITHMS))
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
        Validate the vCon against the core-05 rules.

        Checks required fields and types, that ``vcon`` (if present) is "0.5.0",
        that Sessions, Events, Dialogs, attachments and analysis reference
        existing objects, the per-event-type parameter table, that at least one
        Session exists when there are Dialogs or Events, that attachments have
        ``party`` and ``dialog`` or ``session``, that ``redacted_from`` and
        ``amended_from`` are exclusive, that ``extensions`` lists every extension
        in use (and every ``critical`` entry), and that every
        ``__REDACTED_REF_#`` has a ``redacted_strings`` entry.

        SHOULD-level findings are not errors; see :meth:`get_validation_warnings`.

        Returns:
            Tuple[bool, List[str]]: A tuple where the first element is True if the vCon
            is valid and False otherwise, and the second element is a list of error messages.
        """
        logger.debug("Validating vCon")
        errors, _warnings = validate_vcon_dict(self.vcon_dict, Dialog.MIME_TYPES)
        for error in errors:
            logger.error(error)
        if len(errors) == 0:
            logger.info("vCon validation successful.")
        else:
            logger.warning(f"vCon validation failed with {len(errors)} error(s).")
        return len(errors) == 0, errors

    def get_validation_warnings(self) -> List[str]:
        """SHOULD-level findings (for example SHOULD NOT parameters on Events)."""
        _errors, warnings = validate_vcon_dict(self.vcon_dict, Dialog.MIME_TYPES)
        return warnings

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
    def load(
        cls,
        source: str,
        property_handling: str = PROPERTY_HANDLING_DEFAULT,
        migrate_legacy: bool = True,
        strict_migration: bool = False,
    ) -> "Vcon":
        """
        Load a vCon from either a file path or URL.

        Args:
            source: File path or URL to load the vCon from
            property_handling: How to handle non-standard properties. 
                            Options are "default", "strict", or "meta"
                            
        Returns:
            A Vcon object
            
        Raises:
            ValueError: If the source is invalid or cannot be loaded
            requests.RequestException: If there is an error fetching from URL
            json.JSONDecodeError: If the source contains invalid JSON
        """
        if source.startswith(('http://', 'https://')):
            return cls.load_from_url(
                source,
                property_handling=property_handling,
                migrate_legacy=migrate_legacy,
                strict_migration=strict_migration,
            )
        else:
            return cls.load_from_file(
                source,
                property_handling=property_handling,
                migrate_legacy=migrate_legacy,
                strict_migration=strict_migration,
            )

    @classmethod
    def load_from_file(
        cls,
        file_path: str,
        property_handling: str = PROPERTY_HANDLING_DEFAULT,
        migrate_legacy: bool = True,
        strict_migration: bool = False,
    ) -> "Vcon":
        """
        Load a vCon from a file.

        Args:
            file_path: Path to the vCon JSON file
            property_handling: How to handle non-standard properties. 
                            Options are "default", "strict", or "meta"
                            
        Returns:
            A Vcon object
            
        Raises:
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        try:
            with open(file_path, 'r') as f:
                json_str = f.read()
            return cls.build_from_json(
                json_str,
                property_handling=property_handling,
                migrate_legacy=migrate_legacy,
                strict_migration=strict_migration,
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"vCon file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in vCon file: {str(e)}", e.doc, e.pos)

    @classmethod
    def load_from_url(
        cls,
        url: str,
        property_handling: str = PROPERTY_HANDLING_DEFAULT,
        migrate_legacy: bool = True,
        strict_migration: bool = False,
    ) -> "Vcon":
        """
        Load a vCon from a URL.

        Args:
            url: URL to fetch the vCon JSON from
            property_handling: How to handle non-standard properties. 
                            Options are "default", "strict", or "meta"
                            
        Returns:
            A Vcon object
            
        Raises:
            requests.RequestException: If there is an error fetching from URL
            json.JSONDecodeError: If the response contains invalid JSON
        """
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return cls.build_from_json(
            response.text,
            property_handling=property_handling,
            migrate_legacy=migrate_legacy,
            strict_migration=strict_migration,
        )

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
