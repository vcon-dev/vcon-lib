"""
Base classes for vCon extensions.

This module provides the foundational classes and interfaces for implementing
vCon extensions according to the IETF draft specifications.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExtensionType(Enum):
    """Types of vCon extensions."""
    COMPATIBLE = "compatible"      # Safe to ignore, no breaking changes
    INCOMPATIBLE = "incompatible"  # Must be supported, breaking changes
    EXPERIMENTAL = "experimental"  # Development/testing only


class ValidationResult:
    """Result of extension validation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a validation warning."""
        self.warnings.append(warning)
    
    def __bool__(self):
        return self.is_valid


class ProcessingResult:
    """Result of extension processing."""
    
    def __init__(self, success: bool, data: Dict[str, Any] = None, errors: List[str] = None):
        self.success = success
        self.data = data or {}
        self.errors = errors or []
    
    def add_error(self, error: str):
        """Add a processing error."""
        self.errors.append(error)
        self.success = False


class ExtensionValidator(ABC):
    """Base class for extension validators."""
    
    @abstractmethod
    def validate_attachment(self, attachment: Dict[str, Any]) -> ValidationResult:
        """Validate an extension attachment."""
        pass
    
    @abstractmethod
    def validate_extension_usage(self, vcon_dict: Dict[str, Any]) -> ValidationResult:
        """Validate extension usage in a vCon."""
        pass


class ExtensionProcessor(ABC):
    """Base class for extension processors."""
    
    @abstractmethod
    def process(self, vcon_dict: Dict[str, Any]) -> ProcessingResult:
        """Process extension data in a vCon."""
        pass
    
    @abstractmethod
    def can_process(self, extension_name: str) -> bool:
        """Check if this processor can handle the given extension."""
        pass


class ExtensionInfo:
    """Information about a vCon extension."""
    
    def __init__(
        self,
        name: str,
        extension_type: ExtensionType,
        version: str,
        description: str,
        attachment_types: List[str] = None,
        validator: Optional[ExtensionValidator] = None,
        processor: Optional[ExtensionProcessor] = None
    ):
        self.name = name
        self.type = extension_type
        self.version = version
        self.description = description
        self.attachment_types = attachment_types or []
        self.validator = validator
        self.processor = processor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type.value,
            "version": self.version,
            "description": self.description,
            "attachment_types": self.attachment_types
        }


class ExtensionAttachment:
    """Base class for extension attachments."""
    
    def __init__(
        self,
        attachment_type: str,
        body: Dict[str, Any],
        start: Optional[Union[str, datetime]] = None,
        party: Optional[int] = None,
        dialog: Optional[int] = None,
        encoding: str = "json",
        meta: Optional[Dict[str, Any]] = None
    ):
        self.type = attachment_type
        self.body = body
        self.start = self._normalize_timestamp(start) if start else None
        self.party = party
        self.dialog = dialog
        self.encoding = encoding
        self.meta = meta or {}
    
    def _normalize_timestamp(self, timestamp: Union[str, datetime]) -> str:
        """Normalize timestamp to ISO 8601 string."""
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        return timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "type": self.type,
            "body": self.body,
            "encoding": self.encoding
        }
        
        if self.start:
            result["start"] = self.start
        if self.party is not None:
            result["party"] = self.party
        if self.dialog is not None:
            result["dialog"] = self.dialog
        if self.meta:
            result["meta"] = self.meta
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtensionAttachment':
        """Create from dictionary representation."""
        return cls(
            attachment_type=data["type"],
            body=data["body"],
            start=data.get("start"),
            party=data.get("party"),
            dialog=data.get("dialog"),
            encoding=data.get("encoding", "json"),
            meta=data.get("meta")
        )
