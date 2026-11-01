"""Behaviour that changed in vCon 0.5.0 (draft-ietf-vcon-vcon-core-05)."""

import base64
import json

import pytest

from vcon import Vcon, Dialog, Session, Event, AlgorithmNotPermittedError
from vcon.party import Party
from vcon.vcon import Attachment

T = "2026-01-01T00:00:00Z"


def _b64(obj):
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()


def _base():
    v = Vcon.build_new()
    v.add_party(Party(name="Alice"))
    v.add_party(Party(name="Bob"))
    v.add_session(Session(start=T, parties=[0, 1]))
    return v


class TestRedactedFromAmendedFrom:
    def test_properties_replace_old_names(self):
        v = Vcon({"uuid": "a", "created_at": T, "redacted_from": {"uuid": "b", "type": "PII"}})
        assert v.redacted_from == {"uuid": "b", "type": "PII"}
        assert v.amended_from is None
        # the 0.4.0 names remain as deprecated aliases (TestDeprecatedApi)
        w = Vcon({"uuid": "a", "created_at": T, "amended_from": {"uuid": "b"}})
        assert w.amended_from == {"uuid": "b"}

    def test_mutually_exclusive(self):
        v = _base()
        v.vcon_dict["redacted_from"] = {"uuid": "b", "type": "PII"}
        v.vcon_dict["amended_from"] = {"uuid": "c"}
        valid, errors = v.is_valid()
        assert not valid
        assert any("mutually exclusive" in e for e in errors)

    def test_url_needs_content_hash(self):
        v = _base()
        v.vcon_dict["amended_from"] = {"url": "https://example.com/v.json"}
        assert any("content_hash" in e for e in v.is_valid()[1])
        v.vcon_dict["amended_from"] = {"url": "https://example.com/v.json", "content_hash": "sha512-abc"}
        assert v.is_valid()[0]

    def test_amended_from_needs_uuid_or_url(self):
        v = _base()
        v.vcon_dict["amended_from"] = {}
        assert any("uuid, or an external reference" in e for e in v.is_valid()[1])

    def test_redacted_from_needs_type(self):
        v = _base()
        v.vcon_dict["redacted_from"] = {"uuid": "b"}
        assert any("missing required field: type" in e for e in v.is_valid()[1])

    def test_legacy_names_are_flagged_when_migration_is_off(self):
        v = Vcon(
            {"uuid": "a", "created_at": T, "vcon": "0.4.0", "redacted": {"uuid": "b", "type": "x"}},
            migrate_legacy=False,
        )
        valid, errors = v.is_valid()
        assert not valid
        assert any("'redacted' was renamed 'redacted_from'" in e for e in errors)
        assert any("Unsupported vcon syntax version '0.4.0'" in e for e in errors)

    def test_strict_property_handling_keeps_new_names(self):
        v = Vcon(
            {"uuid": "a", "created_at": T, "redacted_from": {"uuid": "b", "type": "x"}, "junk": 1},
            property_handling="strict",
        )
        assert "redacted_from" in v.vcon_dict and "junk" not in v.vcon_dict


