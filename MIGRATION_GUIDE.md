# Migration Guide

## Upgrading to library 1.0.4

1.0.4 is a fix release on vCon 0.5.0. Most code runs unchanged; check these:

| Before 1.0.4 | 1.0.4 |
| --- | --- |
| `add_wtf_transcription_attachment()` | deprecated (`DeprecationWarning`): the WTF draft stores a transcription as analysis. Use `add_wtf_transcription_analysis(transcript, segments, metadata, dialog_index=None, session_index=None, **kwargs)`; read it back with `vcon.find_analysis_by_type("wtf_transcription")` instead of `find_wtf_attachments()` |
| `add_tag()` on a vCon with no parties wrote `party: 0` silently | still writes party 0, but emits a `DeprecationWarning` (the vCon fails `is_valid()`); it will raise `ValueError` in 1.1. Add a party before the first tag. New `party=` argument (default 0); an index out of range raises `ValueError` |
| `is_valid()` did not check `content_hash` or lawful-basis bodies | errors for a malformed `content_hash` (`<algorithm>-<unpadded base64url digest>`, 86 characters for sha512, 43 for sha256) and for problems in a `lawful_basis` attachment body. Unknown lawful-basis proof types, hash algorithms and canonicalization methods are warnings |
| no check for `url` without `content_hash` | 1.0.4 and 1.0.5 warned; from 1.0.6 it is allowed on Dialog, Attachment and Analysis (still required on `redacted_from` and `amended_from`) |
| (no check) | `get_validation_warnings()` reports an `encoding: "json"` body that is a serialized JSON string |
| loading rewrote `created_at` into Python's ISO format (and an unparseable value crashed `Vcon()`) | `created_at` is kept exactly as written; `is_valid()` reports an unparseable value |
| `Dialog.add_inline_data()` took a str and hashed the base64url text | also takes `bytes` (encoded for you); `content_hash` is over the decoded content |
| `Dialog.generate_thumbnail()` was always the image version | dispatches to `generate_image_thumbnail(max_size)` or `generate_video_thumbnail(timestamp, width, height, quality)` |
| `ffmpeg` dependency (the wrong package: video helpers failed) | optional: `pip install "vcon[video]"` (ffmpeg-python) plus the ffmpeg binary |
| `authlib` for JWS | `joserfc`; `sign()`/`verify()` are unchanged and also accept EC and Ed25519 keys |

```python
from vcon import Vcon
from vcon.party import Party
from vcon.session import Session

vcon = Vcon.build_new()
vcon.add_party(Party(name="Alice"))  # before add_tag()
vcon.add_session(Session(start="2024-01-01T00:00:00Z", parties=[0]))
vcon.add_tag("category", "support")

# Was: vcon.add_wtf_transcription_attachment(...) and vcon.find_wtf_attachments()
vcon.add_wtf_transcription_analysis(
    transcript={"text": "Hello", "language": "en", "duration": 1.0, "confidence": 0.9},
    segments=[{"id": 0, "start": 0.0, "end": 1.0, "text": "Hello", "confidence": 0.9}],
    metadata={"created_at": "2024-01-01T00:00:00Z", "processed_at": "2024-01-01T00:00:05Z",
              "provider": "whisper", "model": "whisper-1"},
    session_index=0,
)
entry = vcon.find_analysis_by_type("wtf_transcription")
wtf_body = Vcon.decoded_body(entry)

is_valid, errors = vcon.is_valid()
warnings = vcon.get_validation_warnings()
```

## Migrating to vCon 0.5.0 (library 1.0.0)

Library 1.0.0 implements `draft-ietf-vcon-vcon-core-05` (syntax `"0.5.0"`). Readers accept 0.4.0 and 0.5.0;
writers emit 0.5.0. A vCon that declares `"vcon": "0.4.0"` is migrated when you load it:

