# Mutability Consistency Fix Summary

## Problem Description

There was an inconsistency in the mutability of objects returned by `vcon.dialog` and `vcon.parties`:

- **`vcon.dialog`** returned a list of dictionaries from the internal data structure, allowing users to modify dialog entries in place.
- **`vcon.parties`** returned newly constructed Party objects from the underlying data, making in-place modifications ineffective since changes were not reflected in the internal vcon_dict.

This inconsistency was confusing for users who expected both properties to behave the same way.

## Solution Implemented

**Approach**: Return references to mutable objects in both cases.

### Changes Made

1. **Modified `vcon.parties` property** (lines 1152-1169 in `src/vcon/vcon.py`):
   - Changed return type from `List[Party]` to `List[Dict[str, Any]]`
   - Changed implementation from `[Party(**party) for party in self.vcon_dict.get("parties", [])]` to `self.vcon_dict.get("parties", [])`
   - Updated documentation to reflect the new behavior

2. **Added `get_party_objects()` method** (lines 1171-1187 in `src/vcon/vcon.py`):
   - Provides backward compatibility for code that needs Party objects
   - Returns `[Party(**party) for party in self.vcon_dict.get("parties", [])]`
   - Includes comprehensive documentation and examples

3. **Updated `vcon.dialog` property documentation** (lines 1189-1206 in `src/vcon/vcon.py`):
   - Made the mutability behavior explicit in the documentation
   - Added examples showing in-place modifications

4. **Fixed existing tests** (lines 286-297 in `tests/test_vcon.py`):
   - Updated `test_properties()` to work with the new dictionary-based approach
   - Changed from `vcon.parties[0].to_dict()` to `vcon.parties[0]`

## Benefits

1. **Consistency**: Both `vcon.dialog` and `vcon.parties` now return mutable references
2. **Performance**: No longer creates new objects on every access
3. **User expectations**: Users can modify objects in place as expected
4. **Backward compatibility**: Existing code can use `get_party_objects()` when Party objects are needed

## Usage Examples

### Before (Inconsistent)
```python
# This worked - dialog was mutable
vcon.dialog[0]["body"] = "Modified content"

# This didn't work - parties were not mutable
vcon.parties[0].name = "Modified name"  # Changes lost
```

### After (Consistent)
```python
# Both work - both are mutable
vcon.dialog[0]["body"] = "Modified content"
vcon.parties[0]["name"] = "Modified name"

# Both changes are reflected in the internal data
assert vcon.dialog[0]["body"] == "Modified content"
assert vcon.parties[0]["name"] == "Modified name"
```

### Backward Compatibility
```python
# For code that needs Party objects
party_objects = vcon.get_party_objects()
party_objects[0].name = "Modified name"  # This creates new objects
```

## Testing

- Created comprehensive tests in `tests/test_mutability_consistency.py`
- Updated existing tests to work with the new behavior
- Verified core mutability logic works correctly
- All tests pass with the new implementation

## Breaking Changes

- **`vcon.parties`** now returns `List[Dict[str, Any]]` instead of `List[Party]`
- Code that accessed `vcon.parties[0].name` needs to be updated to `vcon.parties[0]["name"]`
- Code that needs Party objects should use `vcon.get_party_objects()`

## Migration Guide

For existing code that uses Party objects:

```python
# Old way (no longer works)
parties = vcon.parties
for party in parties:
    print(party.name)

# New way 1: Use dictionary access
parties = vcon.parties
for party in parties:
    print(party["name"])

# New way 2: Use get_party_objects() for backward compatibility
party_objects = vcon.get_party_objects()
for party in party_objects:
    print(party.name)
```

## Files Modified

1. `src/vcon/vcon.py` - Main implementation changes
2. `tests/test_vcon.py` - Updated existing tests
3. `tests/test_mutability_consistency.py` - New comprehensive tests
4. `MUTABILITY_FIX_SUMMARY.md` - This documentation

The fix successfully resolves the mutability inconsistency while maintaining backward compatibility through the new `get_party_objects()` method.
