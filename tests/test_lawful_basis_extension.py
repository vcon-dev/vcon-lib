"""
Tests for Lawful Basis Extension

This module contains tests for the lawful basis extension functionality.
"""

import pytest
import json
from datetime import datetime, timezone, timedelta
from src.vcon.extensions.lawful_basis import (
    LawfulBasisExtension,
    LawfulBasisAttachment,
    PurposeGrant,
    ContentHash,
    ProofMechanism,
    RegistryInfo,
    LawfulBasisType,
    ProofType,
    HashAlgorithm,
    CanonicalizationMethod
)
from src.vcon.extensions.lawful_basis.validation import LawfulBasisValidator
from src.vcon.extensions.lawful_basis.processing import LawfulBasisProcessor


class TestLawfulBasisAttachment:
    """Test LawfulBasisAttachment class."""
    
    def test_create_lawful_basis_attachment(self):
        """Test creating a lawful basis attachment."""
        expiration = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        
        purpose_grants = [
            PurposeGrant(
                purpose="recording",
                granted=True,
                granted_at=datetime.now(timezone.utc).isoformat()
            ),
            PurposeGrant(
                purpose="analysis",
                granted=True,
                granted_at=datetime.now(timezone.utc).isoformat(),
                conditions=["anonymized_data_only"]
            )
        ]
        
        attachment = LawfulBasisAttachment(
            lawful_basis=LawfulBasisType.CONSENT,
            expiration=expiration,
            purpose_grants=purpose_grants
        )
        
        assert attachment.lawful_basis == LawfulBasisType.CONSENT
        assert attachment.is_valid()
        assert attachment.has_permission("recording")
        assert attachment.has_permission("analysis")
        assert not attachment.has_permission("marketing")
        assert attachment.get_conditions("analysis") == ["anonymized_data_only"]
    
    def test_expired_attachment(self):
        """Test expired lawful basis attachment."""
        expiration = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        purpose_grants = [
            PurposeGrant(
                purpose="recording",
                granted=True,
                granted_at=datetime.now(timezone.utc).isoformat()
            )
        ]
        
        attachment = LawfulBasisAttachment(
            lawful_basis=LawfulBasisType.CONSENT,
            expiration=expiration,
            purpose_grants=purpose_grants
        )
        
        assert not attachment.is_valid()
    
    def test_content_hash_validation(self):
        """Test content hash validation."""
        content_hash = ContentHash(
            algorithm=HashAlgorithm.SHA_256,
            canonicalization=CanonicalizationMethod.JCS,
            value="test_hash_value"
        )
        
        # Test with valid content
        test_content = {"test": "data"}
        # Note: This will fail validation since we're using a dummy hash
        # In real usage, you would compute the actual hash
        assert not content_hash.validate(test_content)
    
    def test_serialization(self):
        """Test serialization and deserialization."""
        expiration = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        
        purpose_grants = [
            PurposeGrant(
                purpose="recording",
                granted=True,
                granted_at=datetime.now(timezone.utc).isoformat()
            )
        ]
        
        attachment = LawfulBasisAttachment(
            lawful_basis=LawfulBasisType.CONSENT,
            expiration=expiration,
            purpose_grants=purpose_grants
        )
        
        # Serialize to dict
        attachment_dict = attachment.to_dict()
        
        # Deserialize from dict
        restored_attachment = LawfulBasisAttachment.from_dict(attachment_dict)
        
        assert restored_attachment.lawful_basis == attachment.lawful_basis
        assert restored_attachment.has_permission("recording")
        assert restored_attachment.is_valid()


