"""Regression tests for the 1.0.4 fixes."""

import shutil
import subprocess
import sys

import pytest
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa

from vcon import Vcon, Session, compute_content_hash
from vcon.dialog import Dialog, b64url_encode
from vcon.party import Party
from vcon.validation import content_hash_problems

T = "2026-01-01T00:00:00Z"
H = compute_content_hash(b"example content")


def _base():
    v = Vcon.build_new()
    v.add_party(Party(name="Alice"))
    v.add_session(Session(start=T, parties=[0]))
    return v


def _recording(**kw):
    return Dialog(type="recording", start=T, parties=[0], mediatype="audio/x-wav", **kw)


class TestContentHash:
    def test_url_without_content_hash_is_allowed(self):
        # 1.0.6: allowed on Dialog, Attachment and Analysis (WG direction on
        # draft-ietf-vcon-vcon-core issue #40, e.g. a YouTube recording link).
        v = _base()
        v.add_dialog(_recording(url="https://www.youtube.com/watch?v=x"), session=0)
        v.add_attachment("doc", url="https://example.com/d.pdf", party=0, session=0)
        v.add_analysis(type="summary", vendor="v", url="https://example.com/s.json",
                       sessions=0, body=None)
        assert v.is_valid() == (True, [])
        assert not any("content_hash" in w for w in v.get_validation_warnings())

    def test_redacted_and_amended_from_still_need_content_hash(self):
        v = _base()
        v.vcon_dict["amended_from"] = {"url": "https://example.com/v.json"}
        assert "amended_from with url must include content_hash." in v.is_valid()[1]

    def test_well_formed_hash_passes(self):
        v = _base()
        v.add_dialog(_recording(url="https://example.com/a.wav", content_hash=H), session=0)
        assert v.is_valid() == (True, [])

    @pytest.mark.parametrize("bad", ["sha512-abc", "abc", "sha512-", "SHA512-x", "sha256-" + "A" * 44, 5, []])
    def test_malformed_hash_is_an_error(self, bad):
        assert content_hash_problems(bad)
        v = _base()
        v.add_dialog(_recording(url="https://example.com/a.wav", content_hash=bad), session=0)
        assert any("invalid content_hash" in e for e in v.is_valid()[1])

    def test_hash_array_and_unknown_algorithm(self):
        assert content_hash_problems([H, compute_content_hash(b"x", "sha256")]) == []
        assert content_hash_problems("blake3-abcdef") == []

    def test_attachment_and_analysis_are_checked(self):
        v = _base()
        v.vcon_dict["attachments"].append({"purpose": "doc", "start": T, "party": 0, "session": 0})
        v.add_analysis(type="summary", vendor="v", url="https://example.com/s.json",
                       content_hash="sha512-x", sessions=0, body=None)
        errors = v.is_valid()[1]
        assert any(e.startswith("Attachment at index 0 must include") for e in errors)
        assert any(e.startswith("Analysis at index 0 has an invalid content_hash") for e in errors)


def test_serialized_json_body_is_a_warning():
    def with_body(body):
        v = _base()
        v.vcon_dict["analysis"].append(
            {"type": "summary", "vendor": "v", "body": body, "encoding": "json", "sessions": 0})
        return v
    v = with_body('{"a": 1}')
    assert v.is_valid() == (True, [])
    assert any("serialized JSON string" in w for w in v.get_validation_warnings())
    w = with_body("plain words")  # a JSON string value is allowed
    assert not any("serialized JSON string" in x for x in w.get_validation_warnings())