class TestAttachments:
    def test_party_is_required_and_dialog_or_session(self):
        v = _base()
        v.vcon_dict["attachments"].append(
            {"purpose": "x", "body": "b", "encoding": "none", "start": T}
        )
        errors = v.is_valid()[1]
        assert any("missing required field: party" in e for e in errors)
        assert any("at least one of dialog or session" in e for e in errors)

    def test_session_alone_satisfies_the_scope_rule(self):
        v = _base()
        v.add_attachment("x", body="b", party=0, session=0, mediatype="text/plain")
        assert v.vcon_dict["attachments"][0]["session"] == 0
        assert "dialog" not in v.vcon_dict["attachments"][0]
        assert v.is_valid() == (True, [])

    def test_session_list_and_dialog_together(self):
        v = _base()
        v.add_session(Session(start=T))
        v.add_dialog(Dialog(type="text", start=T, parties=[0], body="x", mediatype="text/plain", encoding="none"), session=0)
        v.add_attachment("x", body="b", party=1, dialog=0, session=[0, 1], mediatype="text/plain")
        assert v.is_valid() == (True, [])

    def test_bad_references_are_errors(self):
        v = _base()
        v.add_attachment("x", body="b", party=7, session=3)
        errors = v.is_valid()[1]
        assert any("invalid party index: 7" in e for e in errors)
        assert any("invalid session index: 3" in e for e in errors)

    def test_default_scope_is_the_only_session(self):
        v = _base()
        v.add_attachment("x", body="b")
        assert v.vcon_dict["attachments"][0]["session"] == 0
        assert v.vcon_dict["attachments"][0]["party"] == 0

    def test_no_default_scope_with_several_sessions(self):
        v = _base()
        v.add_session(Session(start=T))
        with pytest.raises(ValueError, match="dialog or session"):
            v.add_attachment("x", body="b")
        assert v.vcon_dict["attachments"] == []

    def test_no_placeholder_session_is_invented(self):
        v = Vcon.build_new()
        with pytest.raises(ValueError, match="dialog or session"):
            v.add_attachment("x", body="b")
        assert v.sessions == []

    def test_tags_describe_the_whole_vcon(self):
        v = Vcon.build_new()
        v.add_tag("k", "v")
        assert v.sessions == [{}]
        assert v.vcon_dict["attachments"][0]["session"] == [0]
        w = _base()
        w.add_session(Session(start=T))
        w.add_tag("k", "v")
        assert w.vcon_dict["attachments"][0]["session"] == [0, 1]

    def test_attachment_class_has_session_and_no_dialog_default(self):
        a = Attachment("p", body="b", session=[0])
        d = a.to_dict()
        assert d["session"] == [0] and "dialog" not in d and d["party"] == 0

    def test_redacted_attachment_may_lack_content(self):
        v = _base()
        v.vcon_dict["redacted_from"] = {"uuid": "b", "type": "PII"}
        v.vcon_dict["attachments"].append({"purpose": "x", "start": T, "party": 0, "session": 0})
        assert v.is_valid() == (True, [])


class TestAnalysis:
    def test_dialog_is_optional_and_new_references_are_checked(self):
        v = _base()
        v.add_analysis(type="summary", vendor="v", body="s", sessions=0)
        assert "dialog" not in v.analysis[0]
        assert v.is_valid() == (True, [])
        v.add_analysis(type="summary", vendor="v", body="s", sessions=5, attachment=2, analysis=1)
        errors = v.is_valid()[1]
        assert any("invalid session index: 5" in e for e in errors)
        assert any("invalid attachment index: 2" in e for e in errors)
        assert any("must not reference itself" in e for e in errors)


class TestDialog:
    def test_dialog_types_are_recording_text_incomplete(self):
        for t in ("recording", "text", "incomplete"):
            assert t in Dialog.VALID_TYPES
        assert "transfer" not in Dialog.VALID_TYPES

    def test_empty_dialog_is_valid_and_keeps_indices(self):
        v = _base()
        v.add_dialog(Dialog.placeholder(), session=0)  # even if a Session lists it
        v.add_dialog(Dialog(type="text", start=T, parties=[0], body="x", mediatype="text/plain", encoding="none"), session=0)
        assert v.dialog[0] == {}
        assert v.is_valid() == (True, [])

    def test_parties_may_contain_nulls_and_lists(self):
        v = _base()
        v.add_dialog(
            Dialog(type="recording", start=T, parties=[[0, 1], None, 1], mediatype="audio/wav", url="https://e.com/a.wav", content_hash="sha512-x"),
            session=0,
        )
        assert v.is_valid() == (True, [])

    def test_incomplete_dialog_has_no_content(self):
        v = _base()
        v.add_incomplete_dialog(start=T, disposition="no-answer", parties=[0], session=0)
        assert v.is_valid() == (True, [])
        d = v.dialog[0]
        assert d["type"] == "incomplete" and "body" not in d
        v.vcon_dict["dialog"][0]["body"] = "x"
        assert any("must not have field: body" in e for e in v.is_valid()[1])

    def test_removed_types_and_parameters_fail_validation(self):
        v = _base()
        v.vcon_dict["dialog"].append({"type": "transfer", "start": T})
        v.vcon_dict["dialog"].append({"type": "text", "start": T, "parties": [0], "originator": 0, "party_history": [],
                                      "body": "x", "mediatype": "text/plain", "encoding": "none"})
        errors = v.is_valid()[1]
        assert any("type 'transfer'" in e and "removed in 0.5.0" in e for e in errors)
        assert any("'originator', which was removed" in e for e in errors)
        assert any("'party_history', which was removed" in e for e in errors)

    def test_no_transfer_dialog_helper(self):
        with pytest.raises(NotImplementedError):
            Vcon.build_new().add_transfer_dialog()

    def test_multipart_alternative_mediatype_with_parameters(self):
        v = _base()
        v.add_dialog(
            Dialog(type="text", start=T, parties=[0], body="x", encoding="none",
                   mediatype='multipart/alternative; boundary="----=_Part_1"'),
            session=0,
        )
        assert v.is_valid() == (True, [])

    def test_redacted_segments(self):
        v = _base()
        v.add_dialog(
            Dialog(type="recording", start=T, parties=[0], mediatype="audio/wav", url="https://e.com/a.wav",
                   content_hash="sha512-x", redacted_segments=[{"start": T, "end": "2026-01-01T00:00:05Z"}]),
            session=0,
        )
        assert v.is_valid() == (True, [])
        v.vcon_dict["dialog"][0]["redacted_segments"] = [{"start": T}]
        assert any("requires start and end" in e for e in v.is_valid()[1])