```python
from vcon import Vcon, migrate_0_4_0_to_0_5_0, MigrationError

vcon = Vcon.load("old.vcon.json")      # or Vcon(dict), Vcon.build_from_json(text)
print(vcon.migration_report.summary())  # what was inferred, what needs a person

# Explicit form: returns the new dict and the report. strict=True raises MigrationError
# instead of using a documented fallback for a field the spec requires.
new_dict, report = migrate_0_4_0_to_0_5_0(old_dict, strict=False)

# Opt out and keep the 0.4.0 dict as it is (is_valid() will report it as not 0.5.0)
vcon = Vcon.load("old.vcon.json", migrate_legacy=False)
```

The migration follows Appendix A.1 of the draft, one function per step (`vcon.migration.MIGRATION_STEPS`).
Removed `transfer` and `recording-set` Dialogs become empty Dialog Objects (`{}`) in place, so every dialog,
analysis, attachment and event index stays valid. Where A.1 is silent the migration applies a documented default and
lists it in the report (`report.inferred`); anything it cannot resolve is in `report.unresolved`. Signed input is
not migrated on load, because migrating drops the signature: verify it, then call
`Vcon.migrate_0_4_0_to_0_5_0(signed)` (or the function), which migrates the unsigned payload; sign the result again
(`report.resign_required`). Input with no `vcon` parameter that already has `sessions`, `events`, `redacted_from`,
`amended_from` or `redacted_strings` is 0.5.0 and is refused. Persist `report.to_dict()` next to each migrated
record: it holds the original content of every removed Dialog and every value that was inferred or dropped.

Code that changes:

| 0.4.0 | 0.5.0 |
| --- | --- |
| `vcon.redacted`, `vcon.amended` | `vcon.redacted_from`, `vcon.amended_from` |
| `PartyHistory`, `Dialog(party_history=...)` | `Event` and `Vcon.add_event()` (`event` is now `type`, `sessions` set) |
| `Vcon.add_transfer_dialog()` | transfer `Event` types |
| `Dialog(originator=...)` | `Session(originator=...)` |
| `Dialog(parties=[sender, *receivers])` | `Dialog(parties=[sender])`; receivers in `Session(parties=[...])` |
| `recording-set` Dialog | `Session(dialog=[...])` |
| attachments always `dialog=0` by default | pass `dialog` or `session`; with neither, the only Session is used when exactly one exists, else `ValueError` (`add_tag()` lists every Session) |
| `vcon.sign(key)` accepts any header | `alg` "none" raises `AlgorithmNotPermittedError` on `sign()` and `verify()` |

Also new: `is_valid()` now reports a missing Session when dialog or events exist, a missing `extensions` entry
for an extension in use (`lawful_basis`, `wtf_transcription`, or any value outside the core vocabulary), and an
attachment with inline content but no `mediatype`.

---

# Earlier migration: Version Management Changes

> **Historical (pre-1.0).** This section describes an earlier release. Since 1.0.0, `build_new()` writes
> `"vcon": "0.5.0"`, a vCon that declares `"0.4.0"` is migrated to 0.5.0 on load (`migrate_legacy=False` turns
> that off), `is_valid()` requires a Session once there are dialogs or events, and attachments need `party` plus
> `dialog` or `session`. Where the text below says the version field is optional or that nothing is migrated,
> the 1.0.0 behavior above applies instead.

This guide helps you migrate your existing vCon code to work with the updated version management system.

## Overview

The vCon library has been updated to align with the latest vCon specification changes. The most significant change is that the **version field is now optional** and version management has been simplified. All changes are **backward compatible**, so existing code will continue to work without changes.

## Key Changes

### Version Field is Now Optional
- The `vcon` field is no longer required in vCon objects
- No automatic version assignment or migration
- Existing vCons with version fields continue to work unchanged
- New vCons can be created without version fields

### Removed Version Management
- Removed `strict_version` parameter from all methods
- No more automatic version migration
- No more version enforcement or validation

## What's New

### vCon Object Level
- `extensions`: List of extension names used
- `critical`: List of extensions that must be supported

