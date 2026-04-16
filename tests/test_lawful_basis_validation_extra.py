"""Extra tests for lawful basis validation paths."""

from datetime import datetime, timezone, timedelta

from src.vcon.extensions.lawful_basis.validation import LawfulBasisValidator
from src.vcon.extensions.lawful_basis.attachment import (
    LawfulBasisAttachment,
    LawfulBasisType,
    PurposeGrant,
    ContentHash,
    HashAlgorithm,
    CanonicalizationMethod,
)


def test_validate_attachment_with_invalid_fields():
    validator = LawfulBasisValidator()
    attachment = {
        "purpose": "lawful_basis",
        "encoding": "json",
        "body": {
            "lawful_basis": "invalid",
            "expiration": "bad",
            "purpose_grants": [
                {
                    "purpose": "recording",
                    "granted": "yes",
                    "granted_at": "bad",
                    "conditions": "no",
                }
            ],
            "content_hash": {
                "algorithm": "bad",
                "canonicalization": "bad",
                "value": "zzzz",
            },
            "proof_mechanisms": [
                {"proof_type": "bad", "timestamp": "bad", "proof_data": "no"}
            ],
            "registry": {"type": "unknown", "url": "ftp://example.com"},
        },
    }

    result = validator.validate_attachment(attachment)
    assert not result.is_valid
    assert result.errors


def test_validate_lawful_basis_attachment_expired_and_missing_grants():
    validator = LawfulBasisValidator()
    expired = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    grant = PurposeGrant(
        purpose="recording",
        granted=True,
        granted_at=datetime.now(timezone.utc).isoformat(),
    )
    attachment = LawfulBasisAttachment(
        lawful_basis=LawfulBasisType.CONSENT,
        expiration=expired,
        purpose_grants=[grant],
        content_hash=ContentHash(
            algorithm=HashAlgorithm.SHA_256,
            canonicalization=CanonicalizationMethod.JCS,
            value="bad",
        ),
    )

    result = validator.validate_lawful_basis_attachment(attachment)
    assert not result.is_valid

    attachment = LawfulBasisAttachment(
        lawful_basis=LawfulBasisType.CONSENT,
        expiration=None,
        purpose_grants=[],
    )
    result = validator.validate_lawful_basis_attachment(attachment)
    assert not result.is_valid
