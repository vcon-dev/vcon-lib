"""Migration of a 0.4.0 vCon to 0.5.0 (Appendix A.1, steps T1 to T15)."""

import base64
import copy
import json
from pathlib import Path

import pytest

from vcon import (
    Vcon,
    migrate_0_4_0_to_0_5_0,
    MigrationError,
    MigrationReport,
)
from vcon.migration import MIGRATION_STEPS, FALLBACK, INFERRED, UNRESOLVED

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

SCHEMA = json.loads((Path(__file__).parent / "schema" / "vcon_json_schema.json").read_text())

T0 = "2022-06-21T17:53:26.000+00:00"
T1 = "2022-06-21T17:54:00.000+00:00"
T2 = "2022-06-21T17:55:00.000+00:00"


def v04(**kw):
    """A 0.4.0 vCon with three parties and the given extra top-level members."""
    d = {
        "vcon": "0.4.0",
        "uuid": "01a16b86-9a63-8346-b9a2-279e0d16bc46",
        "created_at": "2022-06-21T13:53:00-04:00",
        "parties": [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"}],
        "dialog": [],
        "analysis": [],
        "attachments": [],
    }
    d.update(kw)
    return d


def rec(**kw):
    d = {"type": "recording", "start": T0, "duration": 10, "parties": [0, 1],
         "mediatype": "audio/x-wav", "url": "https://e.com/a.wav", "content_hash": "sha512-x"}
    d.update(kw)
    return d


def text(**kw):
    d = {"type": "text", "start": T1, "parties": [0, 1], "body": "hi", "encoding": "none", "mediatype": "text/plain"}
    d.update(kw)
    return d


def check_schema(vcon):
    if jsonschema:
        jsonschema.Draft7Validator(SCHEMA).validate(vcon)


def migrate(d, **kw):
    out, report = migrate_0_4_0_to_0_5_0(d, **kw)
    check_schema(out)
    return out, report


class TestTableDriven:
    def test_one_entry_per_transform_step(self):
        ids = [s.id for s in MIGRATION_STEPS]
        assert sorted(ids) == sorted(
            ["T1", "T2", "T3", "T4", "T6", "T7", "T8", "T9", "T9b", "T10", "T11", "T12", "T13", "T14", "T15", "T10b"]
        )
        assert len(ids) == len(set(ids))
        assert all(s.source and s.title and callable(s.func) for s in MIGRATION_STEPS)

    def test_steps_run_in_the_documented_order(self):
        _, report = migrate(v04())
        assert report.steps_run == [s.id for s in MIGRATION_STEPS]
        order = report.steps_run
        # reads of the original dialog array precede the in-place blanking
        for step in ("T8", "T9", "T9b", "T6", "T2", "T7", "T3", "T4"):
            assert order.index(step) < order.index("T10")

    def test_input_is_not_modified(self):
        d = v04(dialog=[rec(originator=1, party_history=[{"party": 0, "time": T0, "event": "join"}])])
        before = copy.deepcopy(d)
        migrate_0_4_0_to_0_5_0(d)
        assert d == before

    def test_accepts_json_string(self):
        out, _ = migrate_0_4_0_to_0_5_0(json.dumps(v04(dialog=[rec()])))
        assert out["vcon"] == "0.5.0"

    def test_rejects_other_versions_and_garbage(self):
        with pytest.raises(MigrationError, match="expected '0.4.0'"):
            migrate_0_4_0_to_0_5_0({"vcon": "0.5.0", "uuid": "a", "created_at": "2022-01-01T00:00:00Z"})
        with pytest.raises(MigrationError):
            migrate_0_4_0_to_0_5_0("not json")
        with pytest.raises(MigrationError):
            migrate_0_4_0_to_0_5_0([1])


class TestT1Version:
    def test_vcon_parameter(self):
        out, report = migrate(v04())
        assert out["vcon"] == "0.5.0"

    def test_missing_version_is_set_and_reported(self):
        d = v04()
        del d["vcon"]
        out, report = migrate_0_4_0_to_0_5_0(d)
        assert out["vcon"] == "0.5.0"
        assert any(e.code == "AMB-12" for e in report.inferred)


class TestT2Session:
    def test_one_session_references_all_dialogs(self):
        out, _ = migrate(v04(dialog=[rec(), text()]))
        assert len(out["sessions"]) == 1
        assert out["sessions"][0]["dialog"] == [0, 1]

    def test_simple_call_matches_the_appendix_b_shape(self):
        out, _ = migrate(v04(dialog=[rec(parties=[0, 1])]))
        assert out["sessions"] == [{"start": T0, "duration": 10, "parties": [0, 1], "dialog": [0]}]

    def test_no_dialog_means_no_session(self):
        out, _ = migrate(v04())
        assert "sessions" not in out and "events" not in out

    def test_removed_positions_are_skipped_in_the_dialog_list(self):
        out, _ = migrate(v04(dialog=[rec(), {"type": "recording-set", "recordings": [0], "start": T0}, text()]))
        assert out["sessions"][0]["dialog"] == [0, 2]

    def test_session_start_and_duration_are_derived_and_reported(self):
        d = v04(dialog=[rec(), text(duration=5)])
        out, report = migrate(d)
        assert out["sessions"][0]["start"] == T0
        assert out["sessions"][0]["duration"] == 39  # T0 .. (T1 + 5s) = 34s + 5s
        assert any("start/duration derived" in e.message for e in report.inferred)

    def test_text_only_session_has_no_duration(self):
        out, _ = migrate(v04(dialog=[text()]))
        assert "duration" not in out["sessions"][0]


class TestT3PartyHistory:
    HISTORY = [
        {"party": 0, "time": T0, "event": "join"},
        {"party": 1, "time": T0, "event": "join"},
        {"party": 1, "time": T1, "event": "hold"},
        {"party": 0, "time": T1, "event": "drop"},
    ]

    def test_entries_become_events_with_event_renamed_type(self):
        out, _ = migrate(v04(dialog=[rec(party_history=self.HISTORY)]))
        assert out["events"] == [
            {"type": "join", "time": T0, "sessions": 0, "party": 0},
            {"type": "join", "time": T0, "sessions": 0, "party": 1},
            {"type": "hold", "time": T1, "sessions": 0, "party": 1},
            {"type": "drop", "time": T1, "sessions": 0, "party": 0},
        ]
        assert "party_history" not in out["dialog"][0]

    def test_events_do_not_reference_the_dialog(self):
        out, _ = migrate(v04(dialog=[rec(party_history=self.HISTORY)]))
        assert all("dialog" not in e for e in out["events"])

    def test_button_survives_on_key_events(self):
        out, _ = migrate(v04(dialog=[rec(party_history=[{"party": 0, "time": T0, "event": "keydown", "button": "5"}])]))
        assert out["events"][0] == {"type": "keydown", "time": T0, "sessions": 0, "party": 0, "button": "5"}

    def test_dialog_in_two_sessions_lists_both(self):
        d = v04(dialog=[rec(party_history=self.HISTORY[:1]), {"type": "recording-set", "recordings": [0], "start": T0}])
        out, report = migrate(d)
        assert out["events"][0]["sessions"] == [0, 1]
        assert any(e.code == "AMB-3" for e in report.inferred)

    def test_missing_party_uses_empty_party_object_or_raises_in_strict(self):
        d = v04(dialog=[rec(party_history=[{"time": T0, "event": "join"}])])
        out, report = migrate_0_4_0_to_0_5_0(d)
        assert out["parties"][out["events"][0]["party"]] == {}
        assert report.fallbacks
        with pytest.raises(MigrationError, match="no party"):
            migrate_0_4_0_to_0_5_0(d, strict=True)

    def test_missing_time_falls_back_to_dialog_start(self):
        d = v04(dialog=[rec(party_history=[{"party": 0, "event": "join"}])])
        out, report = migrate_0_4_0_to_0_5_0(d)
        assert out["events"][0]["time"] == T0
        assert report.fallbacks
        with pytest.raises(MigrationError):
            migrate_0_4_0_to_0_5_0(d, strict=True)


class TestT4TransferToEvents:
    def base(self, transfer):
        return v04(dialog=[
            rec(),                                   # 0 original call
            rec(start=T1, parties=[1, 2]),           # 1 consultation call
            rec(start=T2, parties=[0, 2]),           # 2 target call
            transfer,                                # 3 transfer dialog
        ])

    def test_blind_transfer(self):
        d = self.base({"type": "transfer", "start": T2, "transferee": 0, "transferor": 1,
                       "transfer_target": 2, "original": 0, "target_dialog": 2})
        out, report = migrate(d)
        assert [e["type"] for e in out["events"]] == ["blind-transfer"]
        e = out["events"][0]
        assert e["party"] == 1 and e["transferee"] == 0 and e["transfer_target"] == 2
        assert e["time"] == T2
        assert "consultation" not in e
        # original / target are Sessions that list the right Dialogs
        assert out["sessions"][e["sessions"]]["dialog"] == [0]
        assert out["sessions"][e["target_session"]]["dialog"] == [2]
        assert out["dialog"][3] == {}
        assert 3 not in [i for s in out["sessions"] for i in s.get("dialog", [])]

    def test_consultative_transfer_emits_two_events_sharing_the_consultation_session(self):
        d = self.base({"type": "transfer", "start": T2, "transferee": 0, "transferor": 1,
                       "transfer_target": 2, "original": 0, "consultation": 1, "target_dialog": 2})
        out, _ = migrate(d)
        assert [e["type"] for e in out["events"]] == ["consultation-start", "consultative-transfer"]
        cs, ct = out["events"]
        assert cs["consultation"] == ct["consultation"]
        assert out["sessions"][cs["consultation"]]["dialog"] == [1]
        assert out["sessions"][ct["target_session"]]["dialog"] == [2]
        assert cs["sessions"] == ct["sessions"]
        assert "target_session" not in cs
        assert ct["party"] == cs["party"] == 1  # transferor becomes party

    def test_transfer_to_recording_set_reuses_its_session(self):
        d = v04(dialog=[
            rec(), rec(start=T2),
            {"type": "recording-set", "start": T0, "recordings": [0], "parties": [0, 1]},
            {"type": "transfer", "start": T2, "transferee": 0, "transferor": 1, "transfer_target": 2,
             "original": 2, "target_dialog": 1},
        ])
        out, _ = migrate(d)
        e = out["events"][0]
        assert out["sessions"][e["sessions"]]["dialog"] == [0]
        assert e["sessions"] == 1  # the recording-set's Session

    def test_time_from_other_source_is_reported(self):
        d = self.base({"type": "transfer", "transferee": 0, "transferor": 1, "transfer_target": 2,
                       "original": 0, "target_dialog": 2})
        out, report = migrate(d)
        assert out["events"][0]["time"] == T2
        entries = [e for e in report.inferred if e.code == "AMB-7" and "Event time taken from" in e.message]
        assert entries and "target dialog[2]" in entries[0].message

    def test_consultation_time_comes_from_consultation_call(self):
        d = self.base({"type": "transfer", "transferee": 0, "transferor": 1, "transfer_target": 2,
                       "original": 0, "consultation": 1, "target_dialog": 2})
        out, report = migrate(d)
        assert out["events"][0]["time"] == T1   # consultation-start: start of consultation call
        assert out["events"][1]["time"] == T2   # transfer: start of target call
        assert len([e for e in report.inferred if "Event time taken from" in e.message]) == 2

    def test_no_time_source_falls_back_to_created_at_or_raises(self):
        d = v04(dialog=[rec(), {"type": "transfer", "transferee": 0, "transferor": 1, "transfer_target": 2,
                                "original": 0}])
        out, report = migrate_0_4_0_to_0_5_0(d)
        assert out["events"][0]["time"] == d["created_at"]
        assert any("created_at" in e.message for e in report.fallbacks)
        with pytest.raises(MigrationError, match="no start and no other time source"):
            migrate_0_4_0_to_0_5_0(d, strict=True)

    def test_no_time_and_no_created_at_always_raises(self):
        d = v04(dialog=[rec(), {"type": "transfer", "transferee": 0, "transferor": 1, "transfer_target": 2, "original": 0}])
        del d["created_at"]
        with pytest.raises(MigrationError, match="no time can be sourced"):
            migrate_0_4_0_to_0_5_0(d)

    def test_abandoned_transfer(self):
        d = self.base({"type": "transfer", "start": T2, "transferee": 0, "transferor": 1, "original": 0})
        out, report = migrate(d)
        e = out["events"][0]
        assert e["type"] == "transfer-abandoned"
        assert "transfer_target" not in e and "target_session" not in e
        assert any(x.code == "AMB-7" for x in report.inferred)

    def test_target_not_captured_gets_placeholder_session(self):
        d = self.base({"type": "transfer", "start": T2, "transferee": 0, "transferor": 1,
                       "transfer_target": 2, "original": 0})
        out, report = migrate(d)
        e = out["events"][0]
        assert e["type"] == "blind-transfer"
        assert out["sessions"][e["target_session"]] == {}
        assert any("placeholder Session" in x.message for x in report.inferred)

    def test_missing_transferor_uses_empty_party_or_raises_in_strict(self):
        t = {"type": "transfer", "start": T2, "transferee": 0, "transfer_target": 2, "original": 0, "target_dialog": 2}
        out, report = migrate_0_4_0_to_0_5_0(self.base(t))
        assert out["parties"][out["events"][0]["party"]] == {}
        assert report.fallbacks
        with pytest.raises(MigrationError, match="no transferor"):
            migrate_0_4_0_to_0_5_0(self.base(t), strict=True)

    def test_missing_original_gets_placeholder_session_or_raises(self):
        t = {"type": "transfer", "start": T2, "transferee": 0, "transferor": 1, "transfer_target": 2, "target_dialog": 2}
        out, report = migrate_0_4_0_to_0_5_0(self.base(t))
        assert out["sessions"][out["events"][0]["sessions"]] == {}
        assert report.fallbacks
        with pytest.raises(MigrationError):
            migrate_0_4_0_to_0_5_0(self.base(t), strict=True)

    def test_unmapped_transfer_content_is_kept_in_the_report(self):
        t = {"type": "transfer", "start": T2, "transferee": 0, "transferor": 1, "transfer_target": 2,
             "original": 0, "target_dialog": 2, "transfer": {"reason": "forwarded"}}
        out, report = migrate_0_4_0_to_0_5_0(self.base(t))
        assert report.removed_dialogs[3]["transfer"] == {"reason": "forwarded"}
        assert any("no Event equivalent" in e.message for e in report.unresolved)

    def test_events_pass_the_parameter_table(self):
        t = {"type": "transfer", "start": T2, "transferee": 0, "transferor": 1, "transfer_target": 2,
             "original": 0, "consultation": 1, "target_dialog": 2}
        out, report = migrate(self.base(t))
        assert not report.unresolved
        assert Vcon(out).is_valid() == (True, [])


class TestT6Originator:
    def test_originator_moves_to_the_session_when_not_first_party(self):
        out, _ = migrate(v04(dialog=[rec(parties=[0, 1], originator=1)]))
        assert out["sessions"][0]["originator"] == 1
        assert "originator" not in out["dialog"][0]

    def test_originator_dropped_when_it_is_the_first_party(self):
        out, _ = migrate(v04(dialog=[rec(parties=[0, 1], originator=0)]))
        assert "originator" not in out["sessions"][0]
        assert "originator" not in out["dialog"][0]

    def test_conflicting_originators_are_reported(self):
        d = v04(dialog=[rec(parties=[0, 1, 2], originator=1), text(parties=[0, 1, 2], originator=2)])
        out, report = migrate(d)
        assert out["sessions"][0]["originator"] == 1
        assert any("different originators" in e.message for e in report.unresolved)


class TestT7RecordingSet:
    def d(self):
        return v04(dialog=[
            rec(recording_set=2, start=T0, duration=4, parties=[0, 1]),
            rec(recording_set=2, start=T0, duration=6, parties=[1, 0]),
            {"type": "recording-set", "start": T0, "duration": 7, "parties": [0, 1], "originator": 1,
             "session_id": {"local": "l", "remote": "r"}, "recordings": [0, 1]},
        ])

    def test_recording_set_becomes_a_session(self):
        out, report = migrate(self.d())
        s = out["sessions"][1]
        assert s["dialog"] == [0, 1]
        assert s["start"] == T0 and s["duration"] == 7 and s["parties"] == [0, 1]
        assert s["originator"] == 1
        assert s["session_id"] == {"local": "l", "remote": "r"}
        assert any(e.code == "AMB-4" for e in report.inferred)
        assert any(e.code == "AMB-1" for e in report.unresolved)

    def test_recording_set_parameter_is_removed_from_recordings(self):
        out, _ = migrate(self.d())
        assert all("recording_set" not in x for x in out["dialog"][:2])

    def test_recording_set_dialog_is_blanked_and_unlisted(self):
        out, report = migrate(self.d())
        assert out["dialog"][2] == {}
        assert report.removed_dialogs[2]["type"] == "recording-set"
        assert all(2 not in s.get("dialog", []) for s in out["sessions"])


class TestT8T9Parties:
    def test_text_dialog_parties_reduce_to_sender_receivers_go_to_session(self):
        out, _ = migrate(v04(dialog=[text(parties=[0, 1, 2])]))
        assert out["dialog"][0]["parties"] == [0]
        assert out["sessions"][0]["parties"] == [0, 1, 2]

    def test_sender_is_the_originator_when_set(self):
        out, _ = migrate(v04(dialog=[text(parties=[0, 1, 2], originator=2)]))
        assert out["dialog"][0]["parties"] == [2]
        assert out["sessions"][0]["parties"] == [0, 1, 2]
        assert out["sessions"][0]["originator"] == 2

    def test_thread_with_different_receivers_is_reported_not_split(self):
        d = v04(dialog=[text(parties=[0, 1]), text(parties=[1, 0, 2])])
        out, report = migrate(d)
        assert len(out["sessions"]) == 1
        assert [x["parties"] for x in out["dialog"]] == [[0], [1]]
        assert out["sessions"][0]["parties"] == [0, 1, 2]
        assert sum(1 for e in report.unresolved if e.code == "AMB-5") >= 1

    def test_incomplete_dialog_parties_reduce_to_originator_or_first(self):
        inc = {"type": "incomplete", "start": T0, "parties": [2, 0], "disposition": "no-answer"}
        out, _ = migrate(v04(dialog=[inc]))
        assert out["dialog"][0]["parties"] == [2]
        assert out["sessions"][0]["parties"] == [2, 0]
        inc2 = dict(inc, originator=0)
        out2, _ = migrate(v04(dialog=[inc2]))
        assert out2["dialog"][0]["parties"] == [0]
        assert out2["sessions"][0]["originator"] == 0

    def test_recording_parties_are_kept_and_unioned_into_the_session(self):
        out, report = migrate(v04(dialog=[rec(parties=[0, 1]), rec(parties=[1, 2])]))
        assert [x["parties"] for x in out["dialog"]] == [[0, 1], [1, 2]]
        assert out["sessions"][0]["parties"] == [0, 1, 2]
        assert any(e.code == "AMB-6" for e in report.inferred)

    def test_text_without_parties_is_reported(self):
        t = text()
        del t["parties"]
        _, report = migrate_0_4_0_to_0_5_0(v04(dialog=[t]))
        assert any("has no parties" in e.message for e in report.unresolved)


class TestT10EmptyDialogsAndAMB2:
    def test_removed_dialogs_become_empty_objects_in_place(self):
        d = v04(dialog=[
            rec(),
            {"type": "transfer", "start": T1, "transferee": 0, "transferor": 1, "transfer_target": 2, "original": 0, "target_dialog": 3},
            text(),
            rec(start=T2),
        ])
        out, report = migrate(d)
        assert len(out["dialog"]) == 4
        assert out["dialog"][1] == {}
        assert out["dialog"][2]["type"] == "text" and out["dialog"][3]["start"] == T2
        assert set(report.removed_dialogs) == {1}

    def test_analysis_on_recording_set_is_repointed(self):
        d = v04(
            dialog=[rec(recording_set=1), {"type": "recording-set", "start": T0, "recordings": [0]}],
            analysis=[{"type": "summary", "dialog": 1, "vendor": "v", "body": "s", "encoding": "none"}],
        )
        out, report = migrate(d)
        a = out["analysis"][0]
        assert a["dialog"] == 0 and a["sessions"] == 1
        assert any(e.code == "AMB-2" for e in report.inferred)

    def test_analysis_dialog_list_is_expanded(self):
        d = v04(
            dialog=[rec(recording_set=2), rec(), {"type": "recording-set", "start": T0, "recordings": [0]}],
            analysis=[{"type": "summary", "dialog": [1, 2], "vendor": "v", "body": "s", "encoding": "none"}],
        )
        out, _ = migrate(d)
        assert out["analysis"][0]["dialog"] == [1, 0]
        assert out["analysis"][0]["sessions"] == 1

    def test_attachment_on_removed_dialog_gets_session(self):
        d = v04(
            dialog=[rec(recording_set=1), {"type": "recording-set", "start": T0, "recordings": [0]}],
            attachments=[{"purpose": "notes", "start": T0, "party": 0, "dialog": 1, "body": "n", "encoding": "none", "mediatype": "text/plain"}],
        )
        out, _ = migrate(d)
        att = out["attachments"][0]
        assert "dialog" not in att and att["session"] == 1

    def test_analysis_on_transfer_dialog_goes_to_the_original_session(self):
        d = v04(
            dialog=[rec(), {"type": "transfer", "start": T1, "transferee": 0, "transferor": 1,
                            "transfer_target": 2, "original": 0, "target_dialog": 0}],
            analysis=[{"type": "report", "dialog": 1, "vendor": "v", "body": "why", "encoding": "none"}],
        )
        out, _ = migrate(d)
        a = out["analysis"][0]
        assert "dialog" not in a
        assert a["sessions"] == out["events"][0]["sessions"]

    def test_references_to_kept_dialogs_are_untouched(self):
        d = v04(
            dialog=[rec(), text()],
            analysis=[{"type": "summary", "dialog": [0, 1], "vendor": "v", "body": "s", "encoding": "none"}],
            attachments=[{"purpose": "notes", "start": T0, "party": 0, "dialog": 1, "body": "n", "encoding": "none", "mediatype": "text/plain"}],
        )
        out, report = migrate(d)
        assert out["analysis"][0]["dialog"] == [0, 1] and "sessions" not in out["analysis"][0]
        assert out["attachments"][0]["dialog"] == 1
        assert not [e for e in report.entries if e.step == "T10b"]


class TestIndexStability:
    """Code that drops empty Dialogs before indexing must not break references."""

    IDENT = ("type", "start", "duration", "mediatype", "body", "url", "disposition")

    def source(self):
        return v04(
            dialog=[
                rec(),                                                                  # 0
                {"type": "recording-set", "start": T0, "recordings": [0, 3], "parties": [0, 1]},  # 1
                {"type": "transfer", "start": T1, "transferee": 0, "transferor": 1,
                 "transfer_target": 2, "original": 1, "consultation": 4, "target_dialog": 3},     # 2
                rec(start=T2, parties=[0, 2], party_history=[{"party": 2, "time": T2, "event": "join"}]),  # 3
                text(parties=[1, 2]),                                                   # 4
                {"type": "incomplete", "start": T2, "parties": [2, 0], "disposition": "busy"},    # 5
            ],
            analysis=[
                {"type": "a0", "dialog": 0, "vendor": "v", "body": "x", "encoding": "none"},
                {"type": "a3", "dialog": [3, 4], "vendor": "v", "body": "x", "encoding": "none"},
                {"type": "a5", "dialog": 5, "vendor": "v", "body": "x", "encoding": "none"},
            ],
            attachments=[
                {"purpose": "p4", "start": T0, "party": 0, "dialog": 4, "body": "x", "encoding": "none", "mediatype": "text/plain"},
                {"purpose": "p5", "start": T0, "party": 0, "dialog": 5, "body": "x", "encoding": "none", "mediatype": "text/plain"},
            ],
        )

    def ident(self, d):
        return {k: d[k] for k in self.IDENT if k in d}

    def test_dialog_array_length_and_positions_do_not_change(self):
        src = self.source()
        out, report = migrate(src)
        assert len(out["dialog"]) == len(src["dialog"])
        removed = set(report.removed_dialogs)
        assert removed == {1, 2}
        for i, (a, b) in enumerate(zip(src["dialog"], out["dialog"])):
            if i in removed:
                assert b == {}
            else:
                assert self.ident(b) == self.ident(a), i

    def test_analysis_and_attachment_references_resolve_to_the_same_dialog(self):
        src = self.source()
        out, _ = migrate(src)
        for a_src, a_out in zip(src["analysis"], out["analysis"]):
            before = a_src["dialog"] if isinstance(a_src["dialog"], list) else [a_src["dialog"]]
            after = a_out.get("dialog")
            after = [] if after is None else (after if isinstance(after, list) else [after])
            for i in before:
                if src["dialog"][i]["type"] in ("transfer", "recording-set"):
                    continue
                assert i in after
                assert self.ident(out["dialog"][i]) == self.ident(src["dialog"][i])
            assert all(out["dialog"][i] != {} for i in after)
        for t_src, t_out in zip(src["attachments"], out["attachments"]):
            i = t_src["dialog"]
            assert t_out["dialog"] == i
            assert self.ident(out["dialog"][i]) == self.ident(src["dialog"][i])

    def test_session_and_event_references_resolve_to_the_intended_dialogs(self):
        src = self.source()
        out, _ = migrate(src)
        # Every Session lists only non-empty Dialogs, found by absolute index.
        for s in out["sessions"]:
            for i in s.get("dialog", []):
                assert out["dialog"][i] != {}
        # party_history of dialog 3 became an event whose Session lists dialog 3.
        join = next(e for e in out["events"] if e["type"] == "join")
        sessions = join["sessions"] if isinstance(join["sessions"], list) else [join["sessions"]]
        assert any(3 in out["sessions"][n]["dialog"] for n in sessions)
        # Transfer events: original = recording-set Session (recordings 0 and 3), target = dialog 3,
        # consultation = dialog 4.
        by_type = {e["type"]: e for e in out["events"] if e["type"] != "join"}
        assert out["sessions"][by_type["consultative-transfer"]["sessions"]]["dialog"] == [0, 3]
        assert out["sessions"][by_type["consultative-transfer"]["target_session"]]["dialog"] == [3]
        assert out["sessions"][by_type["consultation-start"]["consultation"]]["dialog"] == [4]

    def test_filtering_empty_dialogs_first_would_have_broken_the_references(self):
        """This is why the empty placeholders exist: the naive filtered list shifts every later index."""
        src = self.source()
        out, _ = migrate(src)
        filtered = [d for d in out["dialog"] if d]
        # Positions after the first removed Dialog move, so absolute indices in
        # Sessions, Events, analysis and attachments no longer line up.
        assert filtered[3]["type"] != out["dialog"][3]["type"] or filtered[1] != out["dialog"][1]
        # The migrated array itself is positionally correct for every reference.
        assert out["dialog"][4]["type"] == "text" and out["dialog"][5]["type"] == "incomplete"
        for s in out["sessions"]:
            for i in s.get("dialog", []):
                assert i < len(out["dialog"])

    def test_every_reference_in_the_result_resolves(self):
        out, report = migrate(self.source())
        assert Vcon(out).is_valid() == (True, [])
        assert not [e for e in report.unresolved if e.step == "post"]


class TestT11T12Renames:
    def test_redacted_to_redacted_from(self):
        r = {"uuid": "01a16b86-96e7-80a8-b9a2-279e0d16bc46", "type": "PII Redaction", "url": "https://e.com/u", "content_hash": "sha512-x"}
        out, _ = migrate(v04(redacted=r))
        assert out["redacted_from"] == r and "redacted" not in out

    def test_amended_to_amended_from(self):
        a = {"uuid": "01a16b86-96e7-80a8-b9a2-279e0d16bc46"}
        out, _ = migrate(v04(amended=a))
        assert out["amended_from"] == a and "amended" not in out

    def test_rename_keeps_position(self):
        out, _ = migrate(v04(amended={"uuid": "x"}))
        keys = list(out)
        assert keys.index("amended_from") == list(v04(amended={"uuid": "x"})).index("amended")


class TestT13SignedInput:
    def signed(self, payload, alg="RS256"):
        b = lambda o: base64.urlsafe_b64encode(json.dumps(o).encode()).rstrip(b"=").decode()
        return {"payload": b(payload), "signatures": [{"protected": b({"alg": alg}), "header": {"uuid": "x"}, "signature": "AAAA"}]}

    def test_signed_input_is_migrated_as_the_unsigned_payload(self):
        out, report = migrate(self.signed(v04(dialog=[rec()])))
        assert "signatures" not in out and "payload" not in out
        assert out["vcon"] == "0.5.0" and out["sessions"]
        assert report.resign_required is True
        assert any("Re-signing is required" in e.message for e in report.unresolved)

    def test_alg_none_is_called_out(self):
        _, report = migrate(self.signed(v04(), alg="none"))
        assert any("alg 'none'" in e.message for e in report.unresolved)

    def test_unsigned_input_does_not_require_resigning(self):
        assert migrate(v04())[1].resign_required is False

    def test_bad_payload_raises(self):
        with pytest.raises(MigrationError, match="payload"):
            migrate_0_4_0_to_0_5_0({"payload": "!!!", "signatures": []})

    def test_encrypted_input_raises(self):
        with pytest.raises(MigrationError, match="decrypt"):
            migrate_0_4_0_to_0_5_0({"protected": "x", "ciphertext": "y", "recipients": []})

    def test_signed_payload_must_be_0_4_0(self):
        with pytest.raises(MigrationError, match="expected '0.4.0'"):
            migrate_0_4_0_to_0_5_0(self.signed({"vcon": "0.5.0", "uuid": "a", "created_at": "2022-01-01T00:00:00Z"}))

    def test_vcon_load_of_a_library_signed_0_4_0_document(self):
        payload = v04(dialog=[rec()])
        signed = self.signed(payload)
        v = Vcon(signed)
        assert v.vcon == "0.5.0"
        assert v.migration_report.resign_required


class TestT14Extensions:
    LB = {"purpose": "lawful_basis", "start": T0, "party": 0, "dialog": 0, "body": {}, "encoding": "json", "mediatype": "application/json"}

    def test_extensions_in_use_are_added(self):
        out, report = migrate(v04(dialog=[rec()], attachments=[self.LB]))
        assert out["extensions"] == ["lawful_basis"]
        assert any("lawful_basis" in e.message for e in report.inferred)

    def test_existing_list_is_kept_and_extended(self):
        out, _ = migrate(v04(dialog=[rec()], attachments=[self.LB], extensions=["x"], critical=["y"]))
        assert out["extensions"] == ["x", "lawful_basis", "y"]

    def test_wtf_analysis_adds_wtf(self):
        out, _ = migrate(v04(dialog=[rec()], analysis=[{"type": "wtf_transcription", "dialog": 0, "vendor": "v", "body": {}, "encoding": "json"}]))
        assert "wtf_transcription" in out["extensions"]

    def test_unidentifiable_extension_use_is_reported_not_invented(self):
        d = v04(dialog=[rec(encoding="gzip", body="x")])
        out, report = migrate_0_4_0_to_0_5_0(d)
        assert "extensions" not in out
        assert any("cannot be identified" in e.message for e in report.unresolved)

    def test_no_extension_changes_when_none_in_use(self):
        out, _ = migrate(v04(dialog=[rec()]))
        assert "extensions" not in out


class TestLawfulBasisSurvivesMigration:
    LB = {"purpose": "lawful_basis", "start": T0, "party": 0, "dialog": 0, "body": {"lawful_basis": "consent"},
          "encoding": "json", "mediatype": "application/json"}

    def test_attachment_is_kept_unchanged_and_the_gap_is_noted(self):
        out, report = migrate(v04(dialog=[rec()], attachments=[copy.deepcopy(self.LB)]))
        assert out["attachments"] == [self.LB]
        assert "session" not in out["attachments"][0]
        notes = [e for e in report.notes if "lawful_basis attachment scoped by dialog only" in e.message]
        assert len(notes) == 1
        assert Vcon(out).find_lawful_basis_attachments()

    def test_attachment_that_already_has_a_session_is_not_flagged(self):
        att = dict(self.LB, session=[0])
        _, report = migrate(v04(dialog=[rec()], attachments=[att]))
        assert not [e for e in report.notes if "lawful_basis" in e.message]

    def test_attachment_on_a_removed_dialog_gets_the_session_of_the_recording_set(self):
        att = dict(self.LB, dialog=1)
        d = v04(dialog=[rec(recording_set=1), {"type": "recording-set", "start": T0, "recordings": [0]}], attachments=[att])
        out, _ = migrate(d)
        assert out["attachments"][0]["session"] == 1 and "dialog" not in out["attachments"][0]
        assert out["attachments"][0]["purpose"] == "lawful_basis"


class TestT15:
    def test_noted_for_signed_input(self):
        b = lambda o: base64.urlsafe_b64encode(json.dumps(o).encode()).rstrip(b"=").decode()
        _, report = migrate_0_4_0_to_0_5_0({"payload": b(v04()), "signatures": []})
        assert any(e.step == "T15" for e in report.notes)


class TestReport:
    def test_report_structure_and_serialization(self):
        _, report = migrate(v04(dialog=[rec(), text(parties=[0, 1, 2])]))
        assert isinstance(report, MigrationReport)
        assert report.source_version == "0.4.0" and report.target_version == "0.5.0"
        d = json.loads(json.dumps(report.to_dict()))
        assert d["entries"] and d["steps_run"]
        assert "inferred" in report.summary()

    def test_unpacks_as_a_pair(self):
        result = migrate_0_4_0_to_0_5_0(v04())
        out, report = result
        assert result.vcon is out and result.report is report

    def test_post_migration_problems_are_reported(self):
        # An attachment that already lacked party was invalid in 0.4.0 and stays so.
        d = v04(dialog=[rec()], attachments=[{"purpose": "x", "body": "b", "encoding": "none"}])
        _, report = migrate_0_4_0_to_0_5_0(d)
        assert any(e.step == "post" and "party" in e.message for e in report.unresolved)

    def test_every_entry_has_a_known_kind(self):
        _, report = migrate(v04(dialog=[rec(originator=1), text(parties=[0, 1, 2])]))
        assert {e.kind for e in report.entries} <= {"inferred", "fallback", "unresolved", "info"}


class TestReadersAcceptBothVersions:
    def test_0_4_0_json_is_migrated_on_load(self):
        v = Vcon.build_from_json(json.dumps(v04(dialog=[rec(originator=1)])))
        assert v.vcon == "0.5.0"
        assert v.migration_report is not None
        assert v.sessions[0]["originator"] == 1
        assert v.is_valid() == (True, [])

    def test_0_5_0_input_is_not_touched(self):
        src = {"vcon": "0.5.0", "uuid": "a", "created_at": "2022-01-01T00:00:00Z", "parties": [], "dialog": [{}], "sessions": [{}]}
        v = Vcon(copy.deepcopy(src))
        assert v.migration_report is None
        assert v.vcon_dict["dialog"] == [{}] and v.vcon_dict["sessions"] == [{}]

    def test_input_without_vcon_is_not_migrated_on_load(self):
        d = v04(dialog=[rec(originator=1)])
        del d["vcon"]
        v = Vcon(d)
        assert v.migration_report is None
        assert v.vcon_dict["dialog"][0]["originator"] == 1

    def test_load_from_file_migrates(self, tmp_path):
        p = tmp_path / "old.json"
        p.write_text(json.dumps(v04(dialog=[rec()])))
        v = Vcon.load(str(p))
        assert v.vcon == "0.5.0" and v.migration_report

    def test_migrate_legacy_false_keeps_the_raw_document(self):
        v = Vcon(v04(dialog=[rec()]), migrate_legacy=False)
        assert v.vcon == "0.4.0" and v.migration_report is None
        assert not v.is_valid()[0]

    def test_explicit_call_returns_a_vcon_with_report(self):
        d = v04(dialog=[rec()])
        del d["vcon"]
        v = Vcon.migrate_0_4_0_to_0_5_0(d)
        assert v.vcon == "0.5.0" and v.migration_report and v.sessions

    def test_strict_migration_raises_through_the_constructor(self):
        d = v04(dialog=[rec(), {"type": "transfer", "transferee": 0, "transfer_target": 2, "original": 0}])
        with pytest.raises(MigrationError):
            Vcon(d, strict_migration=True)

    def test_writers_emit_0_5_0(self):
        v = Vcon.build_from_json(json.dumps(v04(dialog=[rec()])))
        assert json.loads(v.to_json())["vcon"] == "0.5.0"
