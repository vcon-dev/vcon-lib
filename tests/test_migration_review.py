"""Regression tests for migration defects found in review.

Each test pins one case where the first port lost data, invented a value, or
broke a reference: the semantics here are the ones other ports copy.
"""

import json
import warnings

import pytest

from vcon import Vcon, migrate_0_4_0_to_0_5_0, MigrationError
from vcon.migration import FALLBACK, INFERRED, UNRESOLVED
from tests.test_migration_0_4_0 import v04, rec, text, migrate, T0, T1, T2


def kinds(report, kind, step=None):
    return [e for e in report.entries if e.kind == kind and (step is None or e.step == step)]


class TestAlreadyMigratedInput:
    def test_missing_vcon_with_sessions_is_refused_not_remigrated(self):
        d = {"uuid": "u", "created_at": T0, "parties": [{}, {}], "dialog": [rec()],
             "sessions": [{"start": T0, "parties": [1, 0], "dialog": [0]}],
             "events": [{"type": "join", "time": T0, "sessions": 0, "party": 0}]}
        with pytest.raises(MigrationError, match="already 0.5.0"):
            migrate_0_4_0_to_0_5_0(d)

    @pytest.mark.parametrize("key", ["redacted_from", "amended_from", "redacted_strings"])
    def test_missing_vcon_with_other_050_only_keys_is_refused(self, key):
        d = {"uuid": "u", "created_at": T0, key: {"uuid": "x"} if key != "redacted_strings" else []}
        with pytest.raises(MigrationError, match="already 0.5.0"):
            migrate_0_4_0_to_0_5_0(d)

    def test_missing_vcon_plain_040_shape_still_migrates(self):
        d = v04(dialog=[rec()])
        del d["vcon"]
        out, _ = migrate(d)
        assert out["vcon"] == "0.5.0" and out["sessions"][0]["dialog"] == [0]


class TestRecordingSets:
    def test_back_reference_only_membership_is_kept(self):
        # recording names the set, set has no recordings list (core-04: recording_set SHOULD, recordings MUST)
        out, report = migrate(v04(dialog=[rec(recording_set=1), {"type": "recording-set", "start": T0}]))
        assert out["sessions"][1]["dialog"] == [0]
        assert any("recording_set" in e.message for e in kinds(report, INFERRED, "T7"))

    def test_back_reference_merged_with_partial_recordings_list(self):
        out, _ = migrate(v04(dialog=[rec(recording_set=2), rec(recording_set=2),
                                     {"type": "recording-set", "start": T0, "recordings": [0]}]))
        assert out["sessions"][1]["dialog"] == [0, 1]

    def test_recording_set_pointing_nowhere_is_reported(self):
        _, report = migrate(v04(dialog=[rec(recording_set=5)]))
        assert any("recording_set=5" in e.message for e in kinds(report, UNRESOLVED, "T7"))

    def test_nested_recording_set_becomes_child_reference(self):
        out, _ = migrate(v04(dialog=[rec(), rec(),
                                     {"type": "recording-set", "recordings": [0, 1]},
                                     {"type": "recording-set", "recordings": [2]}]))
        # Session 1 <- dialog[2], Session 2 <- dialog[3]
        assert out["sessions"][2]["sessions"] == [{"session": 1, "type": "child"}]
        assert out["sessions"][1]["dialog"] == [0, 1]

    def test_nested_forward_reference_resolves(self):
        out, _ = migrate(v04(dialog=[rec(), {"type": "recording-set", "recordings": [2]},
                                     {"type": "recording-set", "recordings": [0]}]))
        assert out["sessions"][1]["sessions"] == [{"session": 2, "type": "child"}]
        assert out["sessions"][2]["dialog"] == [0]

    def test_unmapped_recording_set_fields_are_reported_with_values(self):
        _, report = migrate(v04(dialog=[rec(recording_set=1), {
            "type": "recording-set", "recordings": [0], "application": "pbx", "meta": {"k": 1}}]))
        e = [x for x in kinds(report, UNRESOLVED, "T7") if "no Session equivalent" in x.message]
        assert e and e[0].details["dropped"] == {"application": "pbx", "meta": {"k": 1}}


class TestTransfers:
    def test_transfer_originator_is_reported(self):
        _, report = migrate(v04(dialog=[rec(), {"type": "transfer", "transferee": 0, "transferor": 1,
                                                "transfer_target": 2, "original": 0, "start": T1,
                                                "originator": 1}]))
        e = [x for x in kinds(report, UNRESOLVED, "T4") if "no Event equivalent" in x.message]
        assert e and e[0].details["dropped"]["originator"] == 1

    def test_party_history_events_include_transfer_role_session(self):
        # dialog[0] is in a recording-set and is the transfer's original call
        out, _ = migrate(v04(dialog=[
            rec(recording_set=1, party_history=[{"party": 0, "time": T0, "event": "join"}]),
            {"type": "recording-set", "recordings": [0]},
            {"type": "transfer", "transferee": 0, "transferor": 1, "transfer_target": 2,
             "original": 0, "start": T1},
        ]))
        sessions_of_0 = [n for n, s in enumerate(out["sessions"]) if 0 in s.get("dialog", [])]
        join = [e for e in out["events"] if e["type"] == "join"][0]
        assert sorted(join["sessions"]) == sorted(sessions_of_0)
        assert len(sessions_of_0) == 3

    def test_transfer_whose_original_is_recording_set_uses_its_session(self):
        out, _ = migrate(v04(dialog=[rec(recording_set=1), {"type": "recording-set", "recordings": [0]},
                                     {"type": "transfer", "transferee": 0, "transferor": 1,
                                      "transfer_target": 2, "original": 1, "target_dialog": 3, "start": T1},
                                     rec(parties=[0, 2], start=T2)]))
        ev = out["events"][0]
        assert ev["sessions"] == 1 and out["sessions"][1]["dialog"] == [0]
        assert out["sessions"][ev["target_session"]]["dialog"] == [3]


