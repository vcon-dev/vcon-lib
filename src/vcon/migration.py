"""Migrate a vCon from syntax 0.4.0 to 0.5.0 (draft-ietf-vcon-vcon-core-05, Appendix A.1).

The migration is table driven. ``MIGRATION_STEPS`` holds one ``MigrationStep``
per step T1..T15 of the ordered transform table; each step is one function that
mutates a shared ``_Context``. If a later edit of Appendix A.1 changes one step,
only that function (or its table entry) needs to change.

Execution order (the draft gives none; this order is inferred so that every
``dialog`` index stays valid): the steps that read the 0.4.0 ``dialog`` array
run before any array is rewritten, and ``T10`` blanks the removed Dialogs in
place at the end, so the array length and every other index are unchanged.

    T13 T15 T1  ->  T8 T9 T9b T6  ->  T2 T7 T3 T4(+T5)  ->  T10 T10b  ->  T11 T12 T14

Nothing is invented silently. Every value the draft does not dictate is listed
in the :class:`MigrationReport` (kind ``inferred``), every field that had to be
filled by a fallback is listed (kind ``fallback``), and every problem the
migration could not resolve is listed (kind ``unresolved``). In strict mode a
fallback raises :class:`MigrationError` instead.

A signed 0.4.0 vCon is migrated as the unsigned payload. The migration never
signs; the report sets ``resign_required``.
"""

from __future__ import annotations

import base64
import copy
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple

from dateutil import parser

from .validation import extensions_in_use, validate_vcon_dict

logger = logging.getLogger(__name__)

SOURCE_VERSION = "0.4.0"
TARGET_VERSION = "0.5.0"


class MigrationError(ValueError):
    """The vCon cannot be migrated (or, in strict mode, a MUST field has no source)."""


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

#: A value the draft does not dictate; a documented default was applied.
INFERRED = "inferred"
#: A MUST field with no source was filled with the documented fallback.
FALLBACK = "fallback"
#: A problem left for a person to resolve.
UNRESOLVED = "unresolved"
#: Informational.
INFO = "info"


@dataclass
class ReportEntry:
    step: str
    kind: str
    message: str
    code: Optional[str] = None  # AMB-n identifier from the implementation spec
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"step": self.step, "kind": self.kind, "message": self.message}
        if self.code:
            out["code"] = self.code
        if self.details:
            out["details"] = self.details
        return out


@dataclass
class MigrationReport:
    """What a migration did that the draft did not dictate."""

    source_version: Optional[str] = None
    target_version: str = TARGET_VERSION
    strict: bool = False
    #: True when the input was signed: the signature is dropped and the result is unsigned.
    resign_required: bool = False
    entries: List[ReportEntry] = field(default_factory=list)
    #: Original content of every Dialog replaced by ``{}``, keyed by its (unchanged) index.
    removed_dialogs: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    #: Steps that ran, in order.
    steps_run: List[str] = field(default_factory=list)

    def add(
        self,
        step: str,
        kind: str,
        message: str,
        code: Optional[str] = None,
        **details: Any,
    ) -> None:
        self.entries.append(ReportEntry(step, kind, message, code, details))

    def _of(self, kind: str) -> List[ReportEntry]:
        return [e for e in self.entries if e.kind == kind]

    @property
    def inferred(self) -> List[ReportEntry]:
        return self._of(INFERRED)

    @property
    def fallbacks(self) -> List[ReportEntry]:
        return self._of(FALLBACK)

    @property
    def unresolved(self) -> List[ReportEntry]:
        return self._of(UNRESOLVED)

    @property
    def notes(self) -> List[ReportEntry]:
        return self._of(INFO)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_version": self.source_version,
            "target_version": self.target_version,
            "strict": self.strict,
            "resign_required": self.resign_required,
            "steps_run": list(self.steps_run),
            "entries": [e.to_dict() for e in self.entries],
            "removed_dialogs": {str(k): v for k, v in self.removed_dialogs.items()},
        }

    def summary(self) -> str:
        return (
            f"{len(self.inferred)} inferred, {len(self.fallbacks)} fallback, "
            f"{len(self.unresolved)} unresolved"
            + ("; re-signing required" if self.resign_required else "")
        )


class MigrationResult(NamedTuple):
    """Result of a migration. Unpacks as ``(vcon, report)``."""

    vcon: Dict[str, Any]
    report: MigrationReport


# ---------------------------------------------------------------------------
# Context and helpers
# ---------------------------------------------------------------------------


def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _parse_dt(value: Any) -> Optional[datetime]:
    if not isinstance(value, str):
        return None
    try:
        dt = parser.parse(value)
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _num(seconds: float) -> Any:
    seconds = round(seconds, 6)
    return int(seconds) if float(seconds).is_integer() else seconds


def _plain_parties(value: Any) -> List[int]:
    """Flat list of int party indices of a 0.4.0 Dialog ``parties`` value."""
    out: List[int] = []
    items = value if isinstance(value, list) else ([] if value is None else [value])
    for v in items:
        if isinstance(v, list):
            out.extend(x for x in v if _is_int(x))
        elif _is_int(v):
            out.append(v)
    return out


def _union(lists: List[List[int]]) -> List[int]:
    seen: List[int] = []
    for lst in lists:
        for v in lst:
            if v not in seen:
                seen.append(v)
    return seen


def _rename_key(d: Dict[str, Any], old: str, new: str) -> Dict[str, Any]:
    return {(new if k == old else k): v for k, v in d.items()}