class TestSigning:
    def test_sign_rejects_alg_none(self):
        v = _base()
        priv, _ = Vcon.generate_key_pair()
        for alg in ("none", "None", "NONE", " none "):
            with pytest.raises(AlgorithmNotPermittedError):
                v.sign(priv, alg=alg)
        assert "signatures" not in v.vcon_dict

    def test_sign_rejects_unknown_alg(self):
        v = _base()
        priv, _ = Vcon.generate_key_pair()
        with pytest.raises(AlgorithmNotPermittedError):
            v.sign(priv, alg="HS256x")

    def test_sign_and_verify_rs256_default(self):
        v = _base()
        priv, pub = Vcon.generate_key_pair()
        v.sign(priv)
        header = json.loads(base64.urlsafe_b64decode(v.vcon_dict["signatures"][0]["protected"] + "=="))
        assert header["alg"] == "RS256"
        assert v.verify(pub) is True

    def test_verify_refuses_alg_none_in_protected_header(self):
        v = _base()
        _, pub = Vcon.generate_key_pair()
        v.vcon_dict["payload"] = _b64({"uuid": "x"})
        v.vcon_dict["signatures"] = [{"protected": _b64({"alg": "none"}), "signature": ""}]
        with pytest.raises(AlgorithmNotPermittedError):
            v.verify(pub)

    def test_verify_refuses_alg_none_in_header_object(self):
        v = _base()
        _, pub = Vcon.generate_key_pair()
        v.vcon_dict["payload"] = _b64({"uuid": "x"})
        v.vcon_dict["signatures"] = [
            {"protected": _b64({"typ": "JWS"}), "header": {"alg": "NONE"}, "signature": ""}
        ]
        with pytest.raises(AlgorithmNotPermittedError):
            v.verify(pub)

    def test_verify_fails_closed_without_alg(self):
        v = _base()
        _, pub = Vcon.generate_key_pair()
        v.vcon_dict["payload"] = _b64({"uuid": "x"})
        v.vcon_dict["signatures"] = [{"protected": _b64({"typ": "JWS"}), "signature": "AA"}]
        assert v.verify(pub) is False

    def test_verify_wrong_key_is_false(self):
        v = _base()
        priv, _ = Vcon.generate_key_pair()
        _, other = Vcon.generate_key_pair()
        v.sign(priv)
        assert v.verify(other) is False