### Party Object
- `sip`: SIP URI for VoIP communication
- `did`: Decentralized Identifier for blockchain-based identity
- `jCard`: vCard format contact information
- `timezone`: Party's timezone

### Dialog Object
- `session_id`: Session identifier for tracking conversations
- `content_hash`: Hash for content integrity verification (replaces alg/signature)

## Migration Steps

### Step 1: Update Method Calls (Required if using strict_version)

If you were using the `strict_version` parameter, you need to remove it:

```python
# Old code: no longer works (TypeError: unexpected keyword argument 'strict_version')
vcon = Vcon.load("file.json", strict_version=True)
vcon = Vcon.build_from_json(json_str, strict_version=True)
vcon = Vcon(data, strict_version=True)

# New code (remove strict_version parameter)
vcon = Vcon.load("file.json")
vcon = Vcon.build_from_json(json_str)
vcon = Vcon(data)
```

### Step 2: Version Field Handling (Optional)

The version field is now optional. You can choose to:

**Option A: Remove version fields from new vCons**
```python
# Old code
vcon = Vcon({"uuid": "123", "vcon": "0.4.0", "created_at": "2024-01-01T00:00:00Z"})

# New code (version field optional)
vcon = Vcon({"uuid": "123", "created_at": "2024-01-01T00:00:00Z"})
```

**Option B: Keep existing version fields**
```python
# This still loads; since 1.0.0 a "0.4.0" vCon is migrated to "0.5.0" on load
vcon = Vcon({"uuid": "123", "vcon": "0.4.0", "created_at": "2024-01-01T00:00:00Z"})
```

### Step 3: Add Extensions (Optional)

If you want to declare extension capabilities:

```python
# Old code
vcon = Vcon.build_new()

# New code
vcon = Vcon.build_new()
vcon.add_extension("video")
vcon.add_extension("encryption")
vcon.add_critical("encryption")
```

### Step 2: Enhance Party Information (Optional)

Add additional contact and identification methods:

```python
# Old code
party = Party(
    name="John Doe",
    tel="+1234567890"
)

# New code
party = Party(
    name="John Doe",
    tel="+1234567890",
    sip="sip:john@example.com",
    did="did:example:123456789abcdef",
    jCard={
        "fn": "John Doe",
        "tel": "+1234567890",
        "email": "john@example.com"
    },
    timezone="America/New_York"
)
```

### Step 3: Add Session Tracking (Optional)

Track conversation sessions:

```python
# Old code
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    body="Hello!"
)

# New code
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    body="Hello!",
    session_id={"local": "local-uuid", "remote": "remote-uuid"}
)
```

### Step 4: Add Content Integrity (Optional)

Replace alg/signature with content_hash:

```python
# Old code
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    body="Hello!",
    alg="sha256",
    signature="abc123"
)

# New code
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0, 1],
    body="Hello!",
    session_id={"local": "local-uuid", "remote": "remote-uuid"}
)

# Calculate and set content hash
content_hash = dialog.calculate_content_hash()
dialog.set_content_hash(content_hash)
```

## Complete Migration Example

### Before Migration

```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime

# Create vCon
vcon = Vcon.build_new()

# Add party
party = Party(name="Alice", tel="+1234567890")
vcon.add_party(party)

# Add dialog
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0],
    body="Hello!"
)
vcon.add_dialog(dialog)

# Save
vcon.save_to_file("conversation.json")
```

### After Migration