class _Context:
    def __init__(self, data: Dict[str, Any], strict: bool, report: MigrationReport) -> None:
        self.out: Dict[str, Any] = data
        self.src: Dict[str, Any] = copy.deepcopy(data)  # refreshed by T13 after unwrapping
        self.strict = strict
        self.report = report
        self.sessions: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        #: receivers contributed to the Session by each (kept) Dialog index
        self.receivers: Dict[int, List[int]] = {}
        #: originator value taken from each (kept) Dialog index
        self.originators: Dict[int, int] = {}
        #: Session indices each Dialog index belongs to
        self.dialog_sessions: Dict[int, List[int]] = {}
        #: recording-set Dialog index -> Session index (T7)
        self.rs_session: Dict[int, int] = {}
        #: transfer Dialog index -> Session index of its original call (T4)
        self.transfer_session: Dict[int, int] = {}
        self._role_sessions: Dict[int, int] = {}
        self._empty_party: Optional[int] = None
        self.catch_all: Optional[int] = None

    # -- source views ---------------------------------------------------
    @property
    def dialogs(self) -> List[Any]:
        d = self.src.get("dialog")
        return d if isinstance(d, list) else []

    @property
    def removed(self) -> Dict[int, str]:
        """Dialog index -> removed type, for transfer and recording-set Dialogs."""
        return {
            i: d["type"]
            for i, d in enumerate(self.dialogs)
            if isinstance(d, dict) and d.get("type") in ("transfer", "recording-set")
        }

    def kept(self) -> List[int]:
        rem = self.removed
        return [i for i, d in enumerate(self.dialogs) if i not in rem and isinstance(d, dict) and d]

    # -- helpers --------------------------------------------------------
    def need_fallback(self, step: str, message: str, code: Optional[str] = None, **details: Any) -> None:
        """Record a fallback for a MUST field, or raise in strict mode."""
        if self.strict:
            raise MigrationError(f"{step}: {message} (strict mode: no source for a required field)")
        self.report.add(step, FALLBACK, message, code, **details)

    def new_session(self, session: Dict[str, Any]) -> int:
        self.sessions.append(session)
        return len(self.sessions) - 1

    def empty_party(self, step: str, role: str) -> int:
        """Index of an empty Party Object, appended once (4.3.9: unknown party)."""
        if self._empty_party is None:
            parties = self.out.setdefault("parties", [])
            parties.append({})
            self._empty_party = len(parties) - 1
            self.report.add(
                step, INFERRED,
                f"Appended an empty Party Object at parties[{self._empty_party}] to stand for unknown parties.",
                None, party=self._empty_party,
            )
        return self._empty_party

    def dialog_start(self, idx: Any) -> Optional[str]:
        """Start of a Dialog, or of a recording-set's earliest recording."""
        if not _is_int(idx) or not 0 <= idx < len(self.dialogs):
            return None
        d = self.dialogs[idx]
        if not isinstance(d, dict):
            return None
        if _parse_dt(d.get("start")):
            return d["start"]
        if d.get("type") == "recording-set":
            starts = [
                (self.dialogs[r].get("start"))
                for r in (d.get("recordings") or [])
                if _is_int(r) and 0 <= r < len(self.dialogs) and isinstance(self.dialogs[r], dict)
            ]
            starts = [s for s in starts if _parse_dt(s)]
            if starts:
                return min(starts, key=_parse_dt)
        return None

    def span(self, idxs: List[int]) -> Tuple[Optional[str], Optional[Any]]:
        """Derived (start, duration) of a group of Dialogs.

        start is the earliest Dialog start. duration runs from that start to the
        latest Dialog end (start plus duration, or start when no duration is
        known), and is only derived when at least one Dialog has a duration.
        """
        items = [
            (i, _parse_dt(self.dialogs[i].get("start")))
            for i in idxs
            if isinstance(self.dialogs[i], dict)
        ]
        items = [(i, s) for i, s in items if s is not None]
        if not items:
            return None, None
        first_i, first = min(items, key=lambda t: t[1])
        start_str = self.dialogs[first_i]["start"]
        ends = []
        any_duration = False
        for i, s in items:
            dur = self.dialogs[i].get("duration")
            if isinstance(dur, (int, float)) and not isinstance(dur, bool):
                any_duration = True
                ends.append(s.timestamp() + dur)
            else:
                ends.append(s.timestamp())
        if not any_duration:
            return start_str, None
        return start_str, _num(max(ends) - first.timestamp())

    def make_session(self, step: str, idxs: List[int], label: str) -> Dict[str, Any]:
        """Build a Session for a group of kept Dialogs from derived values."""
        session: Dict[str, Any] = {}
        start, duration = self.span(idxs)
        if start is not None:
            session["start"] = start
        if duration is not None:
            session["duration"] = duration
        parties = _union([self.receivers.get(i, []) for i in idxs])
        if parties:
            session["parties"] = parties
        orig = [self.originators[i] for i in idxs if i in self.originators]
        if orig:
            chosen = orig[0]
            others = sorted({o for o in orig[1:] if o != chosen})
            if others:
                self.report.add(
                    step, UNRESOLVED,
                    f"{label}: Dialogs name different originators; kept {chosen}, "
                    f"did not record {others}.", None, kept=chosen, dropped=others,
                )
            if not parties or chosen != parties[0]:
                session["originator"] = chosen
        session["dialog"] = list(idxs)
        # key order: start, duration, parties, originator, dialog
        order = ("start", "duration", "parties", "originator", "session_id", "sessions", "dialog")
        session = {k: session[k] for k in order if k in session}
        if start is not None or duration is not None:
            self.report.add(
                step, INFERRED,
                f"{label}: start/duration derived from its Dialogs (earliest start; "
                "duration to the latest end when any Dialog has a duration).",
                None, start=start, duration=duration,
            )
        return session


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------