class TestExtensionsEnforcement:
    def test_lawful_basis_in_use_must_be_listed(self):
        v = _base()
        v.vcon_dict["attachments"].append(
            {"purpose": "lawful_basis", "start": T, "party": 0, "session": [0], "body": {}, "encoding": "json", "mediatype": "application/json"}
        )
        valid, errors = v.is_valid()
        assert not valid
        assert any("Extension 'lawful_basis' is in use but is not listed" in e for e in errors)
        v.add_extension("lawful_basis")
        assert v.is_valid() == (True, [])

    def test_wtf_in_use_must_be_listed(self):
        v = _base()
        v.add_analysis(type="wtf_transcription", vendor="v", body={}, encoding="json", sessions=0)
        assert any("'wtf_transcription' is in use" in e for e in v.is_valid()[1])

    def test_critical_must_be_in_extensions(self):
        v = _base()
        v.add_critical("x_ext")
        errors = v.is_valid()[1]
        assert any("'x_ext' is listed in critical but not in extensions" in e for e in errors)
        v.add_extension("x_ext")
        assert v.is_valid() == (True, [])

    def test_non_core_values_need_some_extension(self):
        v = _base()
        v.vcon_dict["sessions"][0]["sessions"] = [{"session": 0, "type": "x-weird"}]
        assert any("outside the core vocabulary" in e for e in v.is_valid()[1])
        v.add_extension("weird")
        assert v.is_valid()[0]

    def test_nonstandard_encoding_needs_extension(self):
        v = _base()
        v.add_attachment("x", body="b", encoding="none", session=0)
        v.vcon_dict["attachments"][0]["encoding"] = "gzip"
        assert not v.is_valid()[0]

    def test_helpers_add_the_extension_name(self):
        v = _base()
        v.add_lawful_basis_attachment(
            lawful_basis="consent", expiration="2030-01-01T00:00:00Z",
            purpose_grants=[{"purpose": "recording", "granted": True, "granted_at": T}],
        )
        assert "lawful_basis" in v.get_extensions()
        assert v.is_valid() == (True, [])


class TestLawfulBasisScope:
    GRANTS = [{"purpose": "recording", "granted": True, "granted_at": T}]

    def test_attachment_carries_session_and_party(self):
        v = _base()
        v.add_lawful_basis_attachment(lawful_basis="consent", expiration="2030-01-01T00:00:00Z", purpose_grants=self.GRANTS, party_index=1)
        att = v.find_lawful_basis_attachments()[0]
        assert att["purpose"] == "lawful_basis"
        assert att["session"] == 0
        assert att["party"] == 1
        assert "dialog" not in att

    def test_no_default_scope_with_several_sessions(self):
        v = _base()
        v.add_session(Session(start=T))
        with pytest.raises(ValueError, match="dialog or session"):
            v.add_lawful_basis_attachment(lawful_basis="consent", expiration="2030-01-01T00:00:00Z", purpose_grants=self.GRANTS)
        assert v.find_lawful_basis_attachments() == []

    def test_dialog_index_alone_is_not_widened_to_a_session(self):
        # A consent record for one dialog must not silently cover the whole Session.
        v = _base()
        v.add_session(Session(start=T))
        v.add_dialog(Dialog(type="text", start=T, parties=[0], body="x", mediatype="text/plain", encoding="none"), session=1)
        v.add_lawful_basis_attachment(lawful_basis="consent", expiration="2030-01-01T00:00:00Z", purpose_grants=self.GRANTS, dialog_index=0)
        att = v.find_lawful_basis_attachments()[0]
        assert att["dialog"] == 0 and "session" not in att

    def test_explicit_session_index(self):
        v = _base()
        v.add_session(Session(start=T))
        v.add_lawful_basis_attachment(lawful_basis="consent", expiration="2030-01-01T00:00:00Z", purpose_grants=self.GRANTS, session_index=1)
        assert v.find_lawful_basis_attachments()[0]["session"] == 1

    def test_no_placeholder_session_is_invented(self):
        v = Vcon.build_new()
        v.add_party(Party(name="A"))
        with pytest.raises(ValueError, match="dialog or session"):
            v.add_lawful_basis_attachment(lawful_basis="consent", expiration="2030-01-01T00:00:00Z", purpose_grants=self.GRANTS)
        assert v.sessions == []

    def test_wtf_attachment_is_scoped_too(self):
        v = _base()
        v.add_wtf_transcription_attachment(
            transcript={"text": "hi", "language": "en", "duration": 1.0, "confidence": 0.9},
            segments=[{"id": 0, "start": 0.0, "end": 1.0, "text": "hi", "confidence": 0.9}],
            metadata={"created_at": T, "processed_at": T, "provider": "p", "model": "m"},
        )
        assert v.find_wtf_attachments()[0]["session"] == 0


