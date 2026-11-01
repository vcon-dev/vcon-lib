"""Structural validation of an unsigned vCon dict against core-05.

``validate_vcon_dict`` is the engine behind ``Vcon.is_valid()``. It works on
plain dicts so the migration code can reuse it.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple

from dateutil import parser

from .event import CORE_EVENT_TYPES, validate_event
from .session import SESSION_REFERENCE_TYPES, validate_session

SYNTAX_VERSION = "0.5.0"

CORE_DIALOG_TYPES = ("recording", "text", "incomplete")
#: Dialog types the library itself builds although core-05 does not define them.
LIBRARY_DIALOG_TYPES = ("audio", "video")
CORE_ENCODINGS = ("base64url", "json", "none")
CORE_DISPOSITIONS = (
    "no-answer",
    "congestion",
    "failed",
    "busy",
    "hung-up",
    "voicemail-no-message",
)

#: Extension names this library knows how to recognise, keyed by how they show up.
KNOWN_ATTACHMENT_PURPOSE_EXTENSIONS = {
    "lawful_basis": "lawful_basis",
    "wtf_transcription": "wtf_transcription",
}
KNOWN_ANALYSIS_TYPE_EXTENSIONS = {
    "wtf_transcription": "wtf_transcription",
}

#: Removed in 0.5.0; their presence means the document is still 0.4.0 shaped.
LEGACY_TOP_LEVEL = {"redacted": "redacted_from", "amended": "amended_from"}
LEGACY_DIALOG_PARAMS = (
    "party_history",
    "originator",
    "transferee",
    "transferor",
    "transfer_target",
    "original",
    "consultation",
    "target_dialog",
    "recordings",
    "recording_set",
)
LEGACY_DIALOG_TYPES = ("transfer", "recording-set")

_REDACTED_REF_RE = re.compile(r"__REDACTED_REF_(\d{1,5})(?!\d)")


def mediatype_ok(mediatype: Any, known: List[str]) -> bool:
    """True if ``mediatype`` is acceptable for a Dialog.

    Media type parameters (``; boundary=...``) are ignored. Any ``multipart/``,
    ``message/`` or ``text/`` subtype is accepted, since the draft's examples use
    ``multipart/alternative`` and the list in the draft is open-ended.
    """
    if not isinstance(mediatype, str):
        return False
    base = mediatype.split(";", 1)[0].strip().lower()
    if base in known:
        return True
    return base.startswith(("multipart/", "message/", "text/"))


def _is_index(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _flatten_parties(value: Any) -> List[Any]:
    out: List[Any] = []
    for v in _as_list(value):
        if isinstance(v, list):
            out.extend(v)
        else:
            out.append(v)
    return out


def extensions_in_use(vcon: Dict[str, Any]) -> Tuple[Set[str], List[str]]:
    """Find the vCon extensions the document uses.

    Returns ``(names, unnamed)``. ``names`` holds extension names this library
    recognises (``lawful_basis``, ``wtf_transcription``). ``unnamed`` describes
    each use of a value outside the core vocabulary (an Event type, Dialog type,
    encoding, disposition or Session_Reference type) whose defining extension
    cannot be identified from the document alone.
    """
    names: Set[str] = set()
    unnamed: List[str] = []

    for i, att in enumerate(_as_list(vcon.get("attachments"))):
        if isinstance(att, dict):
            purpose = att.get("purpose")
            if purpose in KNOWN_ATTACHMENT_PURPOSE_EXTENSIONS:
                names.add(KNOWN_ATTACHMENT_PURPOSE_EXTENSIONS[purpose])
            enc = att.get("encoding")
            if enc is not None and enc not in CORE_ENCODINGS:
                unnamed.append(f"attachments[{i}] encoding '{enc}'")
    for i, an in enumerate(_as_list(vcon.get("analysis"))):
        if isinstance(an, dict):
            if an.get("type") in KNOWN_ANALYSIS_TYPE_EXTENSIONS:
                names.add(KNOWN_ANALYSIS_TYPE_EXTENSIONS[an["type"]])
            enc = an.get("encoding")
            if enc is not None and enc not in CORE_ENCODINGS:
                unnamed.append(f"analysis[{i}] encoding '{enc}'")
    for i, d in enumerate(_as_list(vcon.get("dialog"))):
        if isinstance(d, dict) and d:
            enc = d.get("encoding")
            if enc is not None and enc not in CORE_ENCODINGS:
                unnamed.append(f"dialog[{i}] encoding '{enc}'")
            disp = d.get("disposition")
            if d.get("type") == "incomplete" and disp is not None and disp not in CORE_DISPOSITIONS:
                unnamed.append(f"dialog[{i}] disposition '{disp}'")
    for i, e in enumerate(_as_list(vcon.get("events"))):
        if isinstance(e, dict):
            t = e.get("type")
            if t is not None and t not in CORE_EVENT_TYPES:
                unnamed.append(f"events[{i}] type '{t}'")
    for i, s in enumerate(_as_list(vcon.get("sessions"))):
        if isinstance(s, dict):
            for j, ref in enumerate(_as_list(s.get("sessions"))):
                if isinstance(ref, dict):
                    t = ref.get("type")
                    if t is not None and t not in SESSION_REFERENCE_TYPES:
                        unnamed.append(f"sessions[{i}].sessions[{j}] type '{t}'")
    return names, unnamed


def _scan_redacted_refs(obj: Any, found: Set[int]) -> None:
    if isinstance(obj, str):
        for m in _REDACTED_REF_RE.finditer(obj):
            found.add(int(m.group(1)))
    elif isinstance(obj, list):
        for v in obj:
            _scan_redacted_refs(v, found)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _scan_redacted_refs(v, found)


def validate_vcon_dict(
    vcon: Dict[str, Any], dialog_mime_types: List[str]
) -> Tuple[List[str], List[str]]:
    """Validate an unsigned vCon dict. Returns ``(errors, warnings)``."""
    errors: List[str] = []
    warnings: List[str] = []

    # --- required fields and version -------------------------------------
    for field in ("uuid", "created_at"):
        if field not in vcon:
            errors.append(f"Missing required field: {field}")
    for ts in ("created_at", "updated_at"):
        if ts in vcon:
            try:
                parser.parse(vcon[ts])
            except Exception as e:
                errors.append(
                    f"Invalid {ts} format. Must be an ISO 8601 datetime string: {str(e)}"
                )
    if "vcon" in vcon and vcon["vcon"] != SYNTAX_VERSION:
        errors.append(
            f"Unsupported vcon syntax version '{vcon['vcon']}': this library writes "
            f"'{SYNTAX_VERSION}'. Migrate a 0.4.0 vCon with migrate_0_4_0_to_0_5_0()."
        )
    for old, new in LEGACY_TOP_LEVEL.items():
        if old in vcon:
            errors.append(f"Legacy 0.4.0 parameter '{old}' was renamed '{new}' in 0.5.0.")

    # --- parties ----------------------------------------------------------
    parties = vcon.get("parties", [])
    if "parties" in vcon:
        if not isinstance(parties, list):
            errors.append("Field 'parties' must be a list.")
            parties = []
        else:
            for i, party in enumerate(parties):
                if not isinstance(party, dict):
                    errors.append(f"Party at index {i} must be a dictionary.")
    party_count = len(parties)

    dialogs = vcon.get("dialog", [])
    if not isinstance(dialogs, list):
        errors.append("Field 'dialog' must be a list.")
        dialogs = []
    dialog_count = len(dialogs)
    sessions = vcon.get("sessions", [])
    if not isinstance(sessions, list):
        errors.append("Field 'sessions' must be a list.")
        sessions = []
    session_count = len(sessions)
    events = vcon.get("events", [])
    if not isinstance(events, list):
        errors.append("Field 'events' must be a list.")
        events = []
    attachments = vcon.get("attachments", [])
    if "attachments" in vcon and not isinstance(attachments, list):
        errors.append("Field 'attachments' must be a list.")
        attachments = []
    analyses = vcon.get("analysis", [])
    if "analysis" in vcon and not isinstance(analyses, list):
        errors.append("Field 'analysis' must be a list.")
        analyses = []
    redacted = isinstance(vcon.get("redacted_from"), dict)

    # --- redacted_from / amended_from ------------------------------------
    if "redacted_from" in vcon and "amended_from" in vcon:
        errors.append("redacted_from and amended_from are mutually exclusive.")
    rf = vcon.get("redacted_from")
    if "redacted_from" in vcon:
        if not isinstance(rf, dict):
            errors.append("Field 'redacted_from' must be an object.")
        else:
            if "type" not in rf:
                errors.append("redacted_from is missing required field: type")
            if "url" in rf and "content_hash" not in rf:
                errors.append("redacted_from with url must include content_hash.")
    af = vcon.get("amended_from")
    if "amended_from" in vcon:
        if not isinstance(af, dict):
            errors.append("Field 'amended_from' must be an object.")
        else:
            if "uuid" not in af and "url" not in af:
                errors.append("amended_from must include uuid, or an external reference (url).")
            if "url" in af and "content_hash" not in af:
                errors.append("amended_from with url must include content_hash.")

    # --- extensions / critical -------------------------------------------
    ext_listed = vcon.get("extensions", [])
    if "extensions" in vcon and (
        not isinstance(ext_listed, list) or not all(isinstance(x, str) for x in ext_listed)
    ):
        errors.append("Field 'extensions' must be a list of strings.")
        ext_listed = []
    crit = vcon.get("critical", [])
    if "critical" in vcon and (
        not isinstance(crit, list) or not all(isinstance(x, str) for x in crit)
    ):
        errors.append("Field 'critical' must be a list of strings.")
        crit = []
    for name in crit:
        if name not in ext_listed:
            errors.append(
                f"Extension '{name}' is listed in critical but not in extensions."
            )
    used, unnamed = extensions_in_use(vcon)
    for name in sorted(used):
        if name not in ext_listed:
            errors.append(
                f"Extension '{name}' is in use but is not listed in the extensions parameter."
            )
    if unnamed and not ext_listed:
        errors.append(
            "Values outside the core vocabulary are in use but the extensions parameter "
            "lists no extension: " + "; ".join(unnamed) + "."
        )

    # --- dialog -----------------------------------------------------------
    for i, dialog in enumerate(dialogs):
        if not isinstance(dialog, dict):
            errors.append(f"Dialog at index {i} must be a dictionary.")
            continue
        if not dialog:
            continue  # empty placeholder Dialog Object (4.5.1)
        dialog_type = dialog.get("type")
        if "type" not in dialog:
            errors.append(f"Dialog at index {i} is missing required field: type")
        elif dialog_type in LEGACY_DIALOG_TYPES:
            errors.append(
                f"Dialog at index {i} has type '{dialog_type}', which was removed in 0.5.0 "
                "(use Events and Sessions; migrate with migrate_0_4_0_to_0_5_0())."
            )
        elif (
            dialog_type not in CORE_DIALOG_TYPES
            and dialog_type not in LIBRARY_DIALOG_TYPES
            and not ext_listed
        ):
            # A Dialog type outside the core vocabulary must come from a vCon
            # extension, which has to be listed in extensions (4.1.3).
            errors.append(f"Dialog at index {i} has an invalid type: {dialog_type}")
        for legacy in LEGACY_DIALOG_PARAMS:
            if legacy in dialog:
                errors.append(
                    f"Dialog at index {i} has parameter '{legacy}', which was removed in 0.5.0."
                )
        if dialog_type == "incomplete":
            if "disposition" not in dialog:
                errors.append(f"Dialog at index {i} of type 'incomplete' must have a disposition.")
            for forbidden in (
                "mediatype", "filename", "body", "encoding", "url", "content_hash",
                "message_id", "redacted_segments",
            ):
                if forbidden in dialog:
                    errors.append(
                        f"Dialog at index {i} of type 'incomplete' must not have field: {forbidden}"
                    )

        if "parties" in dialog:
            dp = dialog["parties"]
            if not isinstance(dp, (list, int)) or isinstance(dp, bool):
                errors.append(f"Dialog at index {i} field 'parties' must be a list.")
            else:
                for party_idx in _flatten_parties(dp):
                    if party_idx is None:
                        continue  # null placeholder for a channel with no contributor
                    if not _is_index(party_idx) or party_idx >= party_count:
                        errors.append(f"Dialog at index {i} references invalid party index: {party_idx}")
        if "start" in dialog:
            try:
                parser.parse(dialog["start"])
            except Exception:
                errors.append(
                    f"Dialog at index {i} has an invalid 'start' format. Must be an ISO 8601 datetime string."
                )
        if dialog_type != "incomplete":
            has_content = "body" in dialog
            if "mediatype" in dialog:
                if not mediatype_ok(dialog["mediatype"], dialog_mime_types):
                    errors.append(
                        f"Dialog at index {i} has an invalid or missing mediatype: {dialog.get('mediatype')}"
                    )
            elif has_content:
                errors.append(
                    f"Dialog at index {i} has an invalid or missing mediatype: missing"
                )
        if "redacted_segments" in dialog:
            segs = dialog["redacted_segments"]
            if not isinstance(segs, list):
                errors.append(f"Dialog at index {i} field 'redacted_segments' must be a list.")
            else:
                for n, seg in enumerate(segs):
                    if not isinstance(seg, dict) or "start" not in seg or "end" not in seg:
                        errors.append(
                            f"Dialog at index {i} redacted_segments[{n}] requires start and end."
                        )

    # --- sessions ---------------------------------------------------------
    if (dialog_count or events) and not sessions:
        errors.append(
            "At least one Session Object MUST exist if the events array or the dialog array contains Objects."
        )
    for i, s in enumerate(sessions):
        e, w = validate_session(
            s,
            party_count=party_count,
            dialog_count=dialog_count,
            session_count=session_count,
            label=f"Session at index {i}",
        )
        errors.extend(e)
        warnings.extend(w)
    referenced_dialogs: Set[int] = set()
    for s in sessions:
        if isinstance(s, dict) and isinstance(s.get("dialog"), list):
            referenced_dialogs.update(x for x in s["dialog"] if _is_index(x))
    for i, d in enumerate(dialogs):
        if isinstance(d, dict) and d and i not in referenced_dialogs:
            warnings.append(f"Dialog at index {i} is not referenced by any Session Object.")

    # --- events -----------------------------------------------------------
    for i, ev in enumerate(events):
        e, w = validate_event(
            ev,
            party_count=party_count,
            dialog_count=dialog_count,
            session_count=session_count,
            label=f"Event at index {i}",
        )
        errors.extend(e)
        warnings.extend(w)
        if isinstance(ev, dict) and ev.get("type") == "channel-contributors" and _is_index(ev.get("dialog")):
            di = ev["dialog"]
            if di < dialog_count and isinstance(dialogs[di], dict) and dialogs[di].get("type") != "recording":
                errors.append(
                    f"Event at index {i} of type 'channel-contributors' must reference a 'recording' Dialog."
                )

    # --- attachments ------------------------------------------------------
    for i, attachment in enumerate(attachments):
        if not isinstance(attachment, dict):
            errors.append(f"Attachment at index {i} must be a dictionary.")
            continue
        if "purpose" not in attachment:
            errors.append(f"Attachment at index {i} is missing required field: purpose")
        has_inline = "body" in attachment and "encoding" in attachment
        has_external = "url" in attachment and "content_hash" in attachment
        if not (has_inline or has_external or redacted):
            errors.append(f"Attachment at index {i} must include body+encoding or url+content_hash.")
        if "encoding" in attachment and attachment["encoding"] not in CORE_ENCODINGS and not ext_listed:
            errors.append(f"Attachment at index {i} has invalid encoding: {attachment['encoding']}")
        if "body" in attachment and attachment["body"] != "" and "mediatype" not in attachment:
            errors.append(
                f"Attachment at index {i} is missing required field: mediatype (needed for inline content)"
            )
        if "start" not in attachment:
            errors.append(f"Attachment at index {i} is missing required field: start")
        if "party" not in attachment:
            errors.append(f"Attachment at index {i} is missing required field: party")
        elif not _is_index(attachment["party"]) or attachment["party"] >= party_count:
            errors.append(f"Attachment at index {i} references invalid party index: {attachment['party']}")
        if "dialog" not in attachment and "session" not in attachment:
            errors.append(
                f"Attachment at index {i} must have at least one of dialog or session."
            )
        if "dialog" in attachment:
            dv = attachment["dialog"]
            if not _is_index(dv) or dv >= dialog_count:
                errors.append(f"Attachment at index {i} references invalid dialog index: {dv}")
        if "session" in attachment:
            sv = attachment["session"]
            vals = sv if isinstance(sv, list) else [sv]
            if not vals and isinstance(sv, list):
                errors.append(f"Attachment at index {i} field 'session' must not be empty.")
            for v in vals:
                if not _is_index(v) or v >= session_count:
                    errors.append(f"Attachment at index {i} references invalid session index: {v}")

    # --- analysis ---------------------------------------------------------
    for i, analysis in enumerate(analyses):
        if not isinstance(analysis, dict):
            errors.append(f"Analysis at index {i} must be a dictionary.")
            continue
        for field in ("type", "vendor"):
            if field not in analysis:
                errors.append(f"Analysis at index {i} is missing required field: {field}")
        if "body" in analysis and analysis["body"] != "" and "encoding" not in analysis:
            errors.append(f"Analysis at index {i} is missing required field: encoding")
        if "encoding" in analysis and analysis["encoding"] not in CORE_ENCODINGS and not ext_listed:
            errors.append(f"Analysis at index {i} has invalid encoding: {analysis['encoding']}")
        for key, count, noun in (
            ("dialog", dialog_count, "dialog"),
            ("sessions", session_count, "session"),
            ("attachment", len(attachments), "attachment"),
            ("analysis", len(analyses), "analysis"),
        ):
            if key not in analysis:
                continue
            val = analysis[key]
            vals = val if isinstance(val, list) else [val]
            if not isinstance(val, (int, list)) or isinstance(val, bool):
                errors.append(f"Analysis at index {i} has an invalid '{key}' reference type.")
                continue
            for v in vals:
                if not _is_index(v) or v >= count:
                    errors.append(f"Analysis at index {i} references invalid {noun} index: {v}")
                elif key == "analysis" and v == i:
                    errors.append(f"Analysis at index {i} must not reference itself in analysis.")
        if not any(k in analysis for k in ("dialog", "sessions", "attachment", "analysis")):
            warnings.append(
                f"Analysis at index {i} should have at least one of dialog, sessions, attachment or analysis."
            )

    # --- redacted_strings -------------------------------------------------
    rs = vcon.get("redacted_strings")
    refs_declared: Set[int] = set()
    if "redacted_strings" in vcon:
        if not isinstance(rs, list):
            errors.append("Field 'redacted_strings' must be a list.")
        else:
            if len(rs) > 99999:
                errors.append("A vCon MUST NOT have more than 99999 redacted substrings.")
            for n, item in enumerate(rs):
                if not isinstance(item, dict) or not isinstance(item.get("ref"), int) or isinstance(item.get("ref"), bool):
                    errors.append(f"redacted_strings[{n}] requires an integer ref.")
                    continue
                if not 1 <= item["ref"] <= 99999:
                    errors.append(f"redacted_strings[{n}] ref must be between 1 and 99999.")
                if item["ref"] in refs_declared:
                    errors.append(f"redacted_strings[{n}] duplicates ref {item['ref']}.")
                refs_declared.add(item["ref"])
    found: Set[int] = set()
    _scan_redacted_refs({k: v for k, v in vcon.items() if k != "redacted_strings"}, found)
    for ref in sorted(found - refs_declared):
        errors.append(
            f"__REDACTED_REF_{ref} appears in the vCon but has no entry in redacted_strings."
        )

    return errors, warnings