def _step_t1_version(ctx: _Context) -> None:
    """T1: ``vcon`` "0.4.0" -> "0.5.0"."""
    if "vcon" not in ctx.out:
        ctx.report.add("T1", INFERRED, "Input had no 'vcon' parameter; set to '0.5.0' (AMB-12: writers emit it).", "AMB-12")
    ctx.out["vcon"] = TARGET_VERSION


def _step_t2_sessions(ctx: _Context) -> None:
    """T2: add one Session which references all (kept) Dialog Objects.

    The removed transfer and recording-set positions are skipped (they become
    ``{}``; T10). Receivers (T8, T9, T9b) and the originator (T6) have already
    been collected, so the Session is built in one go.
    """
    kept = ctx.kept()
    if not kept:
        return
    ctx.catch_all = ctx.new_session(ctx.make_session("T2", kept, "Session 0 (all Dialogs)"))
    for i in kept:
        ctx.dialog_sessions.setdefault(i, []).append(ctx.catch_all)
    ctx.report.add(
        "T2", INFO,
        f"Added Session {ctx.catch_all} referencing {len(kept)} Dialog Object(s).",
    )


def _step_t3_party_history(ctx: _Context) -> None:
    """T3: each Dialog ``party_history`` entry becomes an Event; ``event`` is renamed ``type``.

    The Event's ``sessions`` references the Session(s) for the Dialog it came
    from and the Event does not reference the Dialog (SHOULD NOT, 4.3.5).
    """
    dialogs = ctx.out.get("dialog")
    if not isinstance(dialogs, list):
        return
    for i, src_d in enumerate(ctx.dialogs):
        if not isinstance(src_d, dict) or "party_history" not in src_d:
            continue
        if src_d.get("type") == "transfer":
            ctx.report.add(
                "T3", UNRESOLVED,
                f"dialog[{i}] is a transfer Dialog with party_history; the entries are not migrated "
                "(A.1 covers party_history on non-transfer Dialogs). Original kept in removed_dialogs.",
                None, dialog=i,
            )
            continue
        if src_d.get("type") == "recording-set":
            sess = [ctx.rs_session[i]] if i in ctx.rs_session else []
        else:
            sess = sorted(ctx.dialog_sessions.get(i, []))
        if len(sess) > 1:
            ctx.report.add(
                "T3", INFERRED,
                f"dialog[{i}] belongs to Sessions {sess}; its party_history Events list all of them "
                "in 'sessions' (4.3.3: an Event applies only to the Sessions listed).",
                "AMB-3", dialog=i, sessions=sess,
            )
        history = src_d["party_history"]
        if not isinstance(history, list):
            ctx.report.add("T3", UNRESOLVED, f"dialog[{i}] party_history is not a list; dropped.", None, dialog=i)
        else:
            for n, entry in enumerate(history):
                if not isinstance(entry, dict) or "event" not in entry:
                    ctx.report.add(
                        "T3", UNRESOLVED,
                        f"dialog[{i}].party_history[{n}] has no 'event'; entry not migrated.",
                        None, dialog=i, entry=entry,
                    )
                    continue
                ev: Dict[str, Any] = {"type": entry["event"]}
                if _parse_dt(entry.get("time")):
                    ev["time"] = entry["time"]
                else:
                    fb = src_d.get("start")
                    ctx.need_fallback(
                        "T3",
                        f"dialog[{i}].party_history[{n}] has no usable time; used the Dialog start "
                        f"({fb!r}) as the Event time.", None, dialog=i,
                    )
                    if fb is None:
                        raise MigrationError(
                            f"T3: dialog[{i}].party_history[{n}] has no time and the Dialog has no start"
                        )
                    ev["time"] = fb
                if sess:
                    ev["sessions"] = sess[0] if len(sess) == 1 else sess
                if _is_int(entry.get("party")):
                    ev["party"] = entry["party"]
                else:
                    ctx.need_fallback(
                        "T3",
                        f"dialog[{i}].party_history[{n}] has no party; referenced an empty Party Object.",
                        None, dialog=i,
                    )
                    ev["party"] = ctx.empty_party("T3", "party")
                if entry["event"] in ("keydown", "keyup") and "button" in entry:
                    ev["button"] = entry["button"]
                elif "button" in entry:
                    ctx.report.add(
                        "T3", UNRESOLVED,
                        f"dialog[{i}].party_history[{n}] has 'button' on a '{entry['event']}' event "
                        "(only keydown and keyup carry it); button not migrated.", None, dialog=i,
                    )
                ctx.events.append(ev)
        if src_d.get("type") != "recording-set" and isinstance(dialogs[i], dict):
            dialogs[i].pop("party_history", None)


