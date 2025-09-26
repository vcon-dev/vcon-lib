Version Management Changes
==========================

This document describes the changes to version management in the vCon library, including the removal of mandatory version enforcement and the optional nature of the version field.

Overview
--------

Starting with version 0.7.0, the vCon library has simplified version management by making the version field optional and removing automatic version enforcement. This aligns with the latest vCon specification changes and provides more flexibility for users.

Key Changes
-----------

### Version Field is Now Optional

The ``vcon`` field in vCon objects is no longer required:

- New vCon objects created with ``Vcon.build_new()`` do not include a version field by default
- Existing vCon objects with version fields continue to work unchanged
- The version field can be manually added if needed

### Removed Version Management Parameters

The following parameters have been removed from all Vcon methods:

- ``strict_version`` parameter removed from:
  - ``Vcon.__init__()``
  - ``Vcon.build_from_json()``
  - ``Vcon.build_new()``
  - ``Vcon.load()``
  - ``Vcon.load_from_file()``
  - ``Vcon.load_from_url()``

### Updated Method Signatures

All method signatures have been updated to remove version management:

.. code-block:: python

    # Old signatures (no longer supported)
    Vcon(vcon_dict=None, strict_version=True)
    Vcon.build_new(created_at=None, strict_version=True)
    Vcon.build_from_json(json_str, strict_version=True)
    Vcon.load(source, strict_version=True)

    # New signatures
    Vcon(vcon_dict=None, property_handling="default")
    Vcon.build_new(created_at=None, property_handling="default")
    Vcon.build_from_json(json_str, property_handling="default")
    Vcon.load(source, property_handling="default")

Migration Guide
---------------

### For Existing Code

If you were using the ``strict_version`` parameter, simply remove it:

.. code-block:: python

    # Old code (will cause errors)
    vcon = Vcon.load("file.json", strict_version=True)
    vcon = Vcon.build_from_json(json_str, strict_version=True)
    vcon = Vcon(data, strict_version=True)

    # New code (remove strict_version parameter)
    vcon = Vcon.load("file.json")
    vcon = Vcon.build_from_json(json_str)
    vcon = Vcon(data)

### For Version Field Handling

The version field is now optional. You can choose to:

1. **Ignore version fields** (recommended for new code):
   - Simply don't set or check version fields
   - The library will work without them

2. **Manually manage version fields** (if needed):
   - Add version fields manually when creating vCon objects
   - Check version fields in your application logic

.. code-block:: python

    # Option 1: Ignore version fields (recommended)
    vcon = Vcon.build_new()
    # vcon.vcon will be None

    # Option 2: Manually add version field if needed
    vcon = Vcon.build_new()
    vcon.vcon_dict["vcon"] = "0.3.0"
    # vcon.vcon will be "0.3.0"

### Backward Compatibility

All changes are backward compatible:

- Existing vCon objects with version fields continue to work
- The ``vcon`` property returns the version field if present, or ``None`` if not
- No breaking changes to existing functionality

Examples
--------

### Creating Versionless vCons

.. code-block:: python

    from vcon import Vcon

    # Create a new vCon without version field
    vcon = Vcon.build_new()
    print(vcon.vcon)  # None

    # Add version field manually if needed
    vcon.vcon_dict["vcon"] = "0.3.0"
    print(vcon.vcon)  # "0.3.0"

### Working with Existing vCons

.. code-block:: python

    # Load existing vCon (with or without version field)
    vcon = Vcon.load("existing.vcon.json")

    # Check if version field exists
    if vcon.vcon:
        print(f"Version: {vcon.vcon}")
    else:
        print("No version field")

### Validation Changes

The validation logic has been updated to reflect the optional nature of the version field:

.. code-block:: python

    # Validation no longer requires version field
    is_valid, errors = vcon.is_valid()
    
    # Only uuid and created_at are required fields
    # Version field is optional and not validated

Benefits
--------

The simplified version management provides several benefits:

1. **Reduced Complexity**: No need to manage version parameters
2. **More Flexibility**: Version fields are optional and can be added as needed
3. **Better Interoperability**: Works with vCon objects from different sources
4. **Simplified API**: Cleaner method signatures without version management
5. **Future-Proof**: Aligns with evolving vCon specification

Troubleshooting
--------------

### Common Issues

1. **"strict_version" parameter errors**:
   - Remove the ``strict_version`` parameter from all method calls
   - Update method signatures to use ``property_handling`` instead

2. **Version field not found**:
   - Check if the vCon object has a version field: ``vcon.vcon is not None``
   - Add version field manually if needed: ``vcon.vcon_dict["vcon"] = "0.3.0"``

3. **Validation errors**:
   - Ensure required fields (uuid, created_at) are present
   - Version field is no longer required for validation

### Getting Help

If you encounter issues with the version management changes:

1. Check the migration guide above
2. Review the changelog for detailed changes
3. Test with the updated method signatures
4. Ensure backward compatibility with existing vCon objects
