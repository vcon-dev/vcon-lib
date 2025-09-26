"""
Lawful Basis Extension Implementation

This module provides the main extension class that integrates all lawful basis
functionality with the vCon extension framework.
"""

from typing import Dict, Any
import logging
from ..base import ExtensionInfo, ExtensionType
from .validation import LawfulBasisValidator
from .processing import LawfulBasisProcessor

logger = logging.getLogger(__name__)


class LawfulBasisExtension:
    """Main class for the lawful basis extension."""
    
    def __init__(self):
        self.validator = LawfulBasisValidator()
        self.processor = LawfulBasisProcessor()
    
    def get_extension_info(self) -> ExtensionInfo:
        """Get extension information."""
        return ExtensionInfo(
            name="lawful_basis",
            extension_type=ExtensionType.COMPATIBLE,
            version="1.0",
            description="Lawful basis management for conversation participants with cryptographic proof mechanisms and regulatory compliance support",
            attachment_types=["lawful_basis"],
            validator=self.validator,
            processor=self.processor
        )
    
    def create_lawful_basis_attachment(
        self,
        lawful_basis: str,
        expiration: str,
        purpose_grants: list,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a lawful basis attachment dictionary."""
        from .attachment import LawfulBasisAttachment, LawfulBasisType, PurposeGrant
        
        # Convert string to enum
        try:
            basis_type = LawfulBasisType(lawful_basis)
        except ValueError:
            raise ValueError(f"Invalid lawful basis type: {lawful_basis}")
        
        # Convert purpose grants
        grants = []
        for grant_data in purpose_grants:
            if isinstance(grant_data, dict):
                grants.append(PurposeGrant.from_dict(grant_data))
            else:
                raise ValueError("Purpose grants must be dictionaries")
        
        # Create attachment object
        attachment = LawfulBasisAttachment(
            lawful_basis=basis_type,
            expiration=expiration,
            purpose_grants=grants,
            **kwargs
        )
        
        # Return as attachment dictionary
        return {
            "type": "lawful_basis",
            "encoding": "json",
            "body": attachment.to_dict()
        }
    
    def validate_lawful_basis_attachment(self, attachment: Dict[str, Any]) -> bool:
        """Validate a lawful basis attachment."""
        result = self.validator.validate_attachment(attachment)
        return result.is_valid
    
    def check_permission(
        self,
        vcon_dict: Dict[str, Any],
        purpose: str,
        party_index: int = None
    ) -> bool:
        """Check if permission is granted for a specific purpose."""
        result = self.processor.check_permission(vcon_dict, purpose, party_index)
        return result.success and result.data.get("permission", False)
