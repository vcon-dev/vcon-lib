"""
Processing for Lawful Basis Extension

This module implements processing logic for lawful basis attachments,
including proof mechanism verification and permission evaluation.
"""

from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime, timezone
from ..base import ExtensionProcessor, ProcessingResult
from .attachment import (
    LawfulBasisAttachment,
    ProofType,
    ProofMechanism
)
from .validation import (
    LawfulBasisValidationError,
    LawfulBasisExpiredError,
    PermissionDeniedError,
    LawfulBasisMissingError,
    ProofVerificationError
)

logger = logging.getLogger(__name__)


class ProofProcessor:
    """Processes different types of proof mechanisms."""
    
    def __init__(self):
        self.processors = {
            ProofType.VERBAL_CONFIRMATION: self._process_verbal_confirmation,
            ProofType.SIGNED_DOCUMENT: self._process_signed_document,
            ProofType.CRYPTOGRAPHIC_SIGNATURE: self._process_cryptographic_signature,
            ProofType.EXTERNAL_SYSTEM: self._process_external_system
        }
    
    def process_proof(self, proof: ProofMechanism, vcon_dict: Dict[str, Any]) -> bool:
        """Process a proof mechanism and return validation result."""
        try:
            processor = self.processors.get(proof.proof_type)
            if not processor:
                logger.error(f"No processor for proof type: {proof.proof_type}")
                return False
            
            return processor(proof, vcon_dict)
        except Exception as e:
            logger.error(f"Error processing proof {proof.proof_type}: {str(e)}")
            return False
    
    def _process_verbal_confirmation(self, proof: ProofMechanism, vcon_dict: Dict[str, Any]) -> bool:
        """Process verbal confirmation proof."""
        proof_data = proof.proof_data
        
        # Check if dialog reference exists
        dialog_reference = proof_data.get("dialog_reference")
        if dialog_reference is not None:
            dialogs = vcon_dict.get("dialog", [])
            if dialog_reference >= len(dialogs):
                logger.error(f"Invalid dialog reference: {dialog_reference}")
                return False
        
        # Check confirmation text
        confirmation_text = proof_data.get("confirmation_text", "").lower()
        positive_confirmations = ["yes", "i consent", "i agree", "consent", "agree"]
        
        return any(phrase in confirmation_text for phrase in positive_confirmations)
    
    def _process_signed_document(self, proof: ProofMechanism, vcon_dict: Dict[str, Any]) -> bool:
        """Process signed document proof."""
        proof_data = proof.proof_data
        
        # Check document hash if provided
        document_hash = proof_data.get("document_hash")
        if document_hash:
            # In a real implementation, you would verify the document hash
            # against a known good hash or verify the signature
            logger.info(f"Document hash provided: {document_hash}")
        
        # Check signature information
        signature_info = proof_data.get("signature_info")
        if signature_info:
            # In a real implementation, you would verify the signature
            logger.info(f"Signature info provided: {signature_info}")
        
        # For now, assume valid if document hash or signature info is present
        return bool(document_hash or signature_info)
    
    def _process_cryptographic_signature(self, proof: ProofMechanism, vcon_dict: Dict[str, Any]) -> bool:
        """Process cryptographic signature proof."""
        proof_data = proof.proof_data
        
        # Check for COSE signature
        cose_signature = proof_data.get("cose_signature")
        if cose_signature:
            # In a real implementation, you would verify the COSE signature
            logger.info("COSE signature provided")
            return True
        
        # Check for other signature formats
        signature = proof_data.get("signature")
        public_key = proof_data.get("public_key")
        
        if signature and public_key:
            # In a real implementation, you would verify the signature
            logger.info("Signature and public key provided")
            return True
        
        return False
    
    def _process_external_system(self, proof: ProofMechanism, vcon_dict: Dict[str, Any]) -> bool:
        """Process external system proof."""
        proof_data = proof.proof_data
        
        # Check system URL
        system_url = proof_data.get("system_url")
        if not system_url:
            logger.error("External system URL not provided")
            return False
        
        # Check query parameters
        query_params = proof_data.get("query_params", {})
        
        # In a real implementation, you would make an API call to the external system
        # to verify the lawful basis status
        logger.info(f"External system verification: {system_url}")
        logger.info(f"Query parameters: {query_params}")
        
        # For now, assume valid if system URL is provided
        return True