class TestPartyHistory:
    def test_unparseable_time_is_kept_in_the_report(self):
        _, report = migrate(v04(dialog=[rec(party_history=[{"party": 0, "time": "yesterday-ish", "event": "join"}])]))
        fb = kinds(report, FALLBACK, "T3")
        assert fb and fb[0].details["original_time"] == "yesterday-ish"

    def test_no_time_and_no_dialog_start_falls_back_to_created_at(self):
        d = rec(party_history=[{"party": 0, "event": "join"}])
        del d["start"]
        out, report = migrate(v04(dialog=[d]))
        assert out["events"][0]["time"] == "2022-06-21T13:53:00-04:00"
        assert kinds(report, FALLBACK, "T3")[0].details["source"] == "vCon created_at"

    def test_no_time_strict_raises(self):
        d = rec(party_history=[{"party": 0, "event": "join"}])
        del d["start"]
        with pytest.raises(MigrationError):
            migrate_0_4_0_to_0_5_0(v04(dialog=[d]), strict=True)

    def test_extension_parameters_are_carried_not_dropped(self):
        out, report = migrate(v04(dialog=[rec(party_history=[
            {"party": 0, "time": T0, "event": "join", "x_reason": "callback", "channel": 3}])]))
        ev = out["events"][0]
        assert ev["x_reason"] == "callback" and "channel" not in ev
        e = [x for x in kinds(report, UNRESOLVED, "T3") if "non-core" in x.message][0]
        assert e.details["dropped"] == {"channel": 3}

    def test_party_history_on_text_and_incomplete(self):
        out, _ = migrate(v04(dialog=[
            text(parties=[0, 1, 2], party_history=[{"party": 1, "time": T1, "event": "join"}]),
            {"type": "incomplete", "start": T2, "parties": [1, 0], "disposition": "busy",
             "party_history": [{"party": 1, "time": T2, "event": "drop"}]},
        ]))
        assert [e["type"] for e in out["events"]] == ["join", "drop"]
        assert all(e["sessions"] == 0 and "dialog" not in e for e in out["events"])
        assert all("party_history" not in d for d in out["dialog"])


class TestNullFirstParty:
    def test_text_with_null_sender_does_not_promote_a_receiver(self):
        out, report = migrate(v04(dialog=[text(parties=[None, 1, 2])]))
        sender = out["dialog"][0]["parties"][0]
        assert sender not in (1, 2)
        assert out["parties"][sender] == {}
        s = out["sessions"][0]
        assert s["parties"][0] == sender or s.get("originator") == sender
        assert any("null" in e.message for e in kinds(report, UNRESOLVED, "T8"))

    def test_incomplete_with_null_originator_does_not_promote(self):
        out, _ = migrate(v04(dialog=[{"type": "incomplete", "start": T0, "parties": [None, 2],
                                      "disposition": "no-answer"}]))
        who = out["dialog"][0]["parties"][0]
        assert who != 2 and out["parties"][who] == {}

    def test_recording_null_channel_is_kept(self):
        out, _ = migrate(v04(dialog=[rec(parties=[None, 1])]))
        assert out["dialog"][0]["parties"] == [None, 1]


class TestOriginator:
    def test_originator_not_first_moves_to_session(self):
        out, _ = migrate(v04(dialog=[text(parties=[0, 1, 2], originator=2)]))
        assert out["dialog"][0]["parties"] == [2]
        assert out["sessions"][0]["parties"] == [0, 1, 2]
        assert out["sessions"][0]["originator"] == 2


class TestUnscopedAttachments:
    def att(self, **kw):
        a = {"purpose": "note", "start": T0, "party": 0, "body": "x", "encoding": "none", "mediatype": "text/plain"}
        a.update(kw)
        return a

    def test_single_session_scope_is_inferred_and_reported(self):
        out, report = migrate(v04(dialog=[rec()], attachments=[self.att()]))
        assert out["attachments"][0]["session"] == 0
        assert kinds(report, INFERRED, "T10c")

    def test_several_sessions_leave_it_unresolved(self):
        out, report = migrate_0_4_0_to_0_5_0(
            v04(dialog=[rec(recording_set=1), {"type": "recording-set", "recordings": [0]}],
                attachments=[self.att()]))
        assert "session" not in out["attachments"][0] and "dialog" not in out["attachments"][0]
        assert kinds(report, UNRESOLVED, "T10c")

    def test_lawful_basis_keeps_dialog_only(self):
        lb = self.att(purpose="lawful_basis", dialog=0, body={}, encoding="json", mediatype="application/json")
        out, _ = migrate(v04(dialog=[rec()], attachments=[lb]))
        assert out["attachments"][0]["dialog"] == 0 and "session" not in out["attachments"][0]