def _step_t4_transfers(ctx: _Context) -> None:
    """T4 (with T5): each ``transfer`` Dialog becomes one or two transfer Events.

    ``transferor`` becomes ``party``. ``original``, ``consultation`` and
    ``target_dialog`` become Session indices (T5): the recording-set's Session,
    otherwise a Session that lists that Dialog.
    """
    for k, kind in ctx.removed.items():
        if kind != "transfer":
            continue
        tr = ctx.dialogs[k]
        step = "T4"

        def session_for(ref: Any, role: str, required: bool) -> Optional[int]:
            """T5: Session index for a Dialog reference held by a transfer Dialog."""
            if ref is None:
                return None
            if not _is_int(ref) or not 0 <= ref < len(ctx.dialogs):
                ctx.report.add(step, UNRESOLVED, f"transfer dialog[{k}] {role}={ref!r} is not a Dialog index.", None, dialog=k)
                return None
            if ref in ctx.rs_session:
                ctx.report.add(
                    "T5", INFO,
                    f"transfer dialog[{k}] {role} -> dialog[{ref}] is a recording-set; using its Session {ctx.rs_session[ref]}.",
                )
                return ctx.rs_session[ref]
            if ref in ctx.removed:
                idx = ctx.new_session({})
                ctx.report.add(
                    "T5", UNRESOLVED,
                    f"transfer dialog[{k}] {role} -> dialog[{ref}] is itself a removed {ctx.removed[ref]} Dialog; "
                    f"created placeholder Session {idx} with no parameters.", None, dialog=k,
                )
                return idx
            if ref in ctx._role_sessions:
                return ctx._role_sessions[ref]
            sess = ctx.make_session("T5", [ref], f"Session for transfer {role} (dialog[{ref}])")
            idx = ctx.new_session(sess)
            ctx._role_sessions[ref] = idx
            ctx.dialog_sessions.setdefault(ref, []).append(idx)
            ctx.report.add(
                "T5", INFERRED,
                f"transfer dialog[{k}] {role} -> created Session {idx} listing dialog[{ref}] "
                "(A.1: referenced through a Session Object).", None, dialog=k, session=idx,
            )
            return idx

        def placeholder(role: str, why: str, required_fallback: bool) -> int:
            idx = ctx.new_session({})
            msg = f"transfer dialog[{k}] has no {role} ({why}); created placeholder Session {idx} with no parameters (4.3.1.3)."
            if required_fallback:
                ctx.need_fallback(step, msg, None, dialog=k, session=idx)
            else:
                ctx.report.add(step, INFERRED, msg, "AMB-7", dialog=k, session=idx)
            return idx

        # Session of the original call (sessions: M, single index).
        orig_ref = tr.get("original")
        sidx = session_for(orig_ref, "original", True)
        if sidx is None:
            sidx = placeholder("original", "'sessions' is required on every transfer Event", True)
        ctx.transfer_session[k] = sidx

        def party_ref(key: str, role: str, required: bool) -> Optional[int]:
            val = tr.get(key)
            if _is_int(val):
                return val
            if not required:
                return None
            ctx.need_fallback(
                step,
                f"transfer dialog[{k}] has no {key} ({role}); referenced an empty Party Object (4.3.9).",
                None, dialog=k,
            )
            return ctx.empty_party(step, role)

        transferor = party_ref("transferor", "Transferor, becomes 'party'", True)
        transferee = party_ref("transferee", "Transferee", True)

        cons_ref = tr.get("consultation")
        target_ref = tr.get("target_dialog")
        cons_sess = session_for(cons_ref, "consultation", False) if cons_ref is not None else None
        if cons_ref is not None and cons_sess is None:
            cons_sess = placeholder("usable consultation", "consultation Dialog index could not be resolved", False)
        target_sess = session_for(target_ref, "target_dialog", False) if target_ref is not None else None
        has_target_party = _is_int(tr.get("transfer_target"))

        # Event types (AMB-7).
        types: List[str] = []
        if cons_ref is not None:
            types.append("consultation-start")
        if target_ref is not None or has_target_party:
            types.append("consultative-transfer" if cons_ref is not None else "blind-transfer")
        else:
            types.append("transfer-abandoned")
        ctx.report.add(
            step, INFERRED,
            f"transfer dialog[{k}] mapped to Event type(s) {types} "
            "(consultation present -> consultation-start + consultative-transfer; otherwise blind-transfer; "
            "no target_dialog and no transfer_target -> transfer-abandoned).",
            "AMB-7", dialog=k, types=types,
        )
        if "blind-transfer" in types or "consultative-transfer" in types:
            if target_sess is None:
                target_sess = placeholder(
                    "target_dialog",
                    "the target call was not captured; 4.3.1.3 uses a placeholder Session in that case", False,
                )

        def event_time(which: str) -> str:
            own = tr.get("start")
            if _parse_dt(own):
                return own
            cands: List[Tuple[Optional[str], str]] = []
            if which == "consult":
                cands.append((ctx.dialog_start(cons_ref), f"start of consultation dialog[{cons_ref}]"))
            else:
                cands.append((ctx.dialog_start(target_ref), f"start of target dialog[{target_ref}]"))
                if cons_ref is not None:
                    cd = ctx.dialogs[cons_ref] if _is_int(cons_ref) and 0 <= cons_ref < len(ctx.dialogs) else None
                    cs, dur = _parse_dt(ctx.dialog_start(cons_ref)), (cd or {}).get("duration") if isinstance(cd, dict) else None
                    if cs is not None and isinstance(dur, (int, float)) and not isinstance(dur, bool):
                        end = datetime.fromtimestamp(cs.timestamp() + dur, tz=timezone.utc).isoformat()
                        cands.append((end, f"end of consultation dialog[{cons_ref}] (start + duration)"))
                    cands.append((ctx.dialog_start(cons_ref), f"start of consultation dialog[{cons_ref}]"))
            for value, src in cands:
                if value and _parse_dt(value):
                    ctx.report.add(
                        step, INFERRED,
                        f"transfer dialog[{k}] has no start; Event time taken from the {src}, "
                        "not from the transfer Dialog's own start.", "AMB-7", dialog=k, source=src, time=value,
                    )
                    return value
            created = ctx.out.get("created_at")
            if _parse_dt(created):
                ctx.need_fallback(
                    step,
                    f"transfer dialog[{k}] has no start and no other time source; used the vCon created_at "
                    f"({created!r}) as the Event time.", "AMB-7", dialog=k,
                )
                return created
            raise MigrationError(
                f"{step}: transfer dialog[{k}] has no start and the vCon has no created_at; no time can be sourced"
            )

        base: Dict[str, Any] = {}
        for t in types:
            ev: Dict[str, Any] = {"type": t}
            ev["time"] = event_time("consult" if t == "consultation-start" else "transfer")
            ev["sessions"] = sidx
            ev["party"] = transferor
            ev["transferee"] = transferee
            need_target = t != "transfer-abandoned"
            tt = party_ref("transfer_target", "Transfer Target", need_target)
            if tt is not None:
                ev["transfer_target"] = tt
            if t in ("consultation-start", "consultative-transfer"):
                ev["consultation"] = cons_sess
            elif t == "transfer-abandoned" and cons_sess is not None:
                ev["consultation"] = cons_sess
            if t in ("blind-transfer", "consultative-transfer"):
                ev["target_session"] = target_sess
            ctx.events.append(ev)
        extra = sorted(
            set(tr)
            - {"type", "start", "transferee", "transferor", "transfer_target", "original", "consultation", "target_dialog", "parties", "originator", "party_history"}
        )
        if extra or tr.get("parties"):
            ctx.report.add(
                step, UNRESOLVED,
                f"transfer dialog[{k}] had parameters with no Event equivalent "
                f"({extra + (['parties'] if tr.get('parties') else [])}); not migrated. "
                "Original kept in report.removed_dialogs.", None, dialog=k,
            )


