"""
Lawful Basis Attachment Classes

This module implements the core data structures for lawful basis attachments
as defined in the draft specification.
"""

from enum import Enum
from typing import List, Dict, Optional, Union, Any
from datetime import datetime, timezone
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class LawfulBasisType(Enum):
    """Types of lawful bases for processing personal data."""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class ProofType(Enum):
    """Types of proof mechanisms for lawful basis."""
    VERBAL_CONFIRMATION = "verbal_confirmation"
    SIGNED_DOCUMENT = "signed_document"
    CRYPTOGRAPHIC_SIGNATURE = "cryptographic_signature"
    EXTERNAL_SYSTEM = "external_system"


class HashAlgorithm(Enum):
    """Supported hash algorithms for content integrity."""
    SHA_256 = "sha-256"
    SHA_3_256 = "sha-3-256"
    BLAKE2B_256 = "blake2b-256"


class CanonicalizationMethod(Enum):
    """Supported canonicalization methods."""
    JCS = "jcs"  # JSON Canonicalization Scheme


class PurposeGrant:
    """Represents a purpose-specific permission grant."""
    
    def __init__(
        self,
        purpose: str,
        granted: bool,
        granted_at: Union[str, datetime],
        conditions: Optional[List[str]] = None
    ):
        self.purpose = purpose
        self.granted = granted
        self.granted_at = self._normalize_timestamp(granted_at)
        self.conditions = conditions or []
    
    def _normalize_timestamp(self, timestamp: Union[str, datetime]) -> datetime:
        """Normalize timestamp to datetime object."""
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return timestamp
    
    def is_expired(self, status_interval: Optional[str] = None) -> bool:
        """Check if the grant has expired based on status interval."""
        if not status_interval:
            return False
        
        # Parse status interval (e.g., "30d", "1y")
        # This is a simplified implementation
        # In practice, you'd want more robust interval parsing
        try:
            if status_interval.endswith('d'):
                days = int(status_interval[:-1])
                expiry = self.granted_at + datetime.timedelta(days=days)
                return datetime.now(timezone.utc) > expiry
            elif status_interval.endswith('y'):
                years = int(status_interval[:-1])
                expiry = self.granted_at.replace(year=self.granted_at.year + years)
                return datetime.now(timezone.utc) > expiry
        except (ValueError, AttributeError):
            logger.warning(f"Invalid status interval format: {status_interval}")
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "purpose": self.purpose,
            "granted": self.granted,
            "granted_at": self.granted_at.isoformat()
        }
        
        if self.conditions:
            result["conditions"] = self.conditions
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PurposeGrant':
        """Create from dictionary representation."""
        return cls(
            purpose=data["purpose"],
            granted=data["granted"],
            granted_at=data["granted_at"],
            conditions=data.get("conditions")
        )


class ContentHash:
    """Represents content integrity information."""
    
    def __init__(
        self,
        algorithm: HashAlgorithm,
        canonicalization: CanonicalizationMethod,
        value: str
    ):
        self.algorithm = algorithm
        self.canonicalization = canonicalization
        self.value = value
    
    def validate(self, content: Dict[str, Any]) -> bool:
        """Validate content against the hash."""
        try:
            canonical_content = self._canonicalize(content)
            computed_hash = self._compute_hash(canonical_content)
            return computed_hash == self.value
        except Exception as e:
            logger.error(f"Content hash validation failed: {str(e)}")
            return False
    
    def _canonicalize(self, content: Dict[str, Any]) -> str:
        """Apply canonicalization method."""
        if self.canonicalization == CanonicalizationMethod.JCS:
            # Implement JSON Canonicalization Scheme (RFC 8785)
            # This is a simplified implementation
            return json.dumps(content, sort_keys=True, separators=(',', ':'))
        else:
            raise ValueError(f"Unsupported canonicalization: {self.canonicalization}")
    
    def _compute_hash(self, content: str) -> str:
        """Compute hash using specified algorithm."""
        content_bytes = content.encode('utf-8')
        
        if self.algorithm == HashAlgorithm.SHA_256:
            return hashlib.sha256(content_bytes).hexdigest()
        elif self.algorithm == HashAlgorithm.SHA_3_256:
            return hashlib.sha3_256(content_bytes).hexdigest()
        elif self.algorithm == HashAlgorithm.BLAKE2B_256:
            return hashlib.blake2b(content_bytes, digest_size=32).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {self.algorithm}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "algorithm": self.algorithm.value,
            "canonicalization": self.canonicalization.value,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentHash':
        """Create from dictionary representation."""
        return cls(
            algorithm=HashAlgorithm(data["algorithm"]),
            canonicalization=CanonicalizationMethod(data["canonicalization"]),
            value=data["value"]
        )


