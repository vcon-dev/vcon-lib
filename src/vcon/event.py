"""Event Object (draft-ietf-vcon-vcon-core-05, section 4.3) and the events array.

An Event is a point-in-time occurrence inside one or more Sessions: a party
joining or dropping, a key press, a call transfer step, or a change of the
parties contributing to a recording channel.

The per-type parameter applicability table of section 4.3.1.5 is held in
``EVENT_PARAMETER_RULES`` and enforced by :func:`validate_event` and by
``Vcon.is_valid()``.

Rule codes (section 4.3.1.5):

* ``M``  the parameter MUST be present
* ``O``  the parameter is optional
* ``SN`` the parameter SHOULD NOT be present (reported as a warning)
* ``X``  the parameter MUST NOT be present
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from dateutil import parser
from datetime import datetime

logger = logging.getLogger(__name__)

PARTY_EVENT_TYPES = ("join", "drop", "hold", "unhold", "mute", "unmute")
KEY_EVENT_TYPES = ("keydown", "keyup")
TRANSFER_EVENT_TYPES = (
    "consultation-start",
    "blind-transfer",
    "consultative-transfer",
    "transfer-abandoned",
)
CHANNEL_CONTRIBUTORS_EVENT_TYPE = "channel-contributors"

#: Every Event type token defined by core-05 (section 4.3.1).
CORE_EVENT_TYPES = (
    PARTY_EVENT_TYPES
    + KEY_EVENT_TYPES
    + TRANSFER_EVENT_TYPES
    + (CHANNEL_CONTRIBUTORS_EVENT_TYPE,)
)

#: Event parameters other than ``type`` and ``time``, in the order of 4.3.
EVENT_PARAMETERS = (
    "type",
    "time",
    "sessions",
    "party",
    "dialog",
    "channel",
    "contributors",
    "button",
    "transferee",
    "transfer_target",
    "consultation",
    "target_session",
)

_X_ALL_TRANSFER = {
    "transferee": "X",
    "transfer_target": "X",
    "consultation": "X",
    "target_session": "X",
}


def _rules(**overrides: str) -> Dict[str, str]:
    base = {
        "type": "M",
        "time": "M",
        "sessions": "M",
        "party": "M",
        "dialog": "SN",
        "channel": "X",
        "contributors": "X",
        "button": "X",
    }
    base.update(_X_ALL_TRANSFER)
    base.update(overrides)
    return base


#: Parameter applicability by Event type (section 4.3.1.5 tables).
EVENT_PARAMETER_RULES: Dict[str, Dict[str, str]] = {}
for _t in PARTY_EVENT_TYPES:
    EVENT_PARAMETER_RULES[_t] = _rules()
for _t in KEY_EVENT_TYPES:
    EVENT_PARAMETER_RULES[_t] = _rules(button="M")
EVENT_PARAMETER_RULES["consultation-start"] = _rules(
    transferee="M", transfer_target="M", consultation="M", target_session="X"
)
EVENT_PARAMETER_RULES["blind-transfer"] = _rules(
    transferee="M", transfer_target="M", consultation="X", target_session="M"
)
EVENT_PARAMETER_RULES["consultative-transfer"] = _rules(
    transferee="M", transfer_target="M", consultation="M", target_session="M"
)
EVENT_PARAMETER_RULES["transfer-abandoned"] = _rules(
    transferee="M", transfer_target="O", consultation="O", target_session="X"
)
EVENT_PARAMETER_RULES[CHANNEL_CONTRIBUTORS_EVENT_TYPE] = {
    "type": "M",
    "time": "M",
    "sessions": "X",
    "party": "X",
    "dialog": "M",
    "channel": "M",
    "contributors": "O",
    "button": "X",
    "transferee": "X",
    "transfer_target": "X",
    "consultation": "X",
    "target_session": "X",
}
del _t


def _is_index(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_index_or_list(value: Any) -> bool:
    if _is_index(value):
        return True
    return isinstance(value, list) and all(_is_index(v) for v in value)


def validate_event(
    event: Any,
    *,
    party_count: Optional[int] = None,
    dialog_count: Optional[int] = None,
    session_count: Optional[int] = None,
    label: str = "Event",
) -> Tuple[List[str], List[str]]:
    """Validate one Event Object dict against core-05 section 4.3.

    Returns ``(errors, warnings)``. ``SN`` violations are warnings, ``M`` and
    ``X`` violations are errors. An Event whose type is not a core token is only
    checked for ``type`` and ``time`` (section 2.5: it belongs to an extension).
    Index values are range-checked only when the matching count is supplied.
    """
    errors: List[str] = []
    warnings: List[str] = []
    if not isinstance(event, dict):
        return [f"{label} must be a dictionary."], warnings

    etype = event.get("type")
    if not isinstance(etype, str) or not etype:
        errors.append(f"{label} is missing required field: type")
    if "time" not in event:
        errors.append(f"{label} is missing required field: time")
    else:
        try:
            if not isinstance(event["time"], str):
                raise ValueError("not a string")
            parser.parse(event["time"])
        except Exception:
            errors.append(f"{label} has an invalid 'time' format. Must be an ISO 8601 datetime string.")

    rules = EVENT_PARAMETER_RULES.get(etype) if isinstance(etype, str) else None
    if rules is not None:
        for param, code in rules.items():
            present = param in event
            if code == "M" and not present:
                errors.append(f"{label} of type '{etype}' is missing required field: {param}")
            elif code == "X" and present:
                errors.append(f"{label} of type '{etype}' must not have field: {param}")
            elif code == "SN" and present:
                warnings.append(f"{label} of type '{etype}' should not have field: {param}")

    # Type and range checks on the parameters that are present.
    def check_index(param: str, count: Optional[int], noun: str) -> None:
        if param not in event:
            return
        val = event[param]
        if not _is_index(val):
            errors.append(f"{label} field '{param}' must be a non-negative integer.")
        elif count is not None and val >= count:
            errors.append(f"{label} references invalid {noun} index: {val}")

    for param, count, noun in (
        ("party", party_count, "party"),
        ("transferee", party_count, "party"),
        ("transfer_target", party_count, "party"),
        ("consultation", session_count, "session"),
        ("target_session", session_count, "session"),
    ):
        check_index(param, count, noun)

    if "dialog" in event:
        val = event["dialog"]
        if _is_index(val):
            idxs = [val]
        elif isinstance(val, list) and etype not in CORE_EVENT_TYPES and all(_is_index(v) for v in val):
            idxs = val  # extension event types may use an array (4.3.5)
        else:
            idxs = []
            errors.append(f"{label} field 'dialog' must be a non-negative integer.")
        for v in idxs:
            if dialog_count is not None and v >= dialog_count:
                errors.append(f"{label} references invalid dialog index: {v}")

    if "channel" in event and not _is_index(event["channel"]):
        errors.append(f"{label} field 'channel' must be a non-negative integer.")

    if "sessions" in event:
        val = event["sessions"]
        if not _is_index_or_list(val):
            errors.append(f"{label} field 'sessions' must be an index or a list of indices.")
        else:
            idxs = val if isinstance(val, list) else [val]
            if etype in TRANSFER_EVENT_TYPES and isinstance(val, list):
                errors.append(
                    f"{label} of type '{etype}' must reference a single session index in 'sessions'."
                )
            for v in idxs:
                if session_count is not None and v >= session_count:
                    errors.append(f"{label} references invalid session index: {v}")

    if "contributors" in event:
        val = event["contributors"]
        if val is not None and not _is_index_or_list(val):
            errors.append(f"{label} field 'contributors' must be an index, a list of indices or null.")
        else:
            for v in ([] if val is None else (val if isinstance(val, list) else [val])):
                if party_count is not None and v >= party_count:
                    errors.append(f"{label} references invalid party index: {v}")

    if "button" in event and not isinstance(event["button"], str):
        errors.append(f"{label} field 'button' must be a string.")

    return errors, warnings


class Event:
    """An Event Object (core-05 section 4.3).

    Args:
        type: Event type token, for example ``"join"`` or ``"blind-transfer"``.
        time: When the event occurred (``datetime`` or ISO 8601 string).
        sessions: Session index or list of indices (not for channel-contributors).
        party: Party index (not for channel-contributors).
        dialog: Dialog index (channel-contributors; SHOULD NOT be used otherwise).
        channel: Channel index (channel-contributors only).
        contributors: Party index, list of indices, or ``None`` (channel-contributors only).
        button: DTMF digit or key label (keydown and keyup only).
        transferee, transfer_target: Party indices (transfer types).
        consultation, target_session: Session indices (transfer types).
        validate: Apply the parameter applicability table and raise
            ``ValueError`` on an ``M``/``X`` violation (default True).
        **extra: Parameters defined by a vCon extension.
    """

    def __init__(
        self,
        type: str,
        time: Union[datetime, str],
        sessions: Optional[Union[int, List[int]]] = None,
        party: Optional[int] = None,
        dialog: Optional[Union[int, List[int]]] = None,
        channel: Optional[int] = None,
        contributors: Optional[Union[int, List[int]]] = None,
        button: Optional[str] = None,
        transferee: Optional[int] = None,
        transfer_target: Optional[int] = None,
        consultation: Optional[int] = None,
        target_session: Optional[int] = None,
        validate: bool = True,
        **extra: Any,
    ) -> None:
        if isinstance(time, datetime):
            time = time.isoformat()
        self.type = type
        self.time = time
        self.sessions = sessions
        self.party = party
        self.dialog = dialog
        self.channel = channel
        self.contributors = contributors
        self.button = button
        self.transferee = transferee
        self.transfer_target = transfer_target
        self.consultation = consultation
        self.target_session = target_session
        self.extra = {k: v for k, v in extra.items() if v is not None}
        if validate:
            errors, warnings = validate_event(self.to_dict())
            for w in warnings:
                logger.warning(w)
            if errors:
                raise ValueError("; ".join(errors))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize, omitting parameters that are ``None``."""
        out: Dict[str, Any] = {}
        for name in EVENT_PARAMETERS:
            value = getattr(self, name)
            if value is not None:
                out[name] = value
        out.update(self.extra)
        return out

    @classmethod
    def from_dict(cls, data: Dict[str, Any], validate: bool = False) -> "Event":
        known = {k: data[k] for k in EVENT_PARAMETERS if k in data}
        extra = {k: v for k, v in data.items() if k not in EVENT_PARAMETERS}
        return cls(validate=validate, **known, **extra)