```python
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from datetime import datetime

# Create vCon with extensions
vcon = Vcon.build_new()
vcon.add_extension("video")
vcon.add_critical("encryption")

# Add party with enhanced information
party = Party(
    name="Alice",
    tel="+1234567890",
    sip="sip:alice@example.com",
    did="did:example:123456789abcdef",
    jCard={
        "fn": "Alice Johnson",
        "tel": "+1234567890",
        "email": "alice@example.com"
    },
    timezone="America/New_York"
)
vcon.add_party(party)

# 1.0.0 / vCon 0.5.0: a Session must exist once there is a dialog
from vcon.session import Session
vcon.add_session(Session(start=datetime.now(), parties=[0]))

# Add dialog with session tracking and integrity
dialog = Dialog(
    type="text",
    start=datetime.now(),
    parties=[0],
    body="Hello!",
    session_id={"local": "local-uuid", "remote": "remote-uuid"}
)

# Calculate and set content hash
content_hash = dialog.calculate_content_hash()
dialog.set_content_hash(content_hash)

vcon.add_dialog(dialog, session=0)

# Save
vcon.save_to_file("conversation.json")
```

## JSON Output Comparison

### Before Migration
```json
{
    "uuid": "...",
    "vcon": "0.4.0",
    "parties": [{
        "name": "Alice",
        "tel": "+1234567890"
    }],
    "dialog": [{
        "type": "text",
        "start": "...",
        "parties": [0],
        "body": "Hello!"
    }]
}
```

### After Migration
```json
{
    "uuid": "...",
    "vcon": "0.4.0",
    "extensions": ["video"],
    "critical": ["encryption"],
    "parties": [{
        "name": "Alice",
        "tel": "+1234567890",
        "sip": "sip:alice@example.com",
        "did": "did:example:123456789abcdef",
        "jCard": {
            "fn": "Alice Johnson",
            "tel": "+1234567890",
            "email": "alice@example.com"
        },
        "timezone": "America/New_York"
    }],
    "dialog": [{
        "type": "text",
        "start": "...",
        "parties": [0],
        "body": "Hello!",
        "session_id": {"local": "local-uuid", "remote": "remote-uuid"},
        "content_hash": "..."
    }]
}
```

## Backward Compatibility

- **Existing code continues to work**: All new fields are optional
- **No breaking changes**: Existing vCon files will load correctly
- **Gradual adoption**: You can add new fields incrementally
- **Property handling**: New fields work with all property handling modes (default, strict, meta)

## Testing Your Migration

1. **Run existing tests**: Ensure they still pass
2. **Test new functionality**: Use the example in `samples/example_new_fields.py`
3. **Validate JSON output**: Check that new fields appear correctly
4. **Verify backward compatibility**: Load old vCon files to ensure they work

## Need Help?

- Check the full documentation in `docs/source/new_required_fields.rst`
- Run the example: `python samples/example_new_fields.py`
- Review the test files for usage examples
- Open an issue if you encounter problems

## Migrating to 0.10.0 (draft-ietf-vcon-vcon-core-04)

0.10.0 retargets the library to `draft-ietf-vcon-vcon-core-04`. The
specification's body semantics did not change from prior guidance in this
library (a `"json"`-encoded body was always meant to be a JSON value, not a
string), but two behavior changes follow from aligning with the WG's
reference JSON schema:

- **Legacy string bodies are now read transparently.** If you (or an
  adapter) previously wrote a `"json"`-encoded body as a `json.dumps`
  string -- for example a `tags` attachment body written as
  `'["category:support"]'` instead of `["category:support"]` -- `get_tag()`,
  `add_tag()`, and the lawful-basis/WTF extension validators now decode
  that string automatically. `add_tag()` also normalizes a legacy string
  body back to a list, in place, the first time you call it on that vCon.
  You don't need to migrate existing data by hand.
- **New attachments get more defaults filled in.** `add_attachment()`,
  `add_lawful_basis_attachment()`, and `add_wtf_transcription_attachment()`
  now default `party`/`dialog` to `0` and `start` to the vCon's
  `created_at` when you don't supply them, because the WG JSON schema
  requires `start`, `party`, and `dialog` on every attachment. If your code
  checked for the *absence* of these keys (rather than their values), check
  the CHANGELOG's 0.10.0 entry before upgrading. (1.0.0 no longer defaults
  `dialog` to `0`: pass `dialog` or `session`; see the 0.5.0 section above.) 
