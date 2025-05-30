- Updated the `__init__` methods in `Dialog` and `Party` classes to accept additional keyword arguments (`**kwargs`) for flexibility.
- Simplified attribute assignment by using `locals()` to set non-None values.
- Enhanced the `to_dict` method in `Dialog` to return all non-None attributes.
- Improved readability and consistency in the code structure.
- Added docstrings for better documentation of methods and parameters.

## Changes since 0.5.0

- The `__init__` methods in both `Dialog` and `Party` classes now accept additional keyword arguments (`**kwargs`), allowing for more flexible instantiation and easier extension.
- Attribute assignment in these classes is now streamlined: all non-None values from the constructor are set as attributes using `locals()`, reducing boilerplate and improving maintainability.
- The `to_dict` methods in both classes have been enhanced to return all non-None attributes, making serialization more robust and predictable.
- Improved overall code readability and consistency, especially in the main data model classes.
- Added or improved docstrings for better documentation of methods and parameters, making the code easier to understand and use.
- No major new features or breaking changes to the core logic or API; the focus is on flexibility, maintainability, and documentation improvements.