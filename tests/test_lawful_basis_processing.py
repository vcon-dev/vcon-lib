"""Tests for lawful basis processing helpers."""

from datetime import datetime, timezone, timedelta

from src.vcon.extensions.lawful_basis.attachment import ProofMechanism, ProofType
from src.vcon.extensions.lawful_basis.processing import ProofProcessor, PermissionEvaluator


def test_proof_processor_verbal_confirmation():
    processor = ProofProcessor()
    proof = ProofMechanism(
        proof_type=ProofType.VERBAL_CONFIRMATION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={"dialog_reference": 0, "confirmation_text": "I consent"},
    )

    assert processor.process_proof(proof, {"dialog": [{}]})

    proof = ProofMechanism(
        proof_type=ProofType.VERBAL_CONFIRMATION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={"dialog_reference": 3, "confirmation_text": "No"},
    )
    assert not processor.process_proof(proof, {"dialog": [{}]})


def test_proof_processor_signed_document():
    processor = ProofProcessor()
    proof = ProofMechanism(
        proof_type=ProofType.SIGNED_DOCUMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={"document_hash": "abc"},
    )

    assert processor.process_proof(proof, {})

    proof = ProofMechanism(
        proof_type=ProofType.SIGNED_DOCUMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={"signature_info": "sig"},
    )
    assert processor.process_proof(proof, {})

    proof = ProofMechanism(
        proof_type=ProofType.SIGNED_DOCUMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={},
    )
    assert not processor.process_proof(proof, {})


def test_proof_processor_crypto_signature():
    processor = ProofProcessor()
    proof = ProofMechanism(
        proof_type=ProofType.CRYPTOGRAPHIC_SIGNATURE,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={"cose_signature": "cose"},
    )

    assert processor.process_proof(proof, {})

    proof = ProofMechanism(
        proof_type=ProofType.CRYPTOGRAPHIC_SIGNATURE,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={"signature": "sig", "public_key": "key"},
    )
    assert processor.process_proof(proof, {})

    proof = ProofMechanism(
        proof_type=ProofType.CRYPTOGRAPHIC_SIGNATURE,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={},
    )
    assert not processor.process_proof(proof, {})


def test_proof_processor_external_system():
    processor = ProofProcessor()
    proof = ProofMechanism(
        proof_type=ProofType.EXTERNAL_SYSTEM,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={},
    )
    assert not processor.process_proof(proof, {})

    proof = ProofMechanism(
        proof_type=ProofType.EXTERNAL_SYSTEM,
        timestamp=datetime.now(timezone.utc).isoformat(),
        proof_data={"system_url": "https://example.com"},
    )
    assert processor.process_proof(proof, {})


def test_permission_evaluator_paths():
    evaluator = PermissionEvaluator()
    result = evaluator.evaluate_permission({"attachments": []}, "recording")
    assert result.success
    assert result.data["permission"] is False

    future_expiration = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    vcon_dict = {
        "attachments": [
            {
                "purpose": "lawful_basis",
                "encoding": "json",
                "body": {
                    "lawful_basis": "consent",
                    "expiration": future_expiration,
                    "purpose_grants": [
                        {
                            "purpose": "recording",
                            "granted": True,
                            "granted_at": datetime.now(timezone.utc).isoformat(),
                        }
                    ],
                },
            }
        ]
    }

    result = evaluator.evaluate_permission(vcon_dict, "recording")
    assert result.success
    assert result.data["permission"] is True

    vcon_dict["attachments"][0]["body"]["purpose_grants"][0]["granted"] = False
    result = evaluator.evaluate_permission(vcon_dict, "recording")
    assert result.success
    assert result.data["permission"] is False
