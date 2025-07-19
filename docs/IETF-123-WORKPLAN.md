# IETF-123 vCon Library Workplan

## Overview
This document outlines the changes required to update the vCon library to be compatible with the new vCon core specification (version 0.3.0).

## 1. Version Change

**Current library:** Uses version "0.0.1"  
**New specification:** Requires version "0.3.0"  
**Impact:** This is a breaking change that requires updating all vCon objects


## 2. New Required Fields

The new specification adds several new fields that are not currently supported:

### vCon Object Level:
- **extensions** (String[]) - List of extension names used
- **must_support** (String[]) - List of incompatible extensions that must be supported

### Party Object:
- **sip** - SIP URI for the party
- **did** - Decentralized Identifier
- **jCard** - vCard format contact information
- **timezone** - Party's timezone

### Dialog Object:
- **session_id** - Session identifier
- **party_history** - Array of party history objects with join/drop/hold/mute events
- **content_hash** - Hash for externally referenced files (replaces alg and signature)

## 3. Field Name Changes

- `mimetype` → `mediatype` (in dialog objects)
- `transfer-target` → `transfer_target` (for consistency with underscore naming)
- `target-dialog` → `target_dialog`

## 4. New Object Types

- **Party_History Object:** Contains party index, time, and event type
- **Redacted Object:** For referencing unredacted versions
- **Appended Object:** For referencing prior versions

## 5. Enhanced Security Features

- Support for JWS (JSON Web Signatures)
- Support for JWE (JSON Web Encryption)
- Content hashing for externally referenced files

## 6. Library Code Changes Needed

### Update Allowed Properties:
- Apply new property lists

### New Classes Needed:
- **PartyHistory** class for party history events
- **Redacted** class for redaction references
- **Appended** class for append references

### Version Handling:
- Update default version from "0.0.1" to "0.3.0"
- Add migration logic for existing vCon objects

## 7. Backward Compatibility

The specification provides migration paths:
- **Version 0.0.1 → 0.0.2:** `mimetype` → `mediatype`, `alg`/`signature` → `content_hash`
- **Version 0.0.2 → 0.3.0:** `transfer-target` → `transfer_target`, `target-dialog` → `target_dialog`

## 8. Recommendations

### Immediate Actions:
- Update the library to support version "0.3.0"
- Add the new required fields to property lists
- Implement the new object classes

### Migration Strategy:
- Add automatic version migration when loading older vCon objects
- Provide deprecation warnings for old field names
- Maintain backward compatibility for reading old formats

### Testing:
- Update all test cases to use the new version
- Add tests for the new fields and objects
- Test migration from older versions

The changes are significant but manageable, and the new specification provides better structure and extensibility for the vCon format.

---

## Implementation Plan: Changes Required for vCon Library Compatibility

Based on my analysis of the new vCon core document and the current library implementation, here's a comprehensive list of changes needed to make the library compatible with the new specification:

### 1. Version Update
- **Change:** Update version from "0.0.1" to "0.3.0"
- **Files:** `src/vcon/vcon.py`, `samples/example.vcon.json`
- **Test:** Verify new vCons are created with version "0.3.0"

### 2. Add New Required vCon Fields
- **Change:** Add extensions field (String[])
- **Files:** `src/vcon/vcon.py`
- **Test:** Verify extensions array is included in vCon objects

- **Change:** Add must_support field (String[])
- **Files:** `src/vcon/vcon.py`
- **Test:** Verify must_support array is included when extensions are used

### 3. Update Party Object Fields
- **Change:** Add did field (String) for Decentralized Identifiers
- **Files:** `src/vcon/party.py`
- **Test:** Verify DID can be set and serialized correctly

- **Change:** Add jCard field (Object) for contact information
- **Files:** `src/vcon/party.py`
- **Test:** Verify jCard object can be included

- **Change:** Add timezone field (String)
- **Files:** `src/vcon/party.py`
- **Test:** Verify timezone can be set and serialized

### 4. Update Dialog Object Fields
- **Change:** Rename mimetype to mediatype (already done in library)
- **Files:** `src/vcon/dialog.py`
- **Test:** Verify mediatype is used consistently

- **Change:** Add session_id field (String)
- **Files:** `src/vcon/dialog.py`
- **Test:** Verify session_id can be set and serialized

- **Change:** Add application field (String)
- **Files:** `src/vcon/dialog.py`
- **Test:** Verify application field can be set

- **Change:** Add message_id field (String)
- **Files:** `src/vcon/dialog.py`
- **Test:** Verify message_id can be set for email/text dialogs

### 5. Update Party History Object
- **Change:** Add time field (Date) to PartyHistory
- **Files:** `src/vcon/party.py`
- **Test:** Verify time field is properly serialized as ISO 8601

### 6. Update Transfer Dialog Fields
- **Change:** Rename transfer-target to transfer_target
- **Files:** `src/vcon/dialog.py`
- **Test:** Verify transfer_target is used consistently

- **Change:** Rename target-dialog to target_dialog
- **Files:** `src/vcon/dialog.py`
- **Test:** Verify target_dialog is used consistently

### 7. Update Allowed Properties Lists
- **Change:** Update `_ALLOWED_VCON_PROPERTIES` to include new fields
- **Files:** `src/vcon/vcon.py`
- **Test:** Verify new properties are allowed

- **Change:** Update `_ALLOWED_PARTY_PROPERTIES` to include new fields
- **Files:** `src/vcon/vcon.py`
- **Test:** Verify new party properties are allowed

- **Change:** Update `_ALLOWED_DIALOG_PROPERTIES` to include new fields
- **Files:** `src/vcon/vcon.py`
- **Test:** Verify new dialog properties are allowed

### 8. Update Civic Address Support
- **Change:** Ensure all civic address fields are supported
- **Files:** `src/vcon/civic_address.py`
- **Test:** Verify all GEOPRIV fields are supported

### 9. Update Media Type Validation
- **Change:** Update supported media types to match specification
- **Files:** `src/vcon/dialog.py`
- **Test:** Verify all specified media types are accepted

### 10. Update Disposition Values
- **Change:** Add new disposition values for incomplete dialogs
- **Files:** `src/vcon/dialog.py`
- **Test:** Verify all specified disposition values are accepted

### 11. Update Party History Events
- **Change:** Add new event types (hold, unhold, mute, unmute)
- **Files:** `src/vcon/party.py`
- **Test:** Verify all event types are supported

### 12. Update Sample Files
- **Change:** Update sample vCon files to use version "0.3.0"
- **Files:** `samples/example.vcon.json`
- **Test:** Verify samples are valid according to new specification

### 13. Add Validation for New Requirements
- **Change:** Add validation for required fields in new version
- **Files:** `src/vcon/vcon.py`
- **Test:** Verify validation catches missing required fields

### 14. Update Documentation
- **Change:** Update docstrings and comments to reflect new specification
- **Files:** All Python files
- **Test:** Verify documentation is accurate

### 15. Add Migration Support
- **Change:** Add methods to migrate from 0.0.1 to 0.3.0
- **Files:** `src/vcon/vcon.py`
- **Test:** Verify old vCons can be migrated to new format

---

## Summary

Each change is small, manageable, and testable. The changes should be implemented incrementally with tests for each modification to ensure backward compatibility and proper functionality.
