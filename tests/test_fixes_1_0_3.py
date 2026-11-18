"""Regression tests for the 1.0.3 fixes."""

import logging
import subprocess
import sys
from datetime import datetime, timezone

import pytest

from vcon import Vcon, Session, compute_content_hash
from vcon.dialog import Dialog, b64url_encode
from vcon.party import Party
from vcon.extensions.lawful_basis.attachment import (
    CanonicalizationMethod,
    ContentHash,
    HashAlgorithm,
)


def _png(tmp_path):
    PIL = pytest.importorskip("PIL.Image")
    path = tmp_path / "pixel.jpg"
    PIL.new("RGB", (1, 1)).save(path, "JPEG")
    return path


def _vcon_with_sessions(n):
    v = Vcon.build_new()
    v.add_party(Party(tel="+15551230001"))
    for _ in range(n):
        v.add_session(Session(start=datetime.now(timezone.utc), parties=[0]))
    return v


class TestAddImageScope:
    def test_uses_the_only_session(self, tmp_path):
        v = _vcon_with_sessions(1)
        v.add_image(str(_png(tmp_path)))
        att = v.attachments[0]
        assert att["session"] == 0
        assert att["party"] == 0
        assert v.is_valid() == (True, [])

    def test_explicit_scope(self, tmp_path):
        v = _vcon_with_sessions(2)
        v.add_image(str(_png(tmp_path)), party=0, session=1)
        assert v.attachments[0]["session"] == 1
        assert v.is_valid() == (True, [])

    def test_ambiguous_scope_raises(self, tmp_path):
        v = _vcon_with_sessions(2)
        with pytest.raises(ValueError):
            v.add_image(str(_png(tmp_path)))
        assert v.attachments == []


class TestImageContentHash:
    def test_add_image_data_hash_verifies(self, tmp_path):
        path = _png(tmp_path)
        d = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0])
        d.add_image_data(str(path))
        assert d.content_hash == compute_content_hash(path.read_bytes())
        assert d.verify_content_hash(d.content_hash)
        assert d.calculate_content_hash() == d.content_hash

    def test_legacy_hash_of_encoded_body_still_verifies(self):
        data = b"\x00\x01binary"
        body = b64url_encode(data)
        d = Dialog(type="recording", start=datetime.now(timezone.utc), parties=[0],
                   body=body, encoding="base64url", mediatype="audio/x-wav")
        assert d.verify_content_hash(compute_content_hash(body.encode()))
        assert d.verify_content_hash(compute_content_hash(data))
        assert not d.verify_content_hash(compute_content_hash(b"other"))

    def test_text_body_unchanged(self):
        d = Dialog(type="text", start=datetime.now(timezone.utc), parties=[0],
                   body="hello", encoding="none", mediatype="text/plain")
        assert d.calculate_content_hash() == compute_content_hash(b"hello")


class TestContentHashStrings:
    def test_accepts_strings(self):
        h = ContentHash(algorithm="sha-256", canonicalization="JCS", value="x")
        assert h.algorithm is HashAlgorithm.SHA_256
        assert h.canonicalization is CanonicalizationMethod.JCS
        assert h.to_dict()["canonicalization"] == "jcs"

    def test_accepts_enums(self):
        h = ContentHash(HashAlgorithm.BLAKE2B_256, CanonicalizationMethod.JCS, "x")
        assert h.to_dict()["algorithm"] == "blake2b-256"

    def test_rejects_unknown_values(self):
        with pytest.raises(ValueError):
            ContentHash(algorithm="md5", canonicalization="jcs", value="x")


def test_import_does_not_configure_root_logging():
    code = (
        "import logging, vcon\n"
        "root = logging.getLogger()\n"
        "print(root.level, len(root.handlers))\n"
    )
    out = subprocess.run([sys.executable, "-W", "ignore", "-c", code],
                         capture_output=True, text=True, check=True)
    assert out.stdout.split() == [str(logging.WARNING), "0"]