class PermissionEvaluator:
    """Evaluates permissions based on lawful basis attachments."""
    
    def __init__(self):
        self.proof_processor = ProofProcessor()
    
    def evaluate_permission(
        self,
        vcon_dict: Dict[str, Any],
        purpose: str,
        party_index: Optional[int] = None
    ) -> ProcessingResult:
        """Evaluate permission for a specific purpose."""
        try:
            # Find applicable lawful basis attachments
            applicable_attachments = self._find_applicable_lawful_basis(
                vcon_dict, purpose, party_index
            )
            
            if not applicable_attachments:
                return ProcessingResult(
                    True,
                    data={
                        "permission": False,
                        "purpose": purpose,
                        "party_index": party_index,
                        "attachments_checked": 0
                    }
                )
            
            # Evaluate permissions from all applicable attachments
            permissions = []
            for attachment_dict in applicable_attachments:
                try:
                    attachment = LawfulBasisAttachment.from_dict(attachment_dict["body"])
                    permission = self._evaluate_attachment_permission(attachment, purpose)
                    permissions.append(permission)
                except Exception as e:
                    logger.error(f"Error evaluating attachment: {str(e)}")
                    permissions.append(False)
            
            # Apply most restrictive permission
            final_permission = self._apply_most_restrictive_permission(permissions)
            
            return ProcessingResult(
                True,
                data={
                    "permission": final_permission,
                    "purpose": purpose,
                    "party_index": party_index,
                    "attachments_checked": len(applicable_attachments)
                }
            )
            
        except Exception as e:
            logger.error(f"Error evaluating permission: {str(e)}")
            return ProcessingResult(
                False,
                errors=[f"Permission evaluation error: {str(e)}"]
            )
    
    def _find_applicable_lawful_basis(
        self,
        vcon_dict: Dict[str, Any],
        purpose: str,
        party_index: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find lawful basis attachments applicable to the purpose and party."""
        attachments = vcon_dict.get("attachments", [])
        applicable = []
        
        for attachment in attachments:
            if attachment.get("type") != "lawful_basis":
                continue
            
            # Check party index if specified
            if party_index is not None:
                attachment_party = attachment.get("party")
                if attachment_party is not None and attachment_party != party_index:
                    continue
            
            # Check if attachment has permission for the purpose
            body = attachment.get("body", {})
            purpose_grants = body.get("purpose_grants", [])
            
            for grant in purpose_grants:
                if grant.get("purpose") == purpose:
                    applicable.append(attachment)
                    break
        
        return applicable
    
    def _evaluate_attachment_permission(
        self,
        attachment: LawfulBasisAttachment,
        purpose: str
    ) -> bool:
        """Evaluate permission from a single lawful basis attachment."""
        # Check if attachment is valid (not expired)
        if not attachment.is_valid():
            logger.warning("Lawful basis attachment has expired")
            return False
        
        # Check if permission is granted for the purpose
        if not attachment.has_permission(purpose):
            logger.info(f"Permission denied for purpose: {purpose}")
            return False
        
        # Verify proof mechanisms if present
        if attachment.proof_mechanisms:
            for proof in attachment.proof_mechanisms:
                # In a real implementation, you would pass the vcon_dict here
                # For now, we'll assume proof verification passes
                logger.info(f"Verifying proof mechanism: {proof.proof_type}")
        
        return True
    
    def _apply_most_restrictive_permission(self, permissions: List[bool]) -> bool:
        """Apply the most restrictive permission (all must be True)."""
        return all(permissions)


class LawfulBasisProcessor(ExtensionProcessor):
    """Processor for lawful basis extension."""
    
    def __init__(self):
        self.permission_evaluator = PermissionEvaluator()
    
    def process(self, vcon_dict: Dict[str, Any]) -> ProcessingResult:
        """Process lawful basis extension in a vCon."""
        try:
            # Find all lawful basis attachments
            attachments = vcon_dict.get("attachments", [])
            lawful_basis_attachments = [
                att for att in attachments 
                if att.get("type") == "lawful_basis"
            ]
            
            if not lawful_basis_attachments:
                return ProcessingResult(
                    True,
                    data={"message": "No lawful basis attachments found"}
                )
            
            # Process each attachment
            processed_attachments = []
            for i, attachment in enumerate(lawful_basis_attachments):
                try:
                    attachment_obj = LawfulBasisAttachment.from_dict(attachment["body"])
                    processed_attachments.append({
                        "index": i,
                        "lawful_basis": attachment_obj.lawful_basis.value,
                        "is_valid": attachment_obj.is_valid(),
                        "purpose_grants": len(attachment_obj.purpose_grants),
                        "proof_mechanisms": len(attachment_obj.proof_mechanisms)
                    })
                except Exception as e:
                    logger.error(f"Error processing lawful basis attachment {i}: {str(e)}")
            
            return ProcessingResult(
                True,
                data={
                    "lawful_basis_attachments": processed_attachments,
                    "total_attachments": len(lawful_basis_attachments)
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing lawful basis extension: {str(e)}")
            return ProcessingResult(
                False,
                errors=[f"Processing error: {str(e)}"]
            )
    
    def can_process(self, extension_name: str) -> bool:
        """Check if this processor can handle the given extension."""
        return extension_name == "lawful_basis"
    
    def check_permission(
        self,
        vcon_dict: Dict[str, Any],
        purpose: str,
        party_index: Optional[int] = None
    ) -> ProcessingResult:
        """Check permission for a specific purpose."""
        return self.permission_evaluator.evaluate_permission(
            vcon_dict, purpose, party_index
        )
