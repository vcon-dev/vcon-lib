Versions and Migration
======================

Which spec each release implements
----------------------------------

=============  ======================================  =================
``vcon``       Specification                           Writes ``vcon``
=============  ======================================  =================
1.0            ``draft-ietf-vcon-vcon-core-05``        ``"0.5.0"``
0.10           ``draft-ietf-vcon-vcon-core-04``        ``"0.4.0"``
=============  ======================================  =================

``Vcon.build_new()`` writes ``"vcon": "0.5.0"``. The ``vcon`` parameter is
optional on read; when present, ``is_valid()`` requires it to be ``"0.5.0"``.

Loading a 0.4.0 vCon
--------------------

Readers accept 0.4.0 and 0.5.0. A vCon that declares ``"vcon": "0.4.0"`` is
migrated to 0.5.0 on load, following core-05 Appendix A.1. Array indices are
preserved, and ``migration_report`` lists every value the migration inferred,
every fallback it used for a required field, and every item it could not
resolve.

.. code-block:: python

    import json
    from vcon import Vcon

    old = {
        "vcon": "0.4.0",
        "uuid": "01928e10-193e-8231-b9a2-279e0d16bc46",
        "created_at": "2024-01-01T00:00:00Z",
        "parties": [{"tel": "+15551230001"}, {"tel": "+15551230002"}],
        "dialog": [{
            "type": "recording",
            "start": "2024-01-01T00:00:00Z",
            "parties": [0, 1],
            "url": "https://example.com/call.wav",
            "mediatype": "audio/x-wav",
            "duration": 95,
        }],
    }
    with open("old.vcon.json", "w") as f:
        json.dump(old, f)

    vcon = Vcon.load("old.vcon.json")
    print(vcon.vcon)                          # 0.5.0
    print(vcon.migration_report.summary())    # 2 inferred, 0 fallback, 0 unresolved
    print(len(vcon.sessions))                 # 1

The same behavior applies to ``Vcon(dict)``, ``build_from_json()``,
``load_from_file()`` and ``load_from_url()``. Two parameters control it:

* ``migrate_legacy=False`` keeps the raw 0.4.0 dict. Property handling is not
  applied to it, so legacy parameters survive.
* ``strict_migration=True`` raises ``MigrationError`` when a required field has
  no source, instead of using a fallback.

A signed 0.4.0 vCon is kept signed on load. Verify it, then migrate it
explicitly; the report sets ``resign_required``, and the library never
re-signs.

Migrating explicitly
--------------------

.. code-block:: python

    from vcon import migrate_0_4_0_to_0_5_0

    new_dict, report = migrate_0_4_0_to_0_5_0(old, strict=False)
    print(new_dict["vcon"])                   # 0.5.0
    for item in report.inferred:
        print(item)

    # Or get a Vcon back
    vcon = Vcon.migrate_0_4_0_to_0_5_0(old)

What changes in a migrated vCon
-------------------------------

* Every Dialog is listed in a Session. Recording-set membership becomes Session
  membership, and nested recording sets become ``child`` Session references.
* ``transfer`` Dialogs and ``party_history`` entries become Events.
* Dialog ``parties`` keep only the contributors; the receivers move to the
  Session.
* ``redacted`` and ``amended`` become ``redacted_from`` and ``amended_from``.
* Attachments without a scope get the only Session when exactly one exists.

The `changelog <https://github.com/vcon-dev/vcon-lib/blob/main/CHANGELOG.md>`_
has the full list, and the `migration guide
<https://github.com/vcon-dev/vcon-lib/blob/main/MIGRATION_GUIDE.md>`_ shows the
code changes when upgrading an application from 0.10 to 1.0.