class TestRedactedStrings:
    def test_every_reference_needs_an_entry(self):
        v = _base()
        v.add_dialog(Dialog(type="text", start=T, parties=[0], body="my number is __REDACTED_REF_1 ok", mediatype="text/plain", encoding="none"), session=0)
        errors = v.is_valid()[1]
        assert any("__REDACTED_REF_1 appears in the vCon but has no entry" in e for e in errors)
        v.vcon_dict["redacted_strings"] = [{"ref": 1, "type": "GOVT_ID_NUM"}]
        assert v.is_valid() == (True, [])

    def test_ref_range_and_duplicates(self):
        v = _base()
        v.vcon_dict["redacted_strings"] = [{"ref": 0}, {"ref": 2}, {"ref": 2}]
        errors = v.is_valid()[1]
        assert any("between 1 and 99999" in e for e in errors)
        assert any("duplicates ref 2" in e for e in errors)


class TestVersionHandling:
    def test_build_new_emits_0_5_0(self):
        assert Vcon.build_new().vcon == "0.5.0"

    def test_version_absent_is_accepted(self):
        v = Vcon({"uuid": "a", "created_at": T})
        assert v.is_valid()[0]

    def test_other_versions_are_not_valid(self):
        v = Vcon({"uuid": "a", "created_at": T, "vcon": "0.3.0"})
        assert not v.is_valid()[0]


class TestLegacyMediaDialogTypes:
    """audio/video: accepted on read with a warning, never written (core-05 4.5.1)."""

    @pytest.mark.parametrize("kind", ["audio", "video"])
    def test_constructor_normalizes_to_recording(self, kind):
        with pytest.warns(DeprecationWarning, match="not a core-05 type"):
            d = Dialog(type=kind, start=T, parties=[0], mediatype=f"{kind}/mp4" if kind == "video" else "audio/wav",
                       url="https://e.com/x", content_hash="sha512-x")
        assert d.to_dict()["type"] == "recording"

    def test_video_helpers_emit_recording(self):
        d = Dialog(type="recording", start=T, parties=[0])
        d.add_streaming_video_reference("ref", "video/mp4")
        assert d.type == "recording" and d.is_video()

    def test_read_is_a_warning_not_an_error(self):
        v = _base()
        v.vcon_dict["dialog"].append({"type": "video", "start": T, "parties": [0], "mediatype": "video/mp4",
                                      "url": "https://e.com/v.mp4", "content_hash": "sha512-x"})
        v.vcon_dict["sessions"][0]["dialog"] = [0]
        assert v.is_valid() == (True, [])
        assert any("type 'video'" in w for w in v.get_validation_warnings())


class TestValidationWarnings:
    def test_redundant_session_originator_warns(self):
        v = _base()
        v.vcon_dict["sessions"][0]["originator"] = 0
        assert any("originator equal to its first party" in w for w in v.get_validation_warnings())

    def test_reference_to_empty_dialog_warns(self):
        v = _base()
        v.add_dialog(Dialog.placeholder(), session=0)
        v.add_attachment("x", body="b", dialog=0, mediatype="text/plain")
        w = v.get_validation_warnings()
        assert any("lists dialog 0, which is an empty placeholder" in x for x in w)
        assert any("Attachment at index 0 references dialog 0" in x for x in w)


class TestDeprecatedApi:
    def test_redacted_and_amended_aliases(self):
        v = Vcon({"uuid": "a", "created_at": T, "redacted_from": {"uuid": "b", "type": "PII"}})
        with pytest.warns(DeprecationWarning):
            assert v.redacted == {"uuid": "b", "type": "PII"}
        with pytest.warns(DeprecationWarning):
            assert v.amended is None

    def test_add_transfer_dialog_points_at_events(self):
        with pytest.raises(NotImplementedError, match="add_event"):
            Vcon.build_new().add_transfer_dialog(start=T, transfer_data={}, parties=[0, 1])

    def test_is_transfer_is_false(self):
        with pytest.warns(DeprecationWarning):
            assert Dialog(type="text", start=T, parties=[0]).is_transfer() is False

    def test_party_history_converts_to_event(self):
        from vcon.party import PartyHistory
        with pytest.warns(DeprecationWarning):
            ph = PartyHistory(0, "keydown", T, button="5")
        assert ph.to_dict()["event"] == "keydown"
        assert ph.to_event(sessions=0).to_dict() == {"type": "keydown", "time": T, "sessions": 0, "party": 0, "button": "5"}