def _step_t6_originator(ctx: _Context) -> None:
    """T6: ``originator`` moves from the Dialog to the Session (only when not the first party)."""
    dialogs = ctx.out.get("dialog")
    if not isinstance(dialogs, list):
        return
    for i in ctx.kept():
        d = dialogs[i]
        if "originator" in d:
            val = d.pop("originator")
            if _is_int(val):
                ctx.originators[i] = val
            else:
                ctx.report.add("T6", UNRESOLVED, f"dialog[{i}] originator {val!r} is not a party index; dropped.", None, dialog=i)


def _step_t7_recording_sets(ctx: _Context) -> None:
    """T7: each ``recording-set`` Dialog becomes a Session listing its recordings.

    The recording-set's own start, duration, parties, session_id and originator
    move to the Session (A.1 is silent: AMB-4). ``recording_set`` is removed from
    each recording.
    """
    dialogs = ctx.out.get("dialog")
    for k, kind in ctx.removed.items():
        if kind != "recording-set":
            continue
        rs = ctx.dialogs[k]
        recs_raw = rs.get("recordings")
        recs: List[int] = []
        if isinstance(recs_raw, list):
            for r in recs_raw:
                if _is_int(r) and 0 <= r < len(ctx.dialogs) and r not in ctx.removed and isinstance(ctx.dialogs[r], dict):
                    if r not in recs:
                        recs.append(r)
                else:
                    ctx.report.add("T7", UNRESOLVED, f"recording-set dialog[{k}] lists recordings entry {r!r}, which is not a kept Dialog; left out of the Session.", None, dialog=k)
        else:
            ctx.report.add("T7", UNRESOLVED, f"recording-set dialog[{k}] has no recordings list; Session has no dialog.", None, dialog=k)
        sess: Dict[str, Any] = {}
        d_start, d_dur = ctx.span(recs) if recs else (None, None)
        if _parse_dt(rs.get("start")):
            sess["start"] = rs["start"]
        elif d_start is not None:
            sess["start"] = d_start
        if isinstance(rs.get("duration"), (int, float)) and not isinstance(rs.get("duration"), bool):
            sess["duration"] = rs["duration"]
        elif d_dur is not None:
            sess["duration"] = d_dur
        rs_parties = _plain_parties(rs.get("parties"))
        parties = rs_parties or _union([ctx.receivers.get(r, []) for r in recs])
        if parties:
            sess["parties"] = parties
        orig = rs.get("originator")
        if _is_int(orig) and (not parties or orig != parties[0]):
            sess["originator"] = orig
        sid = rs.get("session_id")
        if isinstance(sid, dict):
            sess["session_id"] = sid
        elif isinstance(sid, list) and len(sid) == 1 and isinstance(sid[0], dict):
            sess["session_id"] = sid[0]
        elif sid is not None:
            ctx.report.add(
                "T7", UNRESOLVED,
                f"recording-set dialog[{k}] session_id is not a single SessionId Object; Session.session_id not set.",
                "AMB-4", dialog=k, session_id=sid,
            )
        if recs:
            sess["dialog"] = recs
        order = ("start", "duration", "parties", "originator", "session_id", "sessions", "dialog")
        sess = {key: sess[key] for key in order if key in sess}
        sidx = ctx.new_session(sess)
        ctx.rs_session[k] = sidx
        for r in recs:
            ctx.dialog_sessions.setdefault(r, []).append(sidx)
        fields_moved = [f for f in ("start", "duration", "parties", "session_id", "originator") if f in rs]
        ctx.report.add(
            "T7", INFERRED,
            f"recording-set dialog[{k}] -> Session {sidx}; its {fields_moved} moved to the Session "
            "(A.1 silent about them); Session start/duration/parties fall back to values derived from the recordings when absent.",
            "AMB-4", dialog=k, session=sidx,
        )
        if ctx.catch_all is not None:
            ctx.report.add(
                "T7", UNRESOLVED,
                f"Session {sidx} (recording-set dialog[{k}]) overlaps Session {ctx.catch_all}, which also lists its "
                "recordings; A.1 does not say whether to relate them, so no Session_Reference was added.",
                "AMB-1", session=sidx, catch_all=ctx.catch_all,
            )
        for r in recs:
            if isinstance(dialogs, list) and isinstance(dialogs[r], dict):
                dialogs[r].pop("recording_set", None)
    # Remove any stray recording_set / recordings on kept dialogs.
    if isinstance(dialogs, list):
        for i in ctx.kept():
            dialogs[i].pop("recording_set", None)
            dialogs[i].pop("recordings", None)


