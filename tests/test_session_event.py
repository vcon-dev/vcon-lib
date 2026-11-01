"""Session, Session_Reference and Event Objects (core-05 sections 4.2 and 4.3)."""

import pytest

from vcon import Vcon, Dialog, Session, SessionReference, Event
from vcon.event import (
    EVENT_PARAMETER_RULES,
    CORE_EVENT_TYPES,
    validate_event,
)
from vcon.party import Party

T = "2026-01-01T00:00:00Z"


def _valid_event(etype):
    """A minimal valid Event dict for each core type."""
    base = {"type": etype, "time": T}
    if etype == "channel-contributors":
        return {**base, "dialog": 0, "channel": 0}
    base.update({"sessions": 0, "party": 0})
    if etype in ("keydown", "keyup"):
        base["button"] = "5"
    elif etype == "consultation-start":
        base.update(transferee=1, transfer_target=2, consultation=1)
    elif etype == "blind-transfer":
        base.update(transferee=1, transfer_target=2, target_session=1)
    elif etype == "consultative-transfer":
        base.update(transferee=1, transfer_target=2, consultation=1, target_session=2)
    elif etype == "transfer-abandoned":
        base.update(transferee=1)
    return base


class TestSession:
    def test_empty_session_is_allowed(self):
        assert Session().to_dict() == {}
        errors, _ = __import__("vcon.session", fromlist=["x"]).validate_session({})
        assert errors == []

    def test_to_dict_fields(self):
        s = Session(
            start="2026-01-01T00:00:00Z",
            duration=12.5,
            parties=[0, 1],
            originator=1,
            session_id={"local": "a", "remote": "b"},
            sessions=[SessionReference(2, "child", "side call")],
            dialog=[0, 1],
        )
        d = s.to_dict()
        assert d["parties"] == [0, 1]
        assert d["originator"] == 1
        assert d["session_id"] == {"local": "a", "remote": "b"}
        assert d["sessions"] == [{"session": 2, "type": "child", "description": "side call"}]
        assert d["dialog"] == [0, 1]

    def test_session_reference_requires_type_and_index(self):
        with pytest.raises(ValueError):
            SessionReference(-1, "child")
        with pytest.raises(ValueError):
            SessionReference(0, "")

    def test_session_reference_validation(self):
        vcon = Vcon.build_new()
        vcon.add_session(Session(start=T, sessions=[{"session": 5, "type": "child"}]))
        valid, errors = vcon.is_valid()
        assert not valid
        assert any("invalid session index: 5" in e for e in errors)

    def test_add_session_returns_index(self):
        vcon = Vcon.build_new()
        assert vcon.add_session(Session(start=T)) == 0
        assert vcon.add_session() == 1
        assert vcon.sessions == [{"start": "2026-01-01T00:00:00+00:00"}, {}]

    def test_session_dialog_index_checked(self):
        vcon = Vcon.build_new()
        vcon.add_session(Session(dialog=[3]))
        valid, errors = vcon.is_valid()
        assert not valid
        assert any("invalid dialog index: 3" in e for e in errors)

    def test_session_party_index_checked(self):
        vcon = Vcon.build_new()
        vcon.add_party(Party(name="A"))
        vcon.add_session(Session(parties=[0, 4]))
        valid, errors = vcon.is_valid()
        assert not valid
        assert any("invalid party index: 4" in e for e in errors)

    def test_sessions_required_when_dialog_or_events_exist(self):
        vcon = Vcon.build_new()
        vcon.add_party(Party(name="A"))
        vcon.add_dialog(Dialog(type="text", start=T, parties=[0], body="x", mediatype="text/plain", encoding="none"))
        valid, errors = vcon.is_valid()
        assert not valid
        assert any("At least one Session Object MUST exist" in e for e in errors)

        vcon2 = Vcon.build_new()
        vcon2.add_party(Party(name="A"))
        vcon2.add_event(Event(type="join", time=T, sessions=0, party=0))
        valid, errors = vcon2.is_valid()
        assert any("At least one Session Object MUST exist" in e for e in errors)

    def test_add_dialog_to_session_and_unreferenced_dialog_warns(self):
        vcon = Vcon.build_new()
        vcon.add_party(Party(name="A"))
        vcon.add_session(Session(start=T, parties=[0]))
        idx = vcon.add_dialog(
            Dialog(type="text", start=T, parties=[0], body="x", mediatype="text/plain", encoding="none"),
            session=0,
        )
        assert idx == 0
        assert vcon.sessions[0]["dialog"] == [0]
        assert vcon.is_valid() == (True, [])
        vcon.add_dialog(Dialog.placeholder())
        assert vcon.is_valid()[0]  # an empty Dialog needs no Session
        vcon.add_dialog(
            Dialog(type="text", start=T, parties=[0], body="y", mediatype="text/plain", encoding="none")
        )
        assert any("not referenced by any Session" in w for w in vcon.get_validation_warnings())


