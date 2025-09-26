"""
Registry Integration for Lawful Basis Extension

This module implements integration with external attestation registries,
particularly SCITT (Supply Chain Integrity, Transparency, and Trust) services.
"""

from typing import Dict, List, Any, Optional
import logging
import requests
from datetime import datetime, timezone
from ..base import ValidationResult
from .attachment import LawfulBasisAttachment, RegistryInfo

logger = logging.getLogger(__name__)


class RegistryClient:
    """Base class for registry clients."""
    
    def __init__(self, registry_url: str, auth_token: Optional[str] = None):
        self.registry_url = registry_url
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({"Authorization": f"Bearer {auth_token}"})
    
    def submit_attestation(self, lawful_basis: LawfulBasisAttachment) -> str:
        """Submit a lawful basis attestation to the registry."""
        raise NotImplementedError
    
    def verify_receipt(self, receipt_id: str) -> ValidationResult:
        """Verify a registry receipt."""
        raise NotImplementedError
    
    def query_status(self, attestation_id: str) -> Dict[str, Any]:
        """Query the status of an attestation."""
        raise NotImplementedError


class SCITTRegistryClient(RegistryClient):
    """Client for SCITT (Supply Chain Integrity, Transparency, and Trust) registries."""
    
    def __init__(self, registry_url: str, auth_token: Optional[str] = None):
        super().__init__(registry_url, auth_token)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def submit_attestation(self, lawful_basis: LawfulBasisAttachment) -> str:
        """Submit a lawful basis attestation to the SCITT registry."""
        try:
            # Prepare attestation data
            attestation_data = {
                "type": "lawful_basis",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": lawful_basis.to_dict()
            }
            
            # Submit to registry
            response = self.session.post(
                f"{self.registry_url}/attestations",
                json=attestation_data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            receipt_id = result.get("receipt_id")
            
            if not receipt_id:
                raise ValueError("No receipt_id in registry response")
            
            logger.info(f"Successfully submitted attestation, receipt_id: {receipt_id}")
            return receipt_id
            
        except requests.RequestException as e:
            logger.error(f"Error submitting attestation to SCITT registry: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error submitting attestation: {str(e)}")
            raise
    
    def verify_receipt(self, receipt_id: str) -> ValidationResult:
        """Verify a SCITT registry receipt."""
        try:
            response = self.session.get(
                f"{self.registry_url}/receipts/{receipt_id}",
                timeout=30
            )
            response.raise_for_status()
            
            receipt_data = response.json()
            
            # Validate receipt structure
            required_fields = ["receipt_id", "timestamp", "status"]
            for field in required_fields:
                if field not in receipt_data:
                    return ValidationResult(
                        False,
                        [f"Missing required field in receipt: {field}"]
                    )
            
            # Check receipt status
            status = receipt_data.get("status")
            if status != "verified":
                return ValidationResult(
                    False,
                    [f"Receipt not verified, status: {status}"]
                )
            
            logger.info(f"Successfully verified receipt: {receipt_id}")
            return ValidationResult(True)
            
        except requests.RequestException as e:
            logger.error(f"Error verifying receipt {receipt_id}: {str(e)}")
            return ValidationResult(
                False,
                [f"Registry verification error: {str(e)}"]
            )
        except Exception as e:
            logger.error(f"Unexpected error verifying receipt: {str(e)}")
            return ValidationResult(
                False,
                [f"Verification error: {str(e)}"]
            )
    
    def query_status(self, attestation_id: str) -> Dict[str, Any]:
        """Query the status of an attestation in the SCITT registry."""
        try:
            response = self.session.get(
                f"{self.registry_url}/attestations/{attestation_id}",
                timeout=30
            )
            response.raise_for_status()
            
            status_data = response.json()
            logger.info(f"Retrieved status for attestation {attestation_id}")
            return status_data
            
        except requests.RequestException as e:
            logger.error(f"Error querying attestation status {attestation_id}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error querying status: {str(e)}")
            return {"error": str(e)}
    
    def update_attestation(self, attestation_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing attestation."""
        try:
            response = self.session.patch(
                f"{self.registry_url}/attestations/{attestation_id}",
                json=updates,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Successfully updated attestation {attestation_id}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Error updating attestation {attestation_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating attestation: {str(e)}")
            return False


class RegistryManager:
    """Manages multiple registry clients."""
    
    def __init__(self):
        self.clients: Dict[str, RegistryClient] = {}
    
    def register_client(self, registry_type: str, client: RegistryClient):
        """Register a registry client."""
        self.clients[registry_type] = client
        logger.info(f"Registered {registry_type} registry client")
    
    def submit_to_registry(
        self,
        lawful_basis: LawfulBasisAttachment,
        registry_type: str
    ) -> str:
        """Submit lawful basis to a specific registry."""
        client = self.clients.get(registry_type)
        if not client:
            raise ValueError(f"No client registered for registry type: {registry_type}")
        
        return client.submit_attestation(lawful_basis)
    
    def verify_registry_status(
        self,
        attestation_id: str,
        registry_type: str
    ) -> ValidationResult:
        """Verify attestation status in a specific registry."""
        client = self.clients.get(registry_type)
        if not client:
            return ValidationResult(
                False,
                [f"No client registered for registry type: {registry_type}"]
            )
        
        return client.verify_receipt(attestation_id)
    
    def query_registry_status(
        self,
        attestation_id: str,
        registry_type: str
    ) -> Dict[str, Any]:
        """Query attestation status in a specific registry."""
        client = self.clients.get(registry_type)
        if not client:
            return {"error": f"No client registered for registry type: {registry_type}"}
        
        return client.query_status(attestation_id)


class RegistryValidator:
    """Validates registry responses and data."""
    
    @staticmethod
    def validate_scitt_receipt(receipt: Dict[str, Any]) -> ValidationResult:
        """Validate a SCITT receipt structure."""
        result = ValidationResult(True)
        
        required_fields = ["receipt_id", "timestamp", "status"]
        for field in required_fields:
            if field not in receipt:
                result.add_error(f"Missing required field in SCITT receipt: {field}")
        
        # Validate timestamp format
        if "timestamp" in receipt:
            try:
                datetime.fromisoformat(receipt["timestamp"].replace('Z', '+00:00'))
            except ValueError:
                result.add_error("Invalid timestamp format in SCITT receipt")
        
        # Validate status
        if "status" in receipt:
            valid_statuses = ["pending", "verified", "rejected", "expired"]
            if receipt["status"] not in valid_statuses:
                result.add_warning(f"Unknown status in SCITT receipt: {receipt['status']}")
        
        return result
    
    @staticmethod
    def validate_attestation_status(status: Dict[str, Any]) -> ValidationResult:
        """Validate attestation status data."""
        result = ValidationResult(True)
        
        # Check for error field
        if "error" in status:
            result.add_error(f"Registry error: {status['error']}")
            return result
        
        # Validate basic structure
        if "attestation_id" not in status:
            result.add_error("Missing attestation_id in status response")
        
        if "status" not in status:
            result.add_error("Missing status in status response")
        
        return result
    
    @staticmethod
    def validate_registry_metadata(metadata: Dict[str, Any]) -> ValidationResult:
        """Validate registry metadata."""
        result = ValidationResult(True)
        
        # Check for required metadata fields
        if "registry_type" not in metadata:
            result.add_warning("Missing registry_type in metadata")
        
        if "version" not in metadata:
            result.add_warning("Missing version in metadata")
        
        return result
