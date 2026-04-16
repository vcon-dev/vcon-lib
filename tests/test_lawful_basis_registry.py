"""Tests for lawful basis registry integration."""

from datetime import datetime, timezone
import requests
import pytest

from src.vcon.extensions.lawful_basis.attachment import (
    LawfulBasisAttachment,
    PurposeGrant,
    LawfulBasisType,
)
from src.vcon.extensions.lawful_basis.registry import (
    SCITTRegistryClient,
    RegistryManager,
    RegistryValidator,
)


class StubResponse:
    def __init__(self, json_data, status_code=200, raise_error=False):
        self._json_data = json_data
        self.status_code = status_code
        self._raise_error = raise_error

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self._raise_error or self.status_code >= 400:
            raise requests.RequestException("http error")


class StubSession:
    def __init__(self, responses=None, raise_error=False):
        self.responses = responses or {}
        self.raise_error = raise_error
        self.headers = {}

    def post(self, url, json=None, timeout=None):
        if self.raise_error:
            raise requests.RequestException("post failed")
        return self.responses.get("post")

    def get(self, url, timeout=None):
        if self.raise_error:
            raise requests.RequestException("get failed")
        return self.responses.get("get")

    def patch(self, url, json=None, timeout=None):
        if self.raise_error:
            raise requests.RequestException("patch failed")
        return self.responses.get("patch")


def _lawful_basis_attachment():
    grant = PurposeGrant(
        purpose="recording",
        granted=True,
        granted_at=datetime.now(timezone.utc).isoformat(),
    )
    return LawfulBasisAttachment(
        lawful_basis=LawfulBasisType.CONSENT,
        expiration=None,
        purpose_grants=[grant],
    )


def test_scitt_submit_attestation_success():
    client = SCITTRegistryClient("https://registry.example")
    client.session = StubSession(
        responses={"post": StubResponse({"receipt_id": "abc123"})}
    )

    receipt_id = client.submit_attestation(_lawful_basis_attachment())
    assert receipt_id == "abc123"


def test_scitt_submit_attestation_missing_receipt_id():
    client = SCITTRegistryClient("https://registry.example")
    client.session = StubSession(
        responses={"post": StubResponse({"status": "ok"})}
    )

    with pytest.raises(ValueError) as excinfo:
        client.submit_attestation(_lawful_basis_attachment())
    assert "receipt_id" in str(excinfo.value)


def test_scitt_verify_receipt_success_and_failure():
    client = SCITTRegistryClient("https://registry.example")
    client.session = StubSession(
        responses={
            "get": StubResponse(
                {"receipt_id": "r1", "timestamp": datetime.now(timezone.utc).isoformat(), "status": "verified"}
            )
        }
    )

    result = client.verify_receipt("r1")
    assert result.is_valid

    client.session = StubSession(
        responses={
            "get": StubResponse(
                {"receipt_id": "r1", "timestamp": datetime.now(timezone.utc).isoformat(), "status": "rejected"}
            )
        }
    )
    result = client.verify_receipt("r1")
    assert not result.is_valid


def test_scitt_query_status_error():
    client = SCITTRegistryClient("https://registry.example")
    client.session = StubSession(raise_error=True)

    status = client.query_status("attestation-1")
    assert "error" in status


def test_scitt_update_attestation_paths():
    client = SCITTRegistryClient("https://registry.example")
    client.session = StubSession(responses={"patch": StubResponse({"ok": True})})

    assert client.update_attestation("attestation-1", {"status": "ok"})

    client.session = StubSession(raise_error=True)
    assert not client.update_attestation("attestation-1", {"status": "ok"})


def test_registry_manager_and_validator():
    manager = RegistryManager()
    client = SCITTRegistryClient("https://registry.example")
    client.session = StubSession(responses={"post": StubResponse({"receipt_id": "abc123"})})

    manager.register_client("scitt", client)
    receipt_id = manager.submit_to_registry(_lawful_basis_attachment(), "scitt")
    assert receipt_id == "abc123"

    missing_result = manager.verify_registry_status("r1", "missing")
    assert not missing_result.is_valid

    missing_status = manager.query_registry_status("r1", "missing")
    assert "error" in missing_status

    receipt = {
        "receipt_id": "r1",
        "timestamp": "invalid",
        "status": "unknown",
    }
    result = RegistryValidator.validate_scitt_receipt(receipt)
    assert not result.is_valid
    assert result.warnings

    status = {"error": "boom"}
    result = RegistryValidator.validate_attestation_status(status)
    assert not result.is_valid

    metadata = {}
    result = RegistryValidator.validate_registry_metadata(metadata)
    assert result.warnings