def _step_t8_text_parties(ctx: _Context) -> None:
    """T8: a ``text`` Dialog's ``parties`` reduce to the sender; all parties go to the Session."""
    dialogs = ctx.out.get("dialog")
    if not isinstance(dialogs, list):
        return
    for i in ctx.kept():
        if ctx.dialogs[i].get("type") != "text":
            continue
        p = _plain_parties(ctx.dialogs[i].get("parties"))
        if not p:
            ctx.report.add("T8", UNRESOLVED, f"text dialog[{i}] has no parties; sender and receivers unknown.", None, dialog=i)
            continue
        orig = ctx.dialogs[i].get("originator")
        sender = orig if _is_int(orig) else p[0]
        dialogs[i]["parties"] = [sender]
        ctx.receivers[i] = p if sender in p else [sender] + p


def _step_t9_incomplete_parties(ctx: _Context) -> None:
    """T9: an ``incomplete`` Dialog's ``parties`` reduce to the originator (or first party)."""
    dialogs = ctx.out.get("dialog")
    if not isinstance(dialogs, list):
        return
    for i in ctx.kept():
        if ctx.dialogs[i].get("type") != "incomplete":
            continue
        p = _plain_parties(ctx.dialogs[i].get("parties"))
        if not p:
            continue
        orig = ctx.dialogs[i].get("originator")
        who = orig if _is_int(orig) else p[0]
        dialogs[i]["parties"] = [who]
        ctx.receivers[i] = p if who in p else [who] + p


def _step_t9b_recording_parties(ctx: _Context) -> None:
    """T9b: other Dialogs keep ``parties`` (contributors); the Session gets the union (AMB-6)."""
    idxs = []
    for i in ctx.kept():
        if ctx.dialogs[i].get("type") in ("text", "incomplete"):
            continue
        p = _plain_parties(ctx.dialogs[i].get("parties"))
        if p:
            ctx.receivers[i] = p
            idxs.append(i)
    if idxs:
        ctx.report.add(
            "T9b", INFERRED,
            f"Dialog(s) {idxs} (recording or other type): parties left as the contributors; "
            "the Session parties are the union of the contributors across its Dialogs (A.1 gives no rule).",
            "AMB-6", dialogs=idxs,
        )
    texts = [i for i in ctx.kept() if ctx.dialogs[i].get("type") == "text"]
    if texts:
        sets = {tuple(sorted(ctx.receivers.get(i, []))) for i in texts}
        if len(sets) > 1:
            ctx.report.add(
                "T8", UNRESOLVED,
                f"text Dialogs {texts} have different receiver sets; they were put in one Session whose parties "
                "are the union. 4.5.4 prescribes a parent Session with a child Session per receiver set; that "
                "split was not made.", "AMB-5", dialogs=texts,
            )
        if any(len(s) > 2 for s in sets):
            ctx.report.add(
                "T8", UNRESOLVED,
                "0.4.0 parties do not distinguish To, Cc and Bcc, so Bcc recipients cannot be identified or "
                "excluded.", "AMB-5", dialogs=texts,
            )


def _step_t10_blank_removed(ctx: _Context) -> None:
    """T10: each removed Dialog is replaced in place by ``{}`` so no index moves."""
    dialogs = ctx.out.get("dialog")
    if not isinstance(dialogs, list):
        return
    for k, kind in ctx.removed.items():
        ctx.report.removed_dialogs[k] = copy.deepcopy(ctx.dialogs[k])
        dialogs[k] = {}
        ctx.report.add("T10", INFO, f"dialog[{k}] ({kind}) replaced by an empty Dialog Object; index {k} unchanged.", None, dialog=k)
    if len(dialogs) != len(ctx.dialogs):  # pragma: no cover - internal guard
        raise MigrationError("T10: dialog array length changed; indices would break")


def _merge_index(existing: Any, new: List[int]) -> Any:
    cur = [] if existing is None else (existing if isinstance(existing, list) else [existing])
    merged = list(cur)
    for n in new:
        if n not in merged:
            merged.append(n)
    return merged[0] if len(merged) == 1 else merged