class TestEventTable:
    @pytest.mark.parametrize("etype", CORE_EVENT_TYPES)
    def test_minimal_valid_event_passes(self, etype):
        errors, warnings = validate_event(_valid_event(etype))
        assert errors == []
        assert warnings == []

    @pytest.mark.parametrize("etype", CORE_EVENT_TYPES)
    def test_every_M_parameter_is_enforced(self, etype):
        for param, code in EVENT_PARAMETER_RULES[etype].items():
            if code != "M":
                continue
            ev = _valid_event(etype)
            del ev[param]
            errors, _ = validate_event(ev)
            assert any(param in e for e in errors), (etype, param, errors)

    @pytest.mark.parametrize("etype", CORE_EVENT_TYPES)
    def test_every_X_parameter_is_rejected(self, etype):
        sample = {
            "sessions": 0, "party": 0, "dialog": 0, "channel": 0, "contributors": [0],
            "button": "1", "transferee": 0, "transfer_target": 0, "consultation": 0,
            "target_session": 0,
        }
        for param, code in EVENT_PARAMETER_RULES[etype].items():
            if code != "X":
                continue
            ev = _valid_event(etype)
            ev[param] = sample[param]
            errors, _ = validate_event(ev)
            assert any(f"must not have field: {param}" in e for e in errors), (etype, param, errors)

    @pytest.mark.parametrize("etype", CORE_EVENT_TYPES)
    def test_every_SN_parameter_warns(self, etype):
        for param, code in EVENT_PARAMETER_RULES[etype].items():
            if code != "SN":
                continue
            ev = _valid_event(etype)
            ev[param] = 0
            errors, warnings = validate_event(ev)
            assert errors == []
            assert any(f"should not have field: {param}" in w for w in warnings)

    @pytest.mark.parametrize("etype", CORE_EVENT_TYPES)
    def test_optional_parameters_are_accepted(self, etype):
        for param, code in EVENT_PARAMETER_RULES[etype].items():
            if code != "O":
                continue
            ev = _valid_event(etype)
            ev[param] = 1 if param != "contributors" else None
            errors, warnings = validate_event(ev)
            assert errors == [] and warnings == [], (etype, param)

    def test_table_matches_the_draft_for_transfer_types(self):
        r = EVENT_PARAMETER_RULES
        assert r["consultation-start"]["target_session"] == "X"
        assert r["consultation-start"]["consultation"] == "M"
        assert r["blind-transfer"]["consultation"] == "X"
        assert r["blind-transfer"]["target_session"] == "M"
        assert r["consultative-transfer"]["consultation"] == "M"
        assert r["consultative-transfer"]["target_session"] == "M"
        assert r["transfer-abandoned"]["transfer_target"] == "O"
        assert r["transfer-abandoned"]["consultation"] == "O"
        assert r["transfer-abandoned"]["target_session"] == "X"
        assert r["channel-contributors"]["sessions"] == "X"
        assert r["channel-contributors"]["party"] == "X"
        assert r["keydown"]["button"] == "M"
        assert r["join"]["button"] == "X"

    def test_transfer_sessions_must_be_a_single_index(self):
        ev = _valid_event("blind-transfer")
        ev["sessions"] = [0]
        errors, _ = validate_event(ev)
        assert any("single session index" in e for e in errors)

    def test_party_event_accepts_session_list_and_bare_integer(self):
        for sessions in (0, [0, 1]):
            ev = _valid_event("join")
            ev["sessions"] = sessions
            assert validate_event(ev)[0] == []

    def test_time_must_parse(self):
        ev = _valid_event("join")
        ev["time"] = "not a time"
        assert any("invalid 'time'" in e for e in validate_event(ev)[0])
        del ev["time"]
        assert any("missing required field: time" in e for e in validate_event(ev)[0])

    def test_unknown_type_checked_for_type_and_time_only(self):
        errors, warnings = validate_event({"type": "tool-call", "time": T, "tool_name": "x"})
        assert errors == [] and warnings == []

    def test_channel_contributors_must_reference_recording_dialog(self):
        vcon = Vcon.build_new()
        vcon.add_party(Party(name="A"))
        vcon.add_session(Session(start=T, parties=[0]))
        vcon.add_dialog(
            Dialog(type="text", start=T, parties=[0], body="x", mediatype="text/plain", encoding="none"),
            session=0,
        )
        vcon.add_event(Event(type="channel-contributors", time=T, dialog=0, channel=0, contributors=0))
        valid, errors = vcon.is_valid()
        assert not valid
        assert any("must reference a 'recording' Dialog" in e for e in errors)