class TestLawfulBasisValidator:
    """Test LawfulBasisValidator class."""
    
    def test_validate_attachment(self):
        """Test attachment validation."""
        validator = LawfulBasisValidator()
        
        # Valid attachment
        valid_attachment = {
            "type": "lawful_basis",
            "encoding": "json",
            "body": {
                "lawful_basis": "consent",
                "expiration": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                "purpose_grants": [
                    {
                        "purpose": "recording",
                        "granted": True,
                        "granted_at": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }
        }
        
        result = validator.validate_attachment(valid_attachment)
        assert result.is_valid
        
        # Invalid attachment (wrong type)
        invalid_attachment = {
            "type": "invalid_type",
            "encoding": "json",
            "body": {}
        }
        
        result = validator.validate_attachment(invalid_attachment)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_validate_extension_usage(self):
        """Test extension usage validation."""
        validator = LawfulBasisValidator()
        
        vcon_dict = {
            "extensions": ["lawful_basis"],
            "attachments": [
                {
                    "type": "lawful_basis",
                    "encoding": "json",
                    "body": {
                        "lawful_basis": "consent",
                        "expiration": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                        "purpose_grants": [
                            {
                                "purpose": "recording",
                                "granted": True,
                                "granted_at": datetime.now(timezone.utc).isoformat()
                            }
                        ]
                    }
                }
            ]
        }
        
        result = validator.validate_extension_usage(vcon_dict)
        assert result.is_valid


class TestLawfulBasisProcessor:
    """Test LawfulBasisProcessor class."""
    
    def test_process_lawful_basis_extension(self):
        """Test processing lawful basis extension."""
        processor = LawfulBasisProcessor()
        
        vcon_dict = {
            "attachments": [
                {
                    "type": "lawful_basis",
                    "encoding": "json",
                    "body": {
                        "lawful_basis": "consent",
                        "expiration": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                        "purpose_grants": [
                            {
                                "purpose": "recording",
                                "granted": True,
                                "granted_at": datetime.now(timezone.utc).isoformat()
                            }
                        ]
                    }
                }
            ]
        }
        
        result = processor.process(vcon_dict)
        assert result.success
        assert "lawful_basis_attachments" in result.data
    
    def test_check_permission(self):
        """Test permission checking."""
        processor = LawfulBasisProcessor()
        
        vcon_dict = {
            "attachments": [
                {
                    "type": "lawful_basis",
                    "encoding": "json",
                    "body": {
                        "lawful_basis": "consent",
                        "expiration": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                        "purpose_grants": [
                            {
                                "purpose": "recording",
                                "granted": True,
                                "granted_at": datetime.now(timezone.utc).isoformat()
                            }
                        ]
                    }
                }
            ]
        }
        
        # Check granted permission
        result = processor.check_permission(vcon_dict, "recording")
        assert result.success
        assert result.data["permission"] is True
        
        # Check denied permission
        result = processor.check_permission(vcon_dict, "marketing")
        assert result.success
        assert result.data["permission"] is False


class TestLawfulBasisExtension:
    """Test LawfulBasisExtension class."""
    
    def test_get_extension_info(self):
        """Test getting extension information."""
        extension = LawfulBasisExtension()
        info = extension.get_extension_info()
        
        assert info.name == "lawful_basis"
        assert info.version == "1.0"
        assert "lawful_basis" in info.attachment_types
    
    def test_create_lawful_basis_attachment(self):
        """Test creating lawful basis attachment."""
        extension = LawfulBasisExtension()
        
        expiration = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        purpose_grants = [
            {
                "purpose": "recording",
                "granted": True,
                "granted_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        attachment = extension.create_lawful_basis_attachment(
            lawful_basis="consent",
            expiration=expiration,
            purpose_grants=purpose_grants
        )
        
        assert attachment["type"] == "lawful_basis"
        assert attachment["encoding"] == "json"
        assert "body" in attachment
        assert attachment["body"]["lawful_basis"] == "consent"
    
    def test_validate_lawful_basis_attachment(self):
        """Test validating lawful basis attachment."""
        extension = LawfulBasisExtension()
        
        valid_attachment = {
            "type": "lawful_basis",
            "encoding": "json",
            "body": {
                "lawful_basis": "consent",
                "expiration": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                "purpose_grants": [
                    {
                        "purpose": "recording",
                        "granted": True,
                        "granted_at": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }
        }
        
        assert extension.validate_lawful_basis_attachment(valid_attachment)
    
    def test_check_permission(self):
        """Test checking permission."""
        extension = LawfulBasisExtension()
        
        vcon_dict = {
            "attachments": [
                {
                    "type": "lawful_basis",
                    "encoding": "json",
                    "body": {
                        "lawful_basis": "consent",
                        "expiration": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                        "purpose_grants": [
                            {
                                "purpose": "recording",
                                "granted": True,
                                "granted_at": datetime.now(timezone.utc).isoformat()
                            }
                        ]
                    }
                }
            ]
        }
        
        assert extension.check_permission(vcon_dict, "recording")
        assert not extension.check_permission(vcon_dict, "marketing")