def _step_t10b_retarget(ctx: _Context) -> None:
    """AMB-2: re-point analysis and attachment references to removed Dialogs.

    Recording-set: Analysis.dialog is expanded to the recordings and ``sessions``
    gets the recording-set's Session; an Attachment (single ``dialog`` index)
    gets ``session`` instead. Transfer: the reference moves to the Session of the
    transfer's original call. Nothing is left pointing at a ``{}`` Dialog.
    """
    removed = ctx.removed
    if not removed:
        return

    def targets(e: int) -> Tuple[List[int], Optional[int]]:
        """(replacement dialog indices, session index) for a removed Dialog."""
        if removed[e] == "recording-set":
            sidx = ctx.rs_session.get(e)
            recs = ctx.sessions[sidx].get("dialog", []) if sidx is not None else []
            return list(recs), sidx
        return [], ctx.transfer_session.get(e)

    for n, an in enumerate(ctx.out.get("analysis") or []):
        if not isinstance(an, dict) or "dialog" not in an:
            continue
        old = an["dialog"]
        items = old if isinstance(old, list) else [old]
        if not any(_is_int(x) and x in removed for x in items):
            continue
        new_dialogs: List[int] = []
        sess_add: List[int] = []
        for x in items:
            if _is_int(x) and x in removed:
                reps, sidx = targets(x)
                new_dialogs.extend(r for r in reps if r not in new_dialogs)
                if sidx is not None:
                    sess_add.append(sidx)
            elif x not in new_dialogs:
                new_dialogs.append(x)
        if new_dialogs:
            an["dialog"] = new_dialogs[0] if (len(new_dialogs) == 1 and not isinstance(old, list)) else new_dialogs
        else:
            del an["dialog"]
        if sess_add:
            an["sessions"] = _merge_index(an.get("sessions"), sess_add)
        ctx.report.add(
            "T10b", INFERRED,
            f"analysis[{n}].dialog {old!r} pointed at a removed Dialog; now dialog={an.get('dialog')!r}, "
            f"sessions={an.get('sessions')!r}.", "AMB-2", analysis=n,
        )
    for n, att in enumerate(ctx.out.get("attachments") or []):
        if not isinstance(att, dict) or not (_is_int(att.get("dialog")) and att["dialog"] in removed):
            continue
        e = att["dialog"]
        _, sidx = targets(e)
        del att["dialog"]
        if sidx is not None:
            att["session"] = _merge_index(att.get("session"), [sidx])
            ctx.report.add(
                "T10b", INFERRED,
                f"attachments[{n}].dialog={e} pointed at a removed Dialog; replaced by session={att['session']!r}.",
                "AMB-2", attachment=n,
            )
        else:
            ctx.report.add(
                "T10b", UNRESOLVED,
                f"attachments[{n}].dialog={e} pointed at a removed Dialog with no Session to re-point to; "
                "the attachment now has neither dialog nor session.", "AMB-2", attachment=n,
            )


def _step_t13_unwrap_signed(ctx: _Context) -> None:
    """T13: a signed vCon is migrated as its unsigned payload; it must be signed again.

    ``alg: "none"`` is no longer permitted, so such a vCon is flagged explicitly.
    The migration never signs.
    """
    out = ctx.out
    if "ciphertext" in out and ("recipients" in out or "protected" in out):
        raise MigrationError("T13: the input is an encrypted (JWE) vCon; decrypt it before migrating")
    if "payload" in out and "signatures" in out:
        try:
            raw = out["payload"]
            payload = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
        except Exception as e:
            raise MigrationError(f"T13: could not decode the signed vCon payload: {e}") from e
        if not isinstance(payload, dict):
            raise MigrationError("T13: the signed vCon payload is not a JSON object")
        algs = []
        for sig in out.get("signatures") or []:
            try:
                hdr = sig.get("protected")
                if hdr:
                    algs.append(json.loads(base64.urlsafe_b64decode(hdr + "=" * (-len(hdr) % 4))).get("alg"))
                if isinstance(sig.get("header"), dict) and "alg" in sig["header"]:
                    algs.append(sig["header"]["alg"])
            except Exception:
                continue
        ctx.out = payload
        ctx.report.resign_required = True
        ctx.report.add(
            "T13", UNRESOLVED,
            "The input was signed. It was migrated as the unsigned payload; the signature was dropped. "
            "Re-signing is required, and signing changes updated_at (4.1.6).", None,
        )
        if any(isinstance(a, str) and a.lower() == "none" for a in algs):
            ctx.report.add(
                "T13", UNRESOLVED,
                "A signature used alg 'none', which 0.5.0 forbids; sign again with a permitted algorithm.", None,
            )
    ctx.src = copy.deepcopy(ctx.out)
    ctx.report.source_version = ctx.out.get("vcon")


def _step_t14_extensions(ctx: _Context) -> None:
    """T14: ``extensions`` must list every extension in use (MUST, was SHOULD)."""
    names, unnamed = extensions_in_use(ctx.out)
    listed = ctx.out.get("extensions")
    listed = list(listed) if isinstance(listed, list) else []
    added = []
    for name in sorted(names):
        if name not in listed:
            listed.append(name)
            added.append(name)
    for name in ctx.out.get("critical") or []:
        if isinstance(name, str) and name not in listed:
            listed.append(name)
            added.append(name)
    if added:
        ctx.out["extensions"] = listed
        ctx.report.add("T14", INFERRED, f"Added extension name(s) {added} to extensions.", None, added=added)
    if unnamed and not listed:
        ctx.report.add(
            "T14", UNRESOLVED,
            "Values outside the core vocabulary are in use but their defining extension cannot be identified: "
            + "; ".join(unnamed) + ". extensions was not changed.", None, uses=unnamed,
        )


def _step_t15_duplicate_headers(ctx: _Context) -> None:
    """T15: duplicate header parameters in signed or encrypted forms are tolerated on read."""
    if ctx.report.resign_required:
        ctx.report.add(
            "T15", INFO,
            "Header parameters repeated across JWS headers are not checked or rejected on read; "
            "writers must not emit duplicates in 0.5.0.",
        )


# T11 and T12 are renames at the top level; implemented with an order-preserving helper.
def _rename_top(ctx: _Context, old: str, new: str, step: str) -> None:
    if old in ctx.out:
        ctx.out = _rename_key(ctx.out, old, new)
        ctx.report.add(step, INFO, f"Renamed '{old}' to '{new}'.")


def _step_t11(ctx: _Context) -> None:
    """T11: ``redacted`` -> ``redacted_from`` (same fields)."""
    _rename_top(ctx, "redacted", "redacted_from", "T11")


