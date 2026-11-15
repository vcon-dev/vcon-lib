"""Session Object and Session_Reference Object (core-05 sections 4.2 and 4.2.8).

A Session groups the Dialog and Event Objects of one conversation (or part of
one) and records its receivers. A Session Object with no parameters is allowed.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from dateutil import parser

#: Session_Reference ``type`` tokens defined by core-05 (4.2.8.2). Values
#: defined by a vCon extension are also allowed.
SESSION_REFERENCE_TYPES = ("child", "peer", "precursor", "breakout")

SESSION_PARAMETERS = (
    "start",
    "duration",
    "parties",
    "originator",
    "session_id",
    "sessions",
    "dialog",
)


def _is_index(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


class SessionReference:
    """Session_Reference Object: how another Session relates to this one."""

    def __init__(self, session: int, type: str, description: Optional[str] = None) -> None:
        if not _is_index(session):
            raise ValueError("Session_Reference 'session' must be a non-negative integer")
        if not isinstance(type, str) or not type:
            raise ValueError("Session_Reference 'type' is required")
        self.session = session
        self.type = type
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"session": self.session, "type": self.type}
        if self.description is not None:
            out["description"] = self.description
        return out


class Session:
    """A Session Object.

    Args:
        start: Session start (``datetime`` or ISO 8601 string). SHOULD be present.
        duration: Session duration in seconds. Absent means the session has no end.
        parties: Indices of the receivers. The first one is the implied originator.
        originator: Index of the originator, only when it is not the first party.
        session_id: A SessionId Object (``{"local": ..., "remote": ...}``).
        sessions: Relationships to other Sessions (``SessionReference`` or dicts).
        dialog: Indices of the Dialog Objects that are part of the session.
    """

    def __init__(
        self,
        start: Optional[Union[datetime, str]] = None,
        duration: Optional[Union[int, float]] = None,
        parties: Optional[List[int]] = None,
        originator: Optional[int] = None,
        session_id: Optional[Dict[str, str]] = None,
        sessions: Optional[List[Union[SessionReference, Dict[str, Any]]]] = None,
        dialog: Optional[List[int]] = None,
    ) -> None:
        if isinstance(start, datetime):
            start = start.isoformat()
        elif isinstance(start, str):
            start = parser.parse(start).isoformat()
        self.start = start
        self.duration = duration
        self.parties = list(parties) if parties is not None else None
        self.originator = originator
        self.session_id = session_id
        self.sessions = list(sessions) if sessions is not None else None
        self.dialog = list(dialog) if dialog is not None else None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize, omitting parameters that are ``None``. An empty Session is ``{}``."""
        out: Dict[str, Any] = {}
        for name in SESSION_PARAMETERS:
            value = getattr(self, name)
            if value is None:
                continue
            if name == "sessions":
                value = [v.to_dict() if isinstance(v, SessionReference) else v for v in value]
            out[name] = value
        return out


def validate_session(
    session: Any,
    *,
    party_count: Optional[int] = None,
    dialog_count: Optional[int] = None,
    session_count: Optional[int] = None,
    label: str = "Session",
) -> Tuple[List[str], List[str]]:
    """Validate one Session Object dict. Returns ``(errors, warnings)``."""
    errors: List[str] = []
    warnings: List[str] = []
    if not isinstance(session, dict):
        return [f"{label} must be a dictionary."], warnings
    if not session:
        return errors, warnings  # an empty placeholder Session is permitted

    if "start" in session:
        try:
            if not isinstance(session["start"], str):
                raise ValueError("not a string")
            parser.parse(session["start"])
        except Exception:
            errors.append(f"{label} has an invalid 'start' format. Must be an ISO 8601 datetime string.")
    else:
        warnings.append(f"{label} should have a start parameter.")

    if "duration" in session:
        d = session["duration"]
        if isinstance(d, bool) or not isinstance(d, (int, float)) or d < 0:
            errors.append(f"{label} field 'duration' must be a non-negative number.")

    if "parties" in session:
        p = session["parties"]
        if not isinstance(p, list):
            errors.append(f"{label} field 'parties' must be a list.")
        else:
            for idx in p:
                if not _is_index(idx) or (party_count is not None and idx >= party_count):
                    errors.append(f"{label} references invalid party index: {idx}")
    else:
        warnings.append(f"{label} should have a parties parameter.")

    if "originator" in session:
        o = session["originator"]
        if not _is_index(o) or (party_count is not None and o >= party_count):
            errors.append(f"{label} references invalid party index: {o}")

    if "session_id" in session and not isinstance(session["session_id"], dict):
        errors.append(f"{label} field 'session_id' must be a SessionId Object.")

    if "dialog" in session:
        dl = session["dialog"]
        if not isinstance(dl, list):
            errors.append(f"{label} field 'dialog' must be a list.")
        else:
            for idx in dl:
                if not _is_index(idx) or (dialog_count is not None and idx >= dialog_count):
                    errors.append(f"{label} references invalid dialog index: {idx}")

    if "sessions" in session:
        refs = session["sessions"]
        if not isinstance(refs, list):
            errors.append(f"{label} field 'sessions' must be a list.")
        else:
            for n, ref in enumerate(refs):
                if not isinstance(ref, dict):
                    errors.append(f"{label} sessions[{n}] must be a dictionary.")
                    continue
                for req in ("session", "type"):
                    if req not in ref:
                        errors.append(f"{label} sessions[{n}] is missing required field: {req}")
                if "session" in ref:
                    if not _is_index(ref["session"]) or (
                        session_count is not None and ref["session"] >= session_count
                    ):
                        errors.append(f"{label} references invalid session index: {ref['session']}")
                if "type" in ref and not isinstance(ref["type"], str):
                    errors.append(f"{label} sessions[{n}] field 'type' must be a string.")
    return errors, warnings
