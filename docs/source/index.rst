vcon
====

``vcon`` is a Python library for building, reading, validating, signing and
migrating vCons. A vCon (Virtual Conversation) is a JSON container for one
conversation: its parties, sessions, dialog, events, attachments and analysis.

This release (|release|) implements `draft-ietf-vcon-vcon-core-05
<https://datatracker.ietf.org/doc/draft-ietf-vcon-vcon-core/>`_. It writes vCon
syntax ``"0.5.0"`` and reads both ``"0.4.0"`` and ``"0.5.0"``; a 0.4.0 vCon is
migrated to 0.5.0 when it is loaded.

.. code-block:: bash

   pip install vcon

1.0 is a breaking release. If you are upgrading from 0.10 or earlier, read
:doc:`version_management` and the `migration guide
<https://github.com/vcon-dev/vcon-lib/blob/main/MIGRATION_GUIDE.md>`_ first.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   version_management
   api/modules

Other documentation
-------------------

* `conserver.io: vCon Library <https://www.conserver.io/vcon-library>`_: quickstart and API reference
* `Changelog <https://github.com/vcon-dev/vcon-lib/blob/main/CHANGELOG.md>`_
* `Source on GitHub <https://github.com/vcon-dev/vcon-lib>`_
* `vcon on PyPI <https://pypi.org/project/vcon/>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