def _step_t12(ctx: _Context) -> None:
    """T12: ``amended`` -> ``amended_from`` (same fields)."""
    _rename_top(ctx, "amended", "amended_from", "T12")


@dataclass(frozen=True)
class MigrationStep:
    id: str
    title: str
    source: str  # where the draft says it
    func: Callable[[_Context], None]


#: One entry per step of the ordered transform table (Appendix A.1), in execution order.
MIGRATION_STEPS: List[MigrationStep] = [
    MigrationStep("T13", "Signed input: migrate the payload, require re-signing", "A.1 bullet 11; 6.2.2", _step_t13_unwrap_signed),
    MigrationStep("T15", "Duplicate header parameters tolerated on read", "A.1 bullet 13", _step_t15_duplicate_headers),
    MigrationStep("T1", "vcon 0.4.0 -> 0.5.0", "A.1 bullet 1", _step_t1_version),
    MigrationStep("T8", "text Dialog parties -> sender; all parties to Session", "A.1 bullet 6", _step_t8_text_parties),
    MigrationStep("T9", "incomplete Dialog parties -> originator/first", "A.1 bullet 6", _step_t9_incomplete_parties),
    MigrationStep("T9b", "other Dialog parties kept; union to Session", "4.5.4 (A.1 silent)", _step_t9b_recording_parties),
    MigrationStep("T6", "Dialog originator -> Session originator", "A.1 bullet 5", _step_t6_originator),
    MigrationStep("T2", "Add a Session referencing all Dialogs", "A.1 bullet 2", _step_t2_sessions),
    MigrationStep("T7", "recording-set Dialog -> Session", "A.1 bullet 9", _step_t7_recording_sets),
    MigrationStep("T3", "party_history -> Events", "A.1 bullet 3", _step_t3_party_history),
    MigrationStep("T4", "transfer Dialog -> transfer Events (with T5 Session references)", "A.1 bullet 4", _step_t4_transfers),
    MigrationStep("T10", "Removed Dialogs -> {} in place", "A.1 bullet 10; 4.5.1", _step_t10_blank_removed),
    MigrationStep("T10b", "Re-point analysis/attachment references to removed Dialogs", "AMB-2", _step_t10b_retarget),
    MigrationStep("T11", "redacted -> redacted_from", "A.1 bullet 7", _step_t11),
    MigrationStep("T12", "amended -> amended_from", "A.1 bullet 8", _step_t12),
    MigrationStep("T14", "extensions lists every extension in use", "A.1 bullet 12; 4.1.3", _step_t14_extensions),
]


def migrate_0_4_0_to_0_5_0(vcon: Any, *, strict: bool = False) -> MigrationResult:
    """Migrate a 0.4.0 vCon dict (or JSON string) to 0.5.0.

    Args:
        vcon: The 0.4.0 vCon as a dict or JSON string. A signed vCon (JWS general
            form) is migrated as its unsigned payload. The input is not modified.
        strict: When True, raise :class:`MigrationError` instead of using a
            fallback for a MUST field that cannot be sourced from the input.

    Returns:
        ``MigrationResult(vcon, report)``: the 0.5.0 dict and the
        :class:`MigrationReport` listing every inferred value, fallback and
        unresolved item.

    Raises:
        MigrationError: the input is not a 0.4.0 vCon, is encrypted, or (strict)
            a required field has no source.
    """
    if isinstance(vcon, (str, bytes)):
        try:
            vcon = json.loads(vcon)
        except json.JSONDecodeError as e:
            raise MigrationError(f"input is not valid JSON: {e}") from e
    if not isinstance(vcon, dict):
        raise MigrationError("input must be a vCon dict or JSON string")

    data = copy.deepcopy(vcon)
    report = MigrationReport(strict=strict)
    ctx = _Context(data, strict, report)

    version = data.get("vcon")
    if version is not None and version != SOURCE_VERSION and not ("payload" in data and "signatures" in data):
        raise MigrationError(
            f"cannot migrate: input vcon is {version!r}, expected {SOURCE_VERSION!r}"
        )
    for step in MIGRATION_STEPS:
        report.steps_run.append(step.id)
        step.func(ctx)
        if step.id == "T13":
            v = ctx.out.get("vcon")
            if v is not None and v != SOURCE_VERSION:
                raise MigrationError(f"cannot migrate: input vcon is {v!r}, expected {SOURCE_VERSION!r}")
            if v is None:
                report.add("T13", INFO, "Input has no 'vcon' parameter; treated as 0.4.0.")

    out = ctx.out
    if ctx.sessions:
        out["sessions"] = ctx.sessions
    if ctx.events:
        out["events"] = ctx.events

    # Lawful basis attachments keep their 0.4.0 scope (dialog). 0.5.0 scopes them with
    # session plus party; adding a Session reference would be inventing a scope.
    for n, att in enumerate(out.get("attachments") or []):
        if isinstance(att, dict) and att.get("purpose") == "lawful_basis" and "session" not in att:
            report.add(
                "post", INFO,
                f"attachments[{n}] is a lawful_basis attachment scoped by dialog only; it was left as is. "
                "0.5.0 scopes a lawful basis to Sessions with 'session' (plus 'party'); add it if it covers the Session.",
                None, attachment=n,
            )

    # Post-check: the result must satisfy the core-05 rules; anything left is reported.
    from .dialog import Dialog

    errors, _ = validate_vcon_dict(out, Dialog.MIME_TYPES)
    for err in errors:
        report.add("post", UNRESOLVED, f"Result does not validate: {err}")
    logger.info("Migrated vCon %s to 0.5.0: %s", out.get("uuid"), report.summary())
    return MigrationResult(out, report)
