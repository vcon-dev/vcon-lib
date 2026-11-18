Installation
============

``vcon`` requires Python 3.12 or later.

Using pip
---------

.. code-block:: bash

    pip install vcon

The image and PDF helpers need Pillow and pypdf, which the ``image`` extra
installs:

.. code-block:: bash

    pip install "vcon[image]"

Some video features call the ``ffmpeg`` binary, which must be installed
separately and on your ``PATH``.

From source
-----------

The project uses Poetry:

.. code-block:: bash

    git clone https://github.com/vcon-dev/vcon-lib.git
    cd vcon-lib
    poetry install
    poetry run pytest

To build these docs locally:

.. code-block:: bash

    poetry install --with dev
    cd docs
    poetry run make html

The output is in ``docs/build/html``.

Dependencies
------------

The runtime dependencies are listed in ``pyproject.toml`` and installed
automatically: authlib, uuid6, requests, pydash, python-dateutil, mutagen,
and ffmpeg. Pillow and pypdf come with the ``image`` extra.
