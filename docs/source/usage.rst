Usage Guide
===========

The examples on this page run in order, in one Python session.

Building a vCon
---------------

A core-05 vCon has parties, sessions and dialog. A Session groups the dialog of
one conversation, and its ``parties`` are the receivers. A Dialog's ``parties``
are only its contributors.

.. code-block:: python

    from datetime import datetime, timezone

    from vcon import Vcon, Session, Dialog
    from vcon.party import Party

    now = datetime.now(timezone.utc)

    vcon = Vcon.build_new()                      # writes "vcon": "0.5.0"
    vcon.add_party(Party(tel="+15551230001", name="Alice", role="customer"))
    vcon.add_party(Party(tel="+15551230002", name="Bob", role="agent"))

    session = vcon.add_session(Session(start=now, parties=[0, 1]))

    first = vcon.add_dialog(Dialog(
        type="text",
        start=now,
        parties=[0],
        body="Hello, I need help with my account.",
        encoding="none",
        mediatype="text/plain",
    ), session=session)

    is_valid, errors = vcon.is_valid()
    print(is_valid, errors)                      # True []

    vcon.save_to_file("conversation.vcon.json")

``add_session()``, ``add_dialog()`` and ``add_event()`` return the index of the
new object. ``add_dialog(..., session=i)`` also lists the Dialog in Session
``i``.

Dialog types
~~~~~~~~~~~~

Core-05 has three Dialog types: ``recording``, ``text`` and ``incomplete``.
Audio and video are both ``recording`` Dialogs, told apart by ``mediatype``.
``Dialog(type="audio")`` and ``Dialog(type="video")`` still work, but they
raise a ``DeprecationWarning`` and build a ``recording``.

.. code-block:: python

    vcon.add_dialog(Dialog(
        type="recording",
        start=now,
        parties=[0, 1],
        url="https://example.com/call.wav",
        mediatype="audio/x-wav",
        duration=95,
    ), session=session)

    # A call that was not answered: no content, only a disposition
    vcon.add_incomplete_dialog(start=now, disposition="no-answer", parties=[0])

    # An empty Dialog Object keeps a position so no other index moves
    vcon.add_dialog(Dialog.placeholder())        # serializes as {}

Parties
~~~~~~~

.. code-block:: python

    from vcon.civic_address import CivicAddress

    vcon.add_party(Party(
        name="Carol",
        tel="+15551230003",
        sip="sip:carol@example.com",
        did="did:example:123456789abcdef",
        timezone="America/New_York",
        civicaddress=CivicAddress(country="US", a1="CA", a3="San Francisco"),
    ))

Sessions and Events
-------------------

Events record what happened during a Session: joins, drops, holds, mutes, key
presses, call transfers and channel contributors. Each Event applies to the
Sessions in ``sessions``.

.. code-block:: python

    from vcon import Event, SessionReference

    vcon.add_event(Event(type="join", time=now, sessions=session, party=0))
    vcon.add_event(Event(type="hold", time=now, sessions=session, party=0))
    vcon.add_event(Event(type="keydown", time=now, sessions=session, party=1, button="5"))

    # A blind transfer: `sessions` is the original call, `target_session` the
    # call to the transfer target.
    target = vcon.add_session(Session(start=now, parties=[1, 2]))
    vcon.add_event(Event(type="blind-transfer", time=now, sessions=session, party=1,
                         transferee=0, transfer_target=2, target_session=target))

    # Sessions can reference each other: child, peer, precursor or breakout
    vcon.sessions[session]["sessions"] = [SessionReference(target, "peer").to_dict()]

Each Event type has a parameter table (core-05 section 4.3.1.5). ``Event(...)``
raises ``ValueError`` when a required parameter is missing or a forbidden one is
present, and ``Vcon.is_valid()`` checks the same table for Events read from
JSON.

Attachments and analysis
------------------------

An attachment needs ``party`` plus ``dialog`` or ``session``. When you give
neither ``dialog`` nor ``session``, the library uses the only Session if the
vCon has exactly one and raises ``ValueError`` otherwise.

.. code-block:: python

    vcon.add_attachment(
        purpose="invoice",
        body={"amount": 42},
        encoding="json",
        party=0,
        session=session,
    )

    vcon.add_analysis(
        type="sentiment",
        vendor="example-vendor",
        body={"sentiment": "positive"},
        encoding="json",
        dialog=first,
    )

Tags are whole-vCon metadata. ``add_tag()`` lists every Session, and adds an
empty placeholder Session when the vCon has none. The tags attachment needs a
valid ``party`` (default 0, or pass ``party=``), so add a party first; on a
vCon with no parties ``add_tag()`` warns, and from 1.1 it will raise.

.. code-block:: python

    vcon.add_tag("department", "billing")
    print(vcon.get_tag("department"))            # billing

Extensions
----------

``extensions`` must list every extension the vCon uses, and ``critical`` the
ones a reader must understand. The lawful basis and WTF helpers add their own
extension names.

.. code-block:: python

    from datetime import timedelta

    vcon.add_lawful_basis_attachment(
        lawful_basis="consent",
        expiration=(now + timedelta(days=365)).isoformat(),
        purpose_grants=[
            {"purpose": "recording", "granted": True, "granted_at": now.isoformat()},
        ],
        party_index=0,
        session_index=session,
    )
    print(vcon.check_lawful_basis_permission("recording", party_index=0))   # True
    print(vcon.get_extensions())                                           # ['lawful_basis']

Reading and validating
----------------------

.. code-block:: python

    loaded = Vcon.load("conversation.vcon.json")   # a path or an https URL
    print(loaded.vcon)                             # 0.5.0

    is_valid, errors = vcon.is_valid()             # MUST-level rules
    warnings = vcon.get_validation_warnings()      # SHOULD-level findings

    is_valid, errors = Vcon.validate_file("conversation.vcon.json")

Besides the structure and references, ``is_valid()`` checks that every
``content_hash`` has the form ``<algorithm>-<unpadded base64url digest>`` and
the body of every ``lawful_basis`` attachment. A ``url`` without a
``content_hash`` is reported by ``get_validation_warnings()`` in 1.0.x and
will be an error from 1.1. Loading keeps every value as written, including
timestamps, so an invalid ``created_at`` is reported by ``is_valid()`` rather
than raised.

Signing
-------

``sign()`` uses RS256 by default and accepts RSA, EC and Ed25519 keys (RS*,
PS*, ES* and EdDSA), as cryptography key objects or PEM. ``sign()`` and ``verify()`` reject the JWS
``alg`` value ``"none"`` with ``AlgorithmNotPermittedError``.

.. code-block:: python

    private_key, public_key = Vcon.generate_key_pair()
    vcon.sign(private_key)
    print(vcon.verify(public_key))                 # True

Loading 0.4.0 vCons
-------------------

See :doc:`version_management`.