class ProofMechanism:
    """Represents a proof mechanism for lawful basis."""
    
    def __init__(
        self,
        proof_type: ProofType,
        timestamp: Union[str, datetime],
        proof_data: Dict[str, Any]
    ):
        self.proof_type = proof_type
        self.timestamp = self._normalize_timestamp(timestamp)
        self.proof_data = proof_data
    
    def _normalize_timestamp(self, timestamp: Union[str, datetime]) -> datetime:
        """Normalize timestamp to datetime object."""
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "proof_type": self.proof_type.value,
            "timestamp": self.timestamp.isoformat(),
            "proof_data": self.proof_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProofMechanism':
        """Create from dictionary representation."""
        return cls(
            proof_type=ProofType(data["proof_type"]),
            timestamp=data["timestamp"],
            proof_data=data["proof_data"]
        )


class RegistryInfo:
    """Represents external attestation registry information."""
    
    def __init__(self, registry_type: str, url: str):
        self.registry_type = registry_type
        self.url = url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.registry_type,
            "url": self.url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegistryInfo':
        """Create from dictionary representation."""
        return cls(
            registry_type=data["type"],
            url=data["url"]
        )


class LawfulBasisAttachment:
    """
    Represents a lawful basis attachment for vCon processing.
    
    This class handles the creation, validation, and processing of lawful
    basis attachments according to the draft specification.
    """
    
    def __init__(
        self,
        lawful_basis: LawfulBasisType,
        expiration: Optional[Union[str, datetime]],
        purpose_grants: List[PurposeGrant],
        terms_of_service: Optional[str] = None,
        status_interval: Optional[str] = None,
        content_hash: Optional[ContentHash] = None,
        registry: Optional[RegistryInfo] = None,
        proof_mechanisms: Optional[List[ProofMechanism]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.lawful_basis = lawful_basis
        self.expiration = self._normalize_timestamp(expiration) if expiration else None
        self.purpose_grants = purpose_grants
        self.terms_of_service = terms_of_service
        self.status_interval = status_interval
        self.content_hash = content_hash
        self.registry = registry
        self.proof_mechanisms = proof_mechanisms or []
        self.metadata = metadata or {}
    
    def _normalize_timestamp(self, timestamp: Union[str, datetime]) -> datetime:
        """Normalize timestamp to datetime object."""
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return timestamp
    
    def is_valid(self) -> bool:
        """Check if the lawful basis is currently valid."""
        if self.expiration is None:
            return True
        
        now = datetime.now(timezone.utc)
        return now < self.expiration
    
    def has_permission(self, purpose: str) -> bool:
        """Check if permission is granted for a specific purpose."""
        for grant in self.purpose_grants:
            if grant.purpose == purpose:
                return grant.granted
        return False
    
    def get_conditions(self, purpose: str) -> List[str]:
        """Get conditions for a specific purpose grant."""
        for grant in self.purpose_grants:
            if grant.purpose == purpose:
                return grant.conditions or []
        return []
    
    def validate_content_hash(self) -> bool:
        """Validate the content hash if present."""
        if not self.content_hash:
            return True
        
        return self.content_hash.validate(self.to_dict())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "lawful_basis": self.lawful_basis.value,
            "expiration": self.expiration.isoformat() if self.expiration else None,
            "purpose_grants": [grant.to_dict() for grant in self.purpose_grants]
        }
        
        if self.terms_of_service:
            result["terms_of_service"] = self.terms_of_service
        if self.status_interval:
            result["status_interval"] = self.status_interval
        if self.content_hash:
            result["content_hash"] = self.content_hash.to_dict()
        if self.registry:
            result["registry"] = self.registry.to_dict()
        if self.proof_mechanisms:
            result["proof_mechanisms"] = [proof.to_dict() for proof in self.proof_mechanisms]
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LawfulBasisAttachment':
        """Create from dictionary representation."""
        return cls(
            lawful_basis=LawfulBasisType(data["lawful_basis"]),
            expiration=data.get("expiration"),
            purpose_grants=[PurposeGrant.from_dict(g) for g in data["purpose_grants"]],
            terms_of_service=data.get("terms_of_service"),
            status_interval=data.get("status_interval"),
            content_hash=ContentHash.from_dict(data["content_hash"]) if data.get("content_hash") else None,
            registry=RegistryInfo.from_dict(data["registry"]) if data.get("registry") else None,
            proof_mechanisms=[ProofMechanism.from_dict(p) for p in data.get("proof_mechanisms", [])],
            metadata=data.get("metadata")
        )
