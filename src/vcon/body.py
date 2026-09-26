"""Helpers for decoding vCon attachment/analysis/dialog bodies.

Under ``draft-ietf-vcon-vcon-core-04`` section 2.3.2, when ``encoding`` is
``"json"`` the ``body`` field is the JSON *value* itself (object, array,
string, number, bool, or ``null``) rather than a ``json.dumps``-serialized
string. Earlier drafts (and adapters/generators written against them, plus
some helpers in this library prior to 0.10.0) instead stored the JSON
representation of the value as a string body.

``decode_body`` lets every reader in this library -- and callers of it --
accept either shape without special-casing each call site. It is exported
both as a module-level function and as ``Vcon.decoded_body`` for
discoverability.
"""

from typing import Any, Dict, Optional
import json

__all__ = ["decode_body"]


def decode_body(entry: Optional[Dict[str, Any]]) -> Any:
    """Return the decoded ``body`` of an attachment, analysis, or dialog entry.

    If ``encoding`` is ``"json"`` (or absent -- structured bodies were most
    commonly written without an explicit encoding under -02 conventions) and
    ``body`` is a string, the string is parsed as JSON and the resulting
    value is returned. This accepts both:

    - vCons written under -02 conventions (or by this library prior to
      0.10.0), where a JSON body was serialized to a string, and
    - -04-conformant vCons, where ``body`` is already the decoded value.

    Any other shape -- an already-decoded value, a ``base64url``/``none``
    encoded body, or a string that fails to parse as JSON -- is returned
    unchanged.

    :param entry: an attachment, analysis, or dialog dict, or ``None``
    :type entry: dict or None
    :return: the decoded body, or ``None`` if there is no body to decode
    :rtype: Any
    """
    if not entry:
        return None

    body = entry.get("body")
    if body is None:
        return None

    encoding = entry.get("encoding")
    if isinstance(body, str) and encoding in (None, "json"):
        try:
            return json.loads(body)
        except (ValueError, TypeError):
            return body

    return body
