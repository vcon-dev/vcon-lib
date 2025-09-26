"""
Validation for Lawful Basis Extension

This module implements validation logic for lawful basis attachments
and extension usage according to the draft specification.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone
from ..base import ExtensionValidator, ValidationResult
from .attachment import (
    LawfulBasisAttachment,
    LawfulBasisType,
    ProofType,
    HashAlgorithm,
    CanonicalizationMethod
)

logger = logging.getLogger(__name__)


class LawfulBasisValidationError(Exception):
    """Base exception for lawful basis validation errors."""
    pass


class LawfulBasisExpiredError(LawfulBasisValidationError):
    """Raised when lawful basis has expired."""
    pass


class PermissionDeniedError(LawfulBasisValidationError):
    """Raised when permission is explicitly denied."""
    pass


class LawfulBasisMissingError(LawfulBasisValidationError):
    """Raised when no valid lawful basis is found."""
    pass


class ProofVerificationError(LawfulBasisValidationError):
    """Raised when proof mechanisms fail validation."""
    pass


class ContentHashMismatchError(LawfulBasisValidationError):
    """Raised when content hash validation fails."""
    pass


class LawfulBasisValidator(ExtensionValidator):
    """Validator for lawful basis extension."""
    
    def __init__(self):
        self.supported_lawful_bases = {basis.value for basis in LawfulBasisType}
        self.supported_proof_types = {proof.value for proof in ProofType}
        self.supported_hash_algorithms = {alg.value for alg in HashAlgorithm}
        self.supported_canonicalization = {canon.value for canon in CanonicalizationMethod}
    
    def validate_attachment(self, attachment: Dict[str, Any]) -> ValidationResult:
        """Validate a lawful basis attachment."""
        result = ValidationResult(True)
        
        # Check attachment type
        if attachment.get("type") != "lawful_basis":
            result.add_error("Invalid attachment type for lawful basis extension")
            return result
        
        # Check encoding
        if attachment.get("encoding") != "json":
            result.add_error("Lawful basis attachment must use 'json' encoding")
        
        # Validate body structure
        body = attachment.get("body")
        if not isinstance(body, dict):
            result.add_error("Lawful basis attachment body must be a dictionary")
            return result
        
        # Validate required fields
        body_result = self._validate_lawful_basis_body(body)
        if not body_result.is_valid:
            result.errors.extend(body_result.errors)
            result.warnings.extend(body_result.warnings)
            result.is_valid = False
        
        return result
    
    def validate_extension_usage(self, vcon_dict: Dict[str, Any]) -> ValidationResult:
        """Validate lawful basis extension usage in a vCon."""
        result = ValidationResult(True)
        
        # Check if extension is declared
        extensions = vcon_dict.get("extensions", [])
        if "lawful_basis" not in extensions:
            result.add_warning("Lawful basis extension not declared in extensions array")
        
        # Validate all lawful basis attachments
        attachments = vcon_dict.get("attachments", [])
        lawful_basis_attachments = [
            att for att in attachments 
            if att.get("type") == "lawful_basis"
        ]
        
        for i, attachment in enumerate(lawful_basis_attachments):
            att_result = self.validate_attachment(attachment)
            if not att_result.is_valid:
                result.add_error(f"Lawful basis attachment {i}: {', '.join(att_result.errors)}")
                result.is_valid = False
            result.warnings.extend([f"Attachment {i}: {w}" for w in att_result.warnings])
        
        return result
    
    def _validate_lawful_basis_body(self, body: Dict[str, Any]) -> ValidationResult:
        """Validate the body of a lawful basis attachment."""
        result = ValidationResult(True)
        
        # Validate required fields
        required_fields = ["lawful_basis", "expiration", "purpose_grants"]
        for field in required_fields:
            if field not in body:
                result.add_error(f"Missing required field: {field}")
        
        # Validate lawful_basis
        if "lawful_basis" in body:
            lawful_basis = body["lawful_basis"]
            if lawful_basis not in self.supported_lawful_bases:
                result.add_error(f"Unsupported lawful basis: {lawful_basis}")
        
        # Validate expiration
        if "expiration" in body:
            expiration = body["expiration"]
            if expiration is not None:
                try:
                    exp_dt = datetime.fromisoformat(expiration.replace('Z', '+00:00'))
                    if exp_dt <= datetime.now(timezone.utc):
                        result.add_warning("Lawful basis has expired")
                except ValueError:
                    result.add_error("Invalid expiration timestamp format")
        
        # Validate purpose_grants
        if "purpose_grants" in body:
            purpose_grants = body["purpose_grants"]
            if not isinstance(purpose_grants, list):
                result.add_error("purpose_grants must be a list")
            else:
                for i, grant in enumerate(purpose_grants):
                    grant_result = self._validate_purpose_grant(grant)
                    if not grant_result.is_valid:
                        result.add_error(f"Purpose grant {i}: {', '.join(grant_result.errors)}")
                        result.is_valid = False
                    result.warnings.extend([f"Grant {i}: {w}" for w in grant_result.warnings])
        
        # Validate optional fields
        if "content_hash" in body:
            hash_result = self._validate_content_hash(body["content_hash"])
            if not hash_result.is_valid:
                result.add_error(f"Content hash validation failed: {', '.join(hash_result.errors)}")
                result.is_valid = False
        
        if "proof_mechanisms" in body:
            proof_mechanisms = body["proof_mechanisms"]
            if not isinstance(proof_mechanisms, list):
                result.add_error("proof_mechanisms must be a list")
            else:
                for i, proof in enumerate(proof_mechanisms):
                    proof_result = self._validate_proof_mechanism(proof)
                    if not proof_result.is_valid:
                        result.add_error(f"Proof mechanism {i}: {', '.join(proof_result.errors)}")
                        result.is_valid = False
        
        if "registry" in body:
            registry_result = self._validate_registry_info(body["registry"])
            if not registry_result.is_valid:
                result.add_error(f"Registry validation failed: {', '.join(registry_result.errors)}")
                result.is_valid = False
        
        return result
    
    def _validate_purpose_grant(self, grant: Dict[str, Any]) -> ValidationResult:
        """Validate a purpose grant."""
        result = ValidationResult(True)
        
        required_fields = ["purpose", "granted", "granted_at"]
        for field in required_fields:
            if field not in grant:
                result.add_error(f"Missing required field in purpose grant: {field}")
        
        # Validate granted field
        if "granted" in grant and not isinstance(grant["granted"], bool):
            result.add_error("granted field must be a boolean")
        
        # Validate granted_at timestamp
        if "granted_at" in grant:
            try:
                datetime.fromisoformat(grant["granted_at"].replace('Z', '+00:00'))
            except ValueError:
                result.add_error("Invalid granted_at timestamp format")
        
        # Validate conditions
        if "conditions" in grant:
            conditions = grant["conditions"]
            if not isinstance(conditions, list):
                result.add_error("conditions must be a list")
            elif not all(isinstance(c, str) for c in conditions):
                result.add_error("All conditions must be strings")
        
        return result
    
    def _validate_content_hash(self, content_hash: Dict[str, Any]) -> ValidationResult:
        """Validate content hash information."""
        result = ValidationResult(True)
        
        required_fields = ["algorithm", "canonicalization", "value"]
        for field in required_fields:
            if field not in content_hash:
                result.add_error(f"Missing required field in content_hash: {field}")
        
        # Validate algorithm
        if "algorithm" in content_hash:
            algorithm = content_hash["algorithm"]
            if algorithm not in self.supported_hash_algorithms:
                result.add_error(f"Unsupported hash algorithm: {algorithm}")
        
        # Validate canonicalization
        if "canonicalization" in content_hash:
            canonicalization = content_hash["canonicalization"]
            if canonicalization not in self.supported_canonicalization:
                result.add_error(f"Unsupported canonicalization method: {canonicalization}")
        
        # Validate hash value format
        if "value" in content_hash:
            value = content_hash["value"]
            if not isinstance(value, str) or not all(c in '0123456789abcdefABCDEF' for c in value):
                result.add_error("Hash value must be a hexadecimal string")
        
        return result
    
    def _validate_proof_mechanism(self, proof: Dict[str, Any]) -> ValidationResult:
        """Validate a proof mechanism."""
        result = ValidationResult(True)
        
        required_fields = ["proof_type", "timestamp", "proof_data"]
        for field in required_fields:
            if field not in proof:
                result.add_error(f"Missing required field in proof mechanism: {field}")
        
        # Validate proof_type
        if "proof_type" in proof:
            proof_type = proof["proof_type"]
            if proof_type not in self.supported_proof_types:
                result.add_error(f"Unsupported proof type: {proof_type}")
        
        # Validate timestamp
        if "timestamp" in proof:
            try:
                datetime.fromisoformat(proof["timestamp"].replace('Z', '+00:00'))
            except ValueError:
                result.add_error("Invalid timestamp format in proof mechanism")
        
        # Validate proof_data
        if "proof_data" in proof:
            if not isinstance(proof["proof_data"], dict):
                result.add_error("proof_data must be a dictionary")
        
        return result
    
    def _validate_registry_info(self, registry: Dict[str, Any]) -> ValidationResult:
        """Validate registry information."""
        result = ValidationResult(True)
        
        required_fields = ["type", "url"]
        for field in required_fields:
            if field not in registry:
                result.add_error(f"Missing required field in registry: {field}")
        
        # Validate registry type
        if "type" in registry:
            registry_type = registry["type"]
            if registry_type not in ["scitt"]:  # Add more types as they're defined
                result.add_warning(f"Unknown registry type: {registry_type}")
        
        # Validate URL format (basic validation)
        if "url" in registry:
            url = registry["url"]
            if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                result.add_error("Registry URL must be a valid HTTP/HTTPS URL")
        
        return result
    
    def validate_lawful_basis_attachment(self, attachment: LawfulBasisAttachment) -> ValidationResult:
        """Validate a LawfulBasisAttachment object."""
        result = ValidationResult(True)
        
        # Check if expired
        if not attachment.is_valid():
            result.add_error("Lawful basis has expired")
        
        # Validate content hash if present
        if attachment.content_hash and not attachment.validate_content_hash():
            result.add_error("Content hash validation failed")
        
        # Validate purpose grants
        if not attachment.purpose_grants:
            result.add_error("At least one purpose grant is required")
        
        # Check for expired grants
        for grant in attachment.purpose_grants:
            if grant.is_expired(attachment.status_interval):
                result.add_warning(f"Purpose grant for '{grant.purpose}' has expired")
        
        return result