class TestLawfulBasisBody:
    def _attach(self, body):
        v = _base()
        v.add_extension("lawful_basis")
        v.vcon_dict["attachments"].append({
            "purpose": "lawful_basis", "start": T, "party": 0, "session": [0],
            "encoding": "json", "mediatype": "application/json", "body": body,
        })
        return v

    def test_missing_body_fields_are_errors(self):
        ok, errors = self._attach({"lawful_basis": "consent"}).is_valid()
        assert not ok
        assert any("(lawful_basis): Missing required field: purpose_grants" in e for e in errors)

    def test_complete_body_is_valid(self):
        v = self._attach({"lawful_basis": "consent", "expiration": None,
                          "purpose_grants": [{"purpose": "recording", "granted": True, "granted_at": T}]})
        assert v.is_valid() == (True, [])

    def test_unknown_proof_type_is_a_warning(self):
        v = self._attach({
            "lawful_basis": "consent", "expiration": None,
            "purpose_grants": [{"purpose": "recording", "granted": True, "granted_at": T}],
            "proof_mechanisms": [{"proof_type": "biometric_hold", "timestamp": T, "proof_data": {}}],
        })
        assert v.is_valid() == (True, [])
        assert any("biometric_hold" in w for w in v.get_validation_warnings())

    def test_library_helper_output_is_valid(self):
        v = _base()
        v.add_lawful_basis_attachment(
            lawful_basis="consent", expiration="2030-01-01T00:00:00Z",
            purpose_grants=[{"purpose": "recording", "granted": True, "granted_at": T}],
            party_index=0, session_index=0,
        )
        assert v.is_valid() == (True, [])


def test_add_inline_data_accepts_bytes():
    d = Dialog(type="recording", start=T, parties=[0])
    d.add_inline_data(b"\x00\x01raw", "a.wav", "audio/x-wav")
    assert d.body == b64url_encode(b"\x00\x01raw")
    assert d.content_hash == compute_content_hash(b"\x00\x01raw")
    assert d.verify_content_hash(d.content_hash)


def test_wtf_attachment_helper_is_deprecated():
    v = _base()
    with pytest.warns(DeprecationWarning, match="add_wtf_transcription_analysis"):
        v.add_wtf_transcription_attachment(
            transcript={"text": "hi", "language": "en", "duration": 1.0, "confidence": 0.9},
            segments=[{"id": 0, "start": 0.0, "end": 1.0, "text": "hi", "confidence": 0.9}],
            metadata={"created_at": T, "processed_at": T, "provider": "whisper", "model": "whisper-1"},
            party_index=0, session_index=0,
        )


@pytest.mark.parametrize("alg,key", [
    ("RS256", rsa.generate_private_key(public_exponent=65537, key_size=2048)),
    ("PS512", rsa.generate_private_key(public_exponent=65537, key_size=2048)),
    ("ES256", ec.generate_private_key(ec.SECP256R1())),
    ("EdDSA", ed25519.Ed25519PrivateKey.generate()),
])
def test_sign_and_verify_with_key_objects(alg, key):
    v = _base()
    v.sign(key, alg=alg)
    assert v.verify(key.public_key())
    other = type(key) is ed25519.Ed25519PrivateKey and ed25519.Ed25519PrivateKey.generate()
    if other:
        assert not v.verify(other.public_key())


def test_import_does_not_warn():
    out = subprocess.run([sys.executable, "-W", "error", "-c", "import vcon"],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr


class TestVideoHelpers:
    def test_missing_ffmpeg_python_has_a_clear_error(self, monkeypatch):
        import vcon.dialog as dialog_module
        monkeypatch.setitem(sys.modules, "ffmpeg", None)
        with pytest.raises(ImportError, match=r"vcon\[video\]"):
            dialog_module._import_ffmpeg()

    def test_generate_thumbnail_dispatches(self, monkeypatch):
        d = Dialog(type="recording", start=T, parties=[0], mediatype="video/mp4")
        monkeypatch.setattr(Dialog, "generate_video_thumbnail", lambda self, *a, **k: b"video")
        monkeypatch.setattr(Dialog, "generate_image_thumbnail", lambda self, *a, **k: "image")
        assert d.generate_thumbnail(timestamp=1.0) == b"video"
        d.mediatype = "image/jpeg"
        assert d.generate_thumbnail() == "image"

    @pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="needs the ffmpeg binary")
    def test_real_video(self, tmp_path):
        pytest.importorskip("ffmpeg").probe  # ffmpeg-python, not the empty "ffmpeg" package
        clip = tmp_path / "clip.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                        "testsrc=duration=1:size=160x120:rate=10", "-pix_fmt", "yuv420p", str(clip)],
                       check=True)
        d = Dialog(type="recording", start=T, parties=[0])
        d.add_video_data(clip.read_bytes(), filename="clip.mp4")
        meta = d.extract_video_metadata()
        assert (meta["width"], meta["height"]) == (160, 120)
        assert d.generate_thumbnail(timestamp=0.5)[:3] == b"\xff\xd8\xff"