class TestEventClass:
    def test_blind_transfer_roundtrip(self):
        e = Event(
            type="blind-transfer", time=T, sessions=0, party=1,
            transferee=0, transfer_target=2, target_session=1,
        )
        assert e.to_dict() == {
            "type": "blind-transfer", "time": T, "sessions": 0, "party": 1,
            "transferee": 0, "transfer_target": 2, "target_session": 1,
        }
        assert Event.from_dict(e.to_dict()).to_dict() == e.to_dict()

    def test_constructor_enforces_the_table(self):
        with pytest.raises(ValueError, match="button"):
            Event(type="join", time=T, sessions=0, party=0, button="1")
        with pytest.raises(ValueError, match="missing required field: button"):
            Event(type="keydown", time=T, sessions=0, party=0)
        with pytest.raises(ValueError, match="consultation"):
            Event(type="blind-transfer", time=T, sessions=0, party=0, transferee=1,
                  transfer_target=2, target_session=1, consultation=1)

    def test_extension_event_type_and_params(self):
        e = Event(type="tool-call", time=T, tool_name="search")
        assert e.to_dict()["tool_name"] == "search"

    def test_vcon_add_event_and_validation_of_plain_dicts(self):
        vcon = Vcon.build_new()
        vcon.add_party(Party(name="A"))
        vcon.add_session(Session(start=T, parties=[0]))
        i = vcon.add_event(Event(type="join", time=T, sessions=0, party=0))
        assert i == 0 and vcon.events[0]["type"] == "join"
        assert vcon.is_valid() == (True, [])
        vcon.add_event({"type": "join", "time": T, "sessions": 0, "party": 0, "button": "1"})
        valid, errors = vcon.is_valid()
        assert not valid
        assert any("Event at index 1" in e and "button" in e for e in errors)
        vcon.add_event({"type": "join", "time": T, "sessions": 7, "party": 9})
        errors = vcon.is_valid()[1]
        assert any("invalid session index: 7" in e for e in errors)
        assert any("invalid party index: 9" in e for e in errors)

    def test_unlisted_extension_event_type_requires_extensions(self):
        vcon = Vcon.build_new()
        vcon.add_party(Party(name="A"))
        vcon.add_session(Session(start=T, parties=[0]))
        vcon.add_event(Event(type="tool-call", time=T, sessions=0, party=0))
        valid, errors = vcon.is_valid()
        assert not valid
        assert any("events[0] type 'tool-call'" in e for e in errors)
        vcon.add_extension("tool_calls")
        assert vcon.is_valid() == (True, [])
